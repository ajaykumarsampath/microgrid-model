from typing import List, Callable, Any

import cvxpy as cp
import numpy as np

from common.timeseries.domain import Bounds
from control.optimisation_engine.domain import (
    IOptimisationVariable,
    IOptimisationIndexVariable,
    VariableType,
    OptimisationExpression,
    ConstraintType,
)


class CvxVariable(IOptimisationVariable):
    def __init__(
        self,
        name: str,
        value: float,
        bounds: Bounds,
        variable_type: VariableType = VariableType.Continuous,
    ):
        if variable_type == variable_type.Binary:
            self._value = cp.Variable((1,), name=name, value=[value], boolean=True)
        else:
            self._value = cp.Variable((1,), name=name, value=[value])

        self._min_constraint = bounds.min <= self._value
        self._max_constraint = self._value <= bounds.max

        self.variable_type = variable_type
        self.name = name

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, variable: Any):
        self._value = variable

    @property
    def bounds(self):
        return Bounds(
            min=self._min_constraint.args[0].value,
            max=self._max_constraint.args[1].value,
        )

    @bounds.setter
    def bounds(self, bounds: Bounds):
        self._min_constraint = bounds.min <= self._value
        self._max_constraint = self._value <= bounds.max

    @property
    def bound_constraints(self):
        return [self._min_constraint, self._max_constraint]

    def evaluate(self):
        return self._value.value


class CvxParameter(IOptimisationVariable):
    def __init__(self, name: str, value: float):
        self._value = cp.Parameter((1,), name=name, value=value)
        self._init_value = value
        self.name = name

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, parameter: Any):
        self._value = parameter

    def evaluate(self):
        return self._value.value


class CvxConstraint(IOptimisationVariable):
    def __init__(self, name: str, constraint: ConstraintType):
        self._value = constraint.value.value
        self.name = name

    @property
    def value(self):
        return self._value

    def evaluate(self):
        # status = cp.constraints.constraint.Constraint(args=[self._value]).args[0].value()
        status = self._value.value()
        return status


class UndefinedObjective(Exception):
    pass


class CvxObjective(IOptimisationVariable):
    def __init__(self, objective: OptimisationExpression):
        if isinstance(objective.value, (int, float)) or objective.value is None:
            self._value = objective.value
        elif isinstance(objective.value, cp.Expression):
            if objective.value.is_dcp():
                self._value = objective.value
            else:
                raise UndefinedObjective(
                    "Only linear objective is allowed as optimisation expression"
                    "Use update functionality to add other forms of"
                )
        else:
            raise UndefinedObjective(
                "Optimisation expressions should either be a cvxpy expression or int, float or none"
            )

    @property
    def value(self):
        return self._value

    def evaluate(self):
        return cp.Minimize(self._value)

    @staticmethod
    def cvx_callable_objective(callable: Callable, *args) -> OptimisationExpression:
        return OptimisationExpression(callable(*args))

    def update_objective(self, objective_expr: OptimisationExpression):
        try:
            _value = self._value + objective_expr.value
        except Exception as e:
            raise Exception(f"Cannot update the objective {e}")

        if _value.is_dcp():
            self._value = _value
            print(self._value)
        else:
            UndefinedObjective("Objective can be linear or quadratic now")


class CvxIndexParameter(IOptimisationIndexVariable):
    def __init__(self, name: str, index: List[int], value: List[float]):
        self._value = cp.Parameter((len(index),), name=name, value=np.array(value))
        self._index = index
        self.name = name

    @property
    def value(self):
        return self._value

    def evaluate(self):
        return self._value.value

    def _at_index(self, index: int):
        try:
            id = self._index.index(index)
            parameter = CvxParameter(f"{self.name}_{id}", self.value[id])
            parameter.value = self.value[id]
            return parameter
        except IndexError as e:
            raise IndexError(f"cvx index parameter {e}")


class CvxIndexVariable(IOptimisationIndexVariable):
    def __init__(
        self,
        name: str,
        index: List[int],
        value: List[float],
        bounds: List[Bounds],
        variable_type: VariableType = VariableType.Continuous,
    ):

        if variable_type == VariableType.Continuous:
            self._value = cp.Variable((len(index),), name=name, value=np.array(value))
        else:
            self._value = cp.Variable((len(index),), name=name, value=np.array(value), boolean=True)

        self._min_bounds = [b.min <= self._value[i] for i, b in enumerate(bounds)]
        self._max_bounds = [self._value[i] <= b.max for i, b in enumerate(bounds)]
        self._index = index
        self.variable_type = variable_type
        self.name = name

        self._variable = []
        for id in self._index:
            id_bound_min = self._get_expression_value(self.name, self._min_bounds[id])
            id_bound_max = self._get_expression_value(self.name, self._max_bounds[id])

            variable = CvxVariable(
                f"{self.name}_{id}",
                self.value[id].value,
                Bounds(id_bound_min, id_bound_max),
                self.variable_type,
            )
            variable.value = self.value[id]
            self._variable.append(variable)

    @property
    def value(self):
        return self._value

    def _get_expression_value(self, name, value):
        return [i.value for i in value.args if i.name()[: len(name)] != name][0]

    @property
    def bounds(self) -> List[Bounds]:
        bound_min = [self._get_expression_value(self.name, b) for b in self._min_bounds]
        bound_max = [self._get_expression_value(self.name, b) for b in self._max_bounds]

        return [Bounds(mi_, ma_) for mi_, ma_ in zip(bound_min, bound_max)]

    @property
    def bound_constraints(self):
        constraints_ = self._min_bounds
        constraints_.extend(self._max_bounds)
        return constraints_

    def evaluate(self):
        return self._value.value

    def _at_index(self, index: int):
        try:
            id = self._index.index(index)
            return self._variable[id]
        except IndexError as e:
            raise IndexError(f"cvx index parameter {e}")


class CvxIndexConstraint(IOptimisationIndexVariable):
    def __init__(self, name: str, constraint: List[ConstraintType]):
        self._value = [c.value.value for c in constraint]
        self.name = name
        self._constraint = []
        for i, c_type in enumerate(constraint):
            self._constraint.append(CvxConstraint(f"{name}_{i}", c_type))

    @property
    def value(self):
        return self._value

    @property
    def constraint(self):
        return self._constraint

    def evaluate(self):
        return [v.value() for v in self._value]

    def _at_index(self, index: int):
        try:
            return self._constraint[index]
        except IndexError as e:
            raise IndexError(f"cvx index parameter {e}")


class CvxIndexObjective(IOptimisationVariable):
    def __init__(self, objective: OptimisationExpression):
        if objective.value.is_dcp():
            self._value = objective.value
        else:
            raise UndefinedObjective(
                "Only linear objective is allowed as optimisation expression"
                "Use update functionality to add other forms of"
            )

    @property
    def value(self):
        return self._value

    def evaluate(self):
        return cp.Minimize(self._value)

    def cvx_callable_objective(self, callable: Callable, *args) -> OptimisationExpression:
        return OptimisationExpression(callable(*args))

    def add_objective(self, objective_expr: OptimisationExpression):
        try:
            _value = self._value + objective_expr.value
        except Exception as e:
            raise Exception(f"Cannot update the objective {e}")

        if _value.is_dcp():
            self._value = _value
        else:
            UndefinedObjective("Objective can be linear or quadratic now")


def generate_cvx_bound_constraint(variable: CvxVariable.value, bounds: Bounds):
    constraint_ = [bounds.min <= variable.value]
    constraint_.append(variable.value <= bounds.max)
    return constraint_


def generate_cvx_index_bound_constraint(variable, bounds):
    constraint_ = [bounds.min.get_value(t) <= variable[i].value for i, t in enumerate(bounds.timestamps)]
    constraint_.extend([variable[i].value <= bounds.max.get_value(t) for i, t in enumerate(bounds.timestamps)])
    return constraint_


if __name__ == "__main__":

    x = cp.Variable((1,), value=[0])
    x_1 = cp.Variable((1,), value=[0])
    p = cp.Parameter((1,), value=[4])

    # c = cp.power(x[0] - p[0])
    # c = (x[0] - p[0])@2
    x_temp = cp.Variable((2,), value=[0, 0])

    # c = cp.quad_form(x_temp, np.mat([[1, 0], [0, 1]]))
    # c = cp.quad_form(x - p, np.mat([1]))
    c = x * 2

    ob = cp.Minimize(c)
    print(ob)
    c_1 = [x >= 0, x >= 3, x_1 >= 0]
    c_1.extend([x_temp[0] == x, x_temp[1] == x_1])

    # print(c_1[1].value)

    prob = cp.Problem(ob, c_1)
    prob.solve()
    print(prob.status)
    print(x.value)
