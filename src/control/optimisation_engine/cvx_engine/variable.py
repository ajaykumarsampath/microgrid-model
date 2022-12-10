from typing import List, Callable, Any

import cvxpy as cp
import numpy as np

from common.timeseries.domain import Bounds
from control.optimisation_engine.domain import IOptimisationVariable, IOptimisationIndexVariable, \
    VariableType, OptimisationExpression


class CvxVariable(IOptimisationVariable):
    def __init__(self, name: str, value: float, variable_type: VariableType = VariableType.Continuous):
        if variable_type == variable_type.Binary:
            self._value = cp.Variable((1,), name=name, value=[value], boolean=True)
        else:
            self._value = cp.Variable((1,), name=name, value=[value])

        self.variable_type = variable_type

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, variable: Any):
        self._value = variable

    def evaluate(self):
        return self._value.value


class CvxParameter(IOptimisationVariable):
    def __init__(self, name: str, value: float):
        self._value = cp.Parameter((1,), name=name)
        self._init_value = value

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, parameter: Any):
        self._value = parameter

    def evaluate(self):
        return self._value.value


class CvxConstraint(IOptimisationVariable):
    def __init__(self, constraint: OptimisationExpression):
        self._value = constraint.value

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
        if objective.value.is_dcp():
            self._value = objective.value
        else:
            raise UndefinedObjective('Only linear objective is allowed as optimisation expression'
                                     'Use update functionality to add other forms of')

    @property
    def value(self):
        return self._value

    def evaluate(self):
        return cp.Minimize(self._value)

    @staticmethod
    def cvx_callable_objective(callable: Callable, *args) -> OptimisationExpression:
        return OptimisationExpression(callable(*args))

    def add_objective(self, objective_expr: OptimisationExpression):
        try:
            _value = self._value + objective_expr.value
        except Exception as e:
            raise Exception(f'Cannot update the objective {e}')

        if _value.is_dcp():
            self._value = _value
        else:
            UndefinedObjective('Objective can be linear or quadratic now')


class CvxIndexParameter(IOptimisationIndexVariable):
    def __init__(self, name: str, index: List[int], value: List[float]):
        self._value = cp.Parameter(
            (len(index), ), name=name, value=np.array(value)
        )
        self._index = index
        self._name = name

    @property
    def value(self):
        return self._value

    @property
    def name(self):
        return self._name

    def evaluate(self):
        return self._value.value

    def _at_index(self, index: int):
        try:
            id = self._index.index(index)
            parameter = CvxParameter(f'{self._name}_{id}', self.value[id])
            parameter.value = self.value[id]
            return parameter
        except IndexError as e:
            raise IndexError(f'cvx index parameter {e}')


class CvxIndexVariable(IOptimisationIndexVariable):
    def __init__(self, name: str, index: List[int], value: List[float],
                 variable_type: VariableType = VariableType.Continuous):

        if variable_type == VariableType.Continuous:
            self._value = cp.Variable(
                (len(index), ), name=name, value=np.array(value)
            )
        else:
            self._value = cp.Variable(
                (len(index),), name=name, value=np.array(value),
                boolean=True
            )

        self._index = index
        self.variable_type = variable_type
        self._name = name

    @property
    def value(self):
        return self._value

    def evaluate(self):
        return self._value.value

    @property
    def name(self):
        return self._name

    def _at_index(self, index: int):
        try:
            id = self._index.index(index)
            variable = CvxVariable(f'{self._name}_{id}', self.value[id].value, self.variable_type)
            variable.value = self.value[id]
            return variable
            # return self._value[id]
        except IndexError as e:
            raise IndexError(f'cvx index parameter {e}')


class CvxIndexConstraint(IOptimisationIndexVariable):
    def __init__(self, name: str, constraint: List[OptimisationExpression]):
        self._value = [c.value for c in constraint]
        self._name = name

    @property
    def name(self):
        return self._name

    @property
    def value(self):
        return self._value

    def evaluate(self):
        return [v.value() for v in self._value]

    def _at_index(self, index: int):
        try:
            return self._value[index]
        except IndexError as e:
            raise IndexError(f'cvx index parameter {e}')


class CvxIndexObjective(IOptimisationVariable):
    def __init__(self, objective: OptimisationExpression):
        if objective.value.is_dcp():
            self._value = objective.value
        else:
            raise UndefinedObjective('Only linear objective is allowed as optimisation expression'
                                     'Use update functionality to add other forms of')

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
            raise Exception(f'Cannot update the objective {e}')

        if _value.is_dcp():
            self._value = _value
        else:
            UndefinedObjective('Objective can be linear or quadratic now')


def generate_cvx_bound_constraint(variable: CvxVariable.value, bounds: Bounds):
    constraint_ = [bounds.min <= variable.value]
    constraint_.append(variable.value <= bounds.max)
    return constraint_


def generate_cvx_index_bound_constraint(variable, bounds):
    constraint_ = [
        bounds.min.get_value(t) <= variable[i].value
        for i, t in enumerate(bounds.timestamps)
    ]
    constraint_.extend(
        [variable[i].value <= bounds.max.get_value(t) for i, t in enumerate(bounds.timestamps)]
    )
    return constraint_


if __name__ == '__main__':

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
