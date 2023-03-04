from dataclasses import dataclass
from enum import Enum
from typing import List, Callable, TypeVar, Optional

from common.timeseries.domain import Bounds, TimeseriesModel, BoundTimeseries
from control.optimisation_engine.cvx_engine.variable import (
    CvxVariable,
    CvxParameter,
    CvxConstraint,
    CvxObjective,
    CvxIndexVariable,
    CvxIndexConstraint,
    CvxIndexParameter,
)
from control.optimisation_engine.domain import (
    IOptimisationVariable,
    OptimisationExpression,
    VariableType,
    ConstraintType,
)
from control.optimisation_engine.interface import IOptimisationEngine
import cvxpy as cp


@dataclass
class OptimisationSolveRequest:
    variable_ids: List[str] = None
    all_variables: bool = True
    constraint_ids: List[str] = None
    all_constraints: bool = True


class OptimisationEngineStatus(Enum):
    Infeasible: str = "infeasible"
    Optimal: str = "optimal"


class DuplicateOptimisationEngineValue(Exception):
    pass


CvxTypeVar = TypeVar(
    "CvxTypeVar",
    CvxVariable,
    CvxParameter,
    CvxConstraint,
    CvxIndexParameter,
    CvxIndexVariable,
    CvxIndexConstraint,
)


class CvxEngine(IOptimisationEngine):
    def __init__(self):
        self._variable: List[CvxTypeVar] = []
        self._constraint: List[CvxTypeVar] = []
        self._parameter: List[CvxTypeVar] = []
        self._objective: Optional[CvxTypeVar] = None
        self._timestamps = None
        self._model: Optional[cp.Problem] = None
        self._value = None
        self.status: Optional[OptimisationEngineStatus] = None
        self._has_binary_variable = False
        self._mixed_integer_solver_parameters = {"solver": "CBC"}

    @property
    def objective(self):
        return self._objective

    @property
    def variable(self):
        return self._variable

    @property
    def constraint(self):
        return self._constraint

    @property
    def value(self):
        return self._value

    def _add_optimisation_value(self, current_value: CvxTypeVar, existing_values: List[CvxTypeVar]) -> List[CvxTypeVar]:
        if current_value.name in [v.name for v in existing_values]:
            raise DuplicateOptimisationEngineValue(
                f"cvx value with name {current_value.name} already added to the model"
            )
        else:
            existing_values.append(current_value)
            return existing_values

    def generate_optimisation_model(self) -> None:
        constraints = []
        variables = []
        for v in self._variable:
            variables.append(v.value)
            constraints.extend(v.bound_constraints)

        for c in self._constraint:
            if isinstance(c, CvxIndexConstraint):
                constraints.extend(c.value)
            else:
                constraints.append(c.value)

        self._model = cp.Problem(self._objective.evaluate(), constraints)

    def solve(self) -> None:
        if self._model is not None:
            self.generate_optimisation_model()

        if self._has_binary_variable:
            self._model.solve(**self._mixed_integer_solver_parameters)
        else:
            self._model.solve()
        if self._model.status == "optimal":
            self.status = OptimisationEngineStatus.Optimal
        else:
            self.status = OptimisationEngineStatus.Infeasible

        self._value = self._model.value

    def add_parameter(self, name: str, value: float) -> CvxParameter:
        parameter = CvxParameter(name, value)
        self._parameter = self._add_optimisation_value(parameter, self._parameter)
        return parameter

    def add_variable(self, name: str, bounds: Bounds, initial_value: float) -> CvxVariable:
        variable = CvxVariable(name, initial_value, bounds)
        self._variable = self._add_optimisation_value(variable, self._variable)
        return variable

    def add_binary_variable(self, name: str, initial_value: float) -> CvxVariable:
        self._has_binary_variable = True
        variable = CvxVariable(name, initial_value, Bounds(0, 1), VariableType.Binary)
        self._variable = self._add_optimisation_value(variable, self._variable)
        return variable

    def add_constraint(self, name: str, constraint_expression: ConstraintType) -> CvxConstraint:
        cvx_constraint = CvxConstraint(name, constraint_expression)
        self._constraint = self._add_optimisation_value(cvx_constraint, self._constraint)
        return cvx_constraint

    def add_objective(self, name: str, objective: OptimisationExpression) -> None:
        if self._objective is None:
            self._objective = CvxObjective(objective)

    def update_objective(self, variable: IOptimisationVariable, obj_callable: Callable, *args) -> None:
        cvx_expr = OptimisationExpression(obj_callable(variable.value, *args))
        if self._objective is None:
            self._objective = CvxObjective(cvx_expr)
        else:
            self._objective.update_objective(cvx_expr)

    def add_timeindex_parameter(self, name: str, value: TimeseriesModel) -> CvxIndexParameter:
        index = [i for i, _ in enumerate(value.timestamps)]
        cvx_index_parameter = CvxIndexParameter(name, index, value.values)
        self._parameter = self._add_optimisation_value(cvx_index_parameter, self._parameter)
        return cvx_index_parameter

    def add_timeindex_variable(
        self, name: str, bound: BoundTimeseries, initial_value: TimeseriesModel
    ) -> CvxIndexVariable:
        index = [i for i, _ in enumerate(bound.timestamps)]
        bounds_list = [bound.get_value_as_bound(t) for t in bound.timestamps]
        cvx_index_variable = CvxIndexVariable(name=name, index=index, bounds=bounds_list, value=initial_value.values)
        self._variable = self._add_optimisation_value(cvx_index_variable, self._variable)
        return cvx_index_variable

    def add_timeindex_binary_variable(self, name: str, initial_value: TimeseriesModel) -> CvxIndexVariable:
        index = [i for i, _ in enumerate(initial_value.timestamps)]
        bound_list = [Bounds(0, 1) for _ in initial_value.timestamps]
        cvx_index_var = CvxIndexVariable(
            name=name,
            index=index,
            value=initial_value.values,
            bounds=bound_list,
            variable_type=VariableType.Binary,
        )
        self._variable = self._add_optimisation_value(cvx_index_var, self._variable)
        return cvx_index_var

    def add_index_constraint(self, name: str, constraint: List[ConstraintType]) -> CvxIndexConstraint:
        cvx_constraint = CvxIndexConstraint(name, constraint)
        self._constraint = self._add_optimisation_value(cvx_constraint, self._constraint)
        return cvx_constraint
