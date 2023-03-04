from typing import List, Union, Optional

from control.optimisation_engine.domain import (
    IExpression,
    IBaseVariable,
    ConstraintType,
    ObjectiveType,
    ITimeIndexBaseModel,
    IOptimisationVariable,
    IOptimisationIndexVariable,
    UnknownTimestampError,
)
from common.timeseries.domain import (
    Timestamps,
    Timestamp,
    BoundTimeseries,
    Bounds,
    TimeseriesModel,
)


class Parameter(IBaseVariable):
    def __init__(self, name: str, value: Union[float, int]):
        self._value = value
        self._name = name
        self._opt_parameter: Optional[IOptimisationVariable] = None

    @property
    def name(self) -> str:
        return self._name

    @property
    def value(self) -> IOptimisationVariable:
        if self._opt_parameter is None:
            raise NotImplementedError(f"parameter {self._name} is not created")
        else:
            return self._opt_parameter

    @value.setter
    def value(self, var: IOptimisationVariable):
        self._opt_parameter = var

    def evaluate(self):
        return self.value.evaluate()


class Variable(IBaseVariable):
    def __init__(self, name: str, bounds: Bounds, initial_value: float):
        self._name = name
        self._bounds = bounds
        self._initial_value = initial_value
        self._opt_variable: Optional[IOptimisationVariable] = None

    @property
    def name(self):
        return self._name

    @property
    def bounds(self) -> Bounds:
        return self._bounds

    @property
    def initial_value(self) -> float:
        return self._initial_value

    @property
    def value(self) -> IOptimisationVariable:
        if self._opt_variable is None:
            raise NotImplementedError(f"Variable {self._name} is not created")
        else:
            return self._opt_variable

    @value.setter
    def value(self, var: IOptimisationVariable):
        self._opt_variable = var

    def evaluate(self) -> Union[float, int]:
        return self.value.evaluate()


class Constraint:
    def __init__(self, name: str, constraint: ConstraintType):
        self._name = name
        self._constraint = constraint
        self._opt_constraint: Optional[IOptimisationVariable] = None

    @property
    def name(self):
        return self._name

    @property
    def constraint_expression(self) -> ConstraintType:
        return self._constraint

    @property
    def value(self) -> IOptimisationVariable:
        if self._opt_constraint is None:
            raise NotImplementedError(f"Constraint {self.name} is not created")
        else:
            return self._opt_constraint

    @value.setter
    def value(self, var: IOptimisationVariable):
        self._opt_constraint = var

    def evaluate(self) -> bool:
        return self.value.evaluate()


class Objective(IBaseVariable):
    def __init__(self, name: str, objective: ObjectiveType):
        self._name = name
        self._objective = objective
        self._opt_objective: Optional[IOptimisationVariable] = None

    @property
    def objective(self) -> ObjectiveType:
        return self._objective

    @property
    def value(self) -> IOptimisationVariable:
        if self._opt_objective is None:
            raise NotImplementedError(f"Objective {self.name} is not created")
        else:
            return self._opt_objective

    @value.setter
    def value(self, var: IOptimisationVariable):
        self._opt_objective = var

    def evaluate(self) -> float:
        return self.value.evaluate()


class TimeIndexParameter(ITimeIndexBaseModel):
    def __init__(self, name: str, parameter_value: TimeseriesModel):
        self._name = name
        self._value = parameter_value
        self._parameter: List[Parameter] = [
            Parameter(f"{name}_{t}", self._value.get_value(t)) for t in self._value.timestamps
        ]
        self._opt_parameter: Optional[IOptimisationIndexVariable] = None

    @property
    def timestamps(self) -> Timestamps:
        return self._value.timestamps

    @property
    def name(self) -> str:
        return self._name

    @property
    def parameter_value(self):
        return self._value

    @property
    def value(self) -> List[Parameter]:
        return self._parameter

    @property
    def optimisation_value(self) -> IOptimisationIndexVariable:
        if self._opt_parameter is None:
            raise NotImplementedError(f"variable {self._name} is not created")
        else:
            return self._opt_parameter

    @optimisation_value.setter
    def optimisation_value(self, value: IOptimisationIndexVariable):
        self._opt_parameter = value
        for i, _ in enumerate(self.timestamps):
            self.value[i].value = self._opt_parameter[i]

    def evaluate(self) -> List[float]:
        return [v.value.evaluate() for v in self.value]

    def get_value_timestamp(self, timestamp: Timestamp) -> IBaseVariable:
        return self._get_value_timestamp(timestamp)

    def get_value_index(self, index: int) -> IBaseVariable:
        return self._get_value_timestamp(index)


class TimeIndexVariable(ITimeIndexBaseModel):
    def __init__(self, name: str, bounds: BoundTimeseries, initial_value: TimeseriesModel):
        self._name = name
        self._bounds = bounds
        self._initial_value = initial_value
        self._timestamps = initial_value.timestamps
        self._variable = [
            Variable(f"{name}_{t}", bounds.get_value(t), initial_value.get_value(t)) for t in self._timestamps
        ]
        self._opt_variable: Optional[IOptimisationIndexVariable] = None

    @property
    def name(self) -> str:
        return self._name

    @property
    def bounds(self) -> BoundTimeseries:
        return self._bounds

    @property
    def initial_value(self) -> TimeseriesModel:
        return self._initial_value

    @property
    def timestamps(self) -> Timestamps:
        return self._timestamps

    @property
    def value(self) -> List[Variable]:
        return self._variable

    @property
    def optimisation_value(self) -> IOptimisationIndexVariable:
        if self._opt_variable is None:
            raise NotImplementedError(f"variable {self._name} is not created")
        else:
            return self._opt_variable

    @optimisation_value.setter
    def optimisation_value(self, value: IOptimisationIndexVariable):
        self._opt_variable = value
        for i, _ in enumerate(self.timestamps):
            self.value[i].value = self._opt_variable[i]

    def evaluate(self) -> List[float]:
        return [v.evaluate() for v in self.value]

    def get_value_timestamp(self, timestamp: Timestamp) -> Variable:
        return self._get_value_timestamp(timestamp)

    def get_value_index(self, index: int) -> Variable:
        return self._get_value_index(index)


class TimeIndexConstraint:
    def __init__(
        self,
        name: str,
        timestamps: Timestamps,
        constraint_expression: List[ConstraintType],
    ):
        self._name = name
        self._timestamps = timestamps
        self._constraint: List[Constraint] = [
            Constraint(f"{name}_{t}", constraint_expression[i]) for i, t in enumerate(self._timestamps)
        ]
        self._constraint_expression = constraint_expression
        self._opt_constraint: Optional[IOptimisationIndexVariable] = None

    @property
    def name(self):
        return self._name

    @property
    def timestamps(self) -> Timestamps:
        return self._timestamps

    @property
    def value(self) -> List[Constraint]:
        return self._constraint

    @property
    def constraint_expression(self) -> List[ConstraintType]:
        return self._constraint_expression

    @property
    def optimisation_value(self) -> IOptimisationIndexVariable:
        if self._opt_constraint is None:
            raise NotImplementedError(f"variable {self._name} is not created")
        else:
            return self._opt_constraint

    @optimisation_value.setter
    def optimisation_value(self, value: IOptimisationIndexVariable):
        self._opt_constraint = value
        for i, _ in enumerate(self.timestamps):
            self.value[i].value = self._opt_constraint[i]

    def _get_value_timestamp(self, timestamp: Timestamp):
        try:
            return self.value[self.timestamps.get_timestamp_index(timestamp)]
        except (IndexError, ValueError):
            raise UnknownTimestampError(f"timestamp {timestamp} is not part of the timestamps defined")

    def evaluate(self) -> List[bool]:
        return [v.value.evaluate() for v in self.value]

    def get_value_timestamp(self, timestamp: Timestamp) -> Constraint:
        return self._get_value_timestamp(timestamp)


class TimeIndexObjective(ITimeIndexBaseModel):
    def __init__(self, name: str, timestamps: Timestamps):
        self._name = name
        self._timestamps = timestamps
        self._objective: Optional[List[ObjectiveType]] = None

    @property
    def name(self):
        return self._name

    @property
    def timestamps(self) -> Timestamps:
        return self._timestamps

    @property
    def value(self) -> List[ObjectiveType]:
        if self._objective is None:
            raise NotImplementedError(f"objective {self._name} is not created")
        else:
            return self._objective

    def evaluate(self) -> List[float]:
        return [v.evaluate() for v in self.value]

    def get_value_timestamp(self, timestamp: Timestamp) -> IExpression:
        return self._get_value_timestamp(timestamp)

    def get_value_index(self, index: int) -> IExpression:
        return self._get_value_timestamp(index)
