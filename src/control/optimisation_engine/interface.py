from typing import List, Callable

from common.timeseries.domain import Bounds, Timestamps, TimeseriesModel, BoundTimeseries
from control.optimisation_engine.domain import IOptimisationVariable, OptimisationExpression, \
    TimeIndexObjectiveType, ConstraintType, ObjectiveType


class IOptimisationEngine:
    @property
    def model(self):
        raise NotImplementedError

    @property
    def timestamps(self) -> Timestamps:
        raise NotImplementedError

    def solve(self):
        raise NotImplementedError

    def add_parameter(self, name: str, value: float) -> IOptimisationVariable:
        raise NotImplementedError

    def add_variable(self, name: str, bounds: Bounds, initial_value: float) -> IOptimisationVariable:
        raise NotImplementedError

    def add_binary_variable(self, name: str, initial_value: float) -> IOptimisationVariable:
        raise NotImplementedError

    def add_constraint(self, name: str, constraint: ConstraintType) -> IOptimisationVariable:
        raise NotImplementedError

    def add_objective(self, name: str, objective: OptimisationExpression):
        raise NotImplementedError

    def update_objective(self, variable: IOptimisationVariable, obj_callable: Callable):
        raise NotImplementedError

    def add_timeindex_parameter(self, name: str, value: TimeseriesModel):
        raise NotImplementedError

    def add_timeindex_variable(self, name: str, bound: BoundTimeseries, initial_value: TimeseriesModel):
        raise NotImplementedError

    def add_timeindex_binary_variable(self, name: str, initial_value: TimeseriesModel):
        raise NotImplementedError

    def add_index_constraint(self, name: str, constraint: List[ConstraintType]):
        raise NotImplementedError
