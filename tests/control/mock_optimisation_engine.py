from typing import List, Union, Callable, TypeVar, Optional, Any

from common.timeseries.domain import Timestamps, Bounds, TimeseriesModel, BoundTimeseries
from control.optimisation_engine.domain import IOptimisationIndexVariable, IOptimisationVariable, \
    IBaseVariable, OptimisationExpression, ConstraintType, ITimeIndexBaseModel
from control.optimisation_engine.interface import IOptimisationEngine
import cvxpy as cp


class MockOptimisationVariable(IOptimisationVariable):
    def __init__(self, value: Union[cp.Variable, cp.Expression]):
        self._value = value

    @property
    def value(self):
        return self._value

    def evaluate(self):
        return self._value.value


class MockOptimisationIndexVariable(IOptimisationIndexVariable):
    def __init__(self, value: Union[cp.Variable, cp.Parameter]):
        self._value = value
        self._variable = [MockOptimisationVariable(v) for v in self._value]

    def _at_index(self, index: int):
        return self._variable[index]

    @property
    def value(self):
        return self._value

    def __getitem__(self, index: int):
        return self._at_index(index)

    def evaluate(self):
        return self._value.value


class MockBaseVariable(IBaseVariable):
    def __init__(self, name: str,
                 value: Union[float, MockOptimisationVariable, OptimisationExpression]):
        self._value = value
        self._name = name

    @property
    def name(self):
        return self._name

    @property
    def value(self):
        return self._value


class MockIndexVariable(ITimeIndexBaseModel):
    def __init__(self, name: str, timestamps: Timestamps, value: Union[List[float], cp.Variable]):
        self._value = value
        self._name = name
        self._timestamps = timestamps
        self._variable = [
            MockBaseVariable(f'{name}_{id}', MockOptimisationVariable(value[id]))
            for id, t in enumerate(timestamps)
        ]

    @property
    def timestamps(self) -> Timestamps:
        return self._timestamps

    @property
    def value(self):
        return self._variable

    def evaluate(self):
        return self._value.value

    @property
    def name(self):
        return self._name

    def _at_index(self, index: int):
        return self._variable[index]

    @property
    def variable(self):
        return self._variable


MockVar = TypeVar(
    'MockVar',
    MockOptimisationVariable,
    MockOptimisationIndexVariable
)


class MockOptimisationEngine(IOptimisationEngine):
    def __init__(self):
        self._variable: List[MockVar] = []
        self._constraints: Any = []
        self._objective: Optional[cp.Expression] = None
        self._model: Optional[cp.Problem] = None

    @property
    def variable(self) -> List[MockVar]:
        return self._variable

    @property
    def constraints(self):
        return self._constraints

    @property
    def model(self) -> cp.Problem:
        return self._model

    def generate_model(self):
        variables = []
        for v in self._variable:
            variables.append(v.value)

        if self._objective is not None:
            self._model = cp.Problem(cp.Minimize(self._objective), self.constraints)

    @property
    def timestamps(self) -> Timestamps:
        raise NotImplementedError

    def solve(self):
        try:
            self._model.solve()
        except Exception:
            raise NotImplementedError('Model is not generated to solve: use generate_model')

    def add_parameter(self, name: str, value: float) -> MockOptimisationVariable:
        pass

    def add_variable(self, name: str, bounds: Bounds, initial_value: float) -> MockOptimisationVariable:
        pass

    def add_binary_variable(self, name: str, initial_value: float) -> MockOptimisationVariable:
        pass

    def add_constraint(self, name: str, constraint: ConstraintType) -> MockOptimisationVariable:
        cvx_constraint = constraint.value.value
        self._constraints.append(cvx_constraint)
        constraint = MockOptimisationVariable(cvx_constraint)  # type: ignore
        return constraint

    def add_objective(self, name: str, objective: OptimisationExpression):
        if self._objective is None:
            if isinstance(objective.value, cp.Expression):
                self._objective = objective.value

    def update_objective(self, variable: IOptimisationVariable, obj_callable: Callable):
        if self._objective is not None:
            if isinstance(variable.value, cp.Expression):
                self._objective = self._objective + obj_callable(variable.value)

    def add_timeindex_parameter(self, name: str, value: TimeseriesModel):
        var = MockOptimisationIndexVariable(cp.Parameter(
            (len(value.timestamps), ), name=name, value=[value.get_value(t) for t in value.timestamps]))
        self._variable.append(var)
        return var

    def add_timeindex_variable(self, name: str, bound: BoundTimeseries, initial_value: TimeseriesModel):

        cvx_var = cp.Variable(shape=(len(bound.timestamps), ), name=name,
                              value=initial_value.values)
        cvx_min_bound = [bound.min.get_value(t) <= cvx_var[i] for i, t in enumerate(bound.timestamps)]
        cvx_max_bound = [cvx_var[i] <= bound.max.get_value(t) for i, t in enumerate(bound.timestamps)]

        var = MockOptimisationIndexVariable(cvx_var)
        self._variable.append(var)
        self._constraints.extend(cvx_min_bound)
        self._constraints.extend(cvx_max_bound)
        return var

    def add_timeindex_binary_variable(self, name: str, initial_value: TimeseriesModel):
        cvx_var = cp.Variable(shape=(len(initial_value.timestamps),), name=name,
                              value=initial_value.values, integer=True)

        cvx_min_bound = [0 <= cvx_var[i] for i, t in enumerate(initial_value.timestamps)]
        cvx_max_bound = [cvx_var[i] <= 1 for i, t in enumerate(initial_value.timestamps)]

        var = MockOptimisationIndexVariable(cvx_var)
        self._variable.append(var)
        self._constraints.extend(cvx_min_bound)
        self._constraints.extend(cvx_max_bound)
        return var

    def add_index_constraint(self, name: str, constraint: List[ConstraintType]):
        cvx_constraint = [c.value.value for c in constraint]
        self._constraints.extend(cvx_constraint)
        constraint = MockOptimisationIndexVariable(cvx_constraint)  # type: ignore
        return constraint
