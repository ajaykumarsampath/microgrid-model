from typing import List, Callable

from common.timeseries.domain import Bounds, TimeseriesModel, BoundTimeseries
from control.optimisation_engine.cvx_engine.variable import CvxVariable, CvxParameter, CvxConstraint, \
    CvxObjective, CvxIndexVariable, generate_cvx_index_bound_constraint, \
    CvxIndexConstraint, CvxIndexParameter
from control.optimisation_engine.domain import IOptimisationVariable, OptimisationExpression, \
    VariableType
from control.optimisation_engine.interface import IOptimisationEngine
import cvxpy as cp

class CvxEngine(IOptimisationEngine):
    def __init__(self):
        self._variable = []
        self._constraint = []
        self._parameter = []
        self._objective = None
        self._timestamps = None

    def generate_optimisation_model(self):
        self._model = cp.Problem(self._objective.evaluate(), self._constraint)

    def solve(self):
        self._model.solve()

    def add_parameter(self, name: str, value: float) -> IOptimisationVariable:
        parameter = CvxParameter(name, value)
        self._parameter.append(parameter.value)
        return parameter

    def add_variable(self, name: str, bounds: Bounds, initial_value: float) -> IOptimisationVariable:
        variable = CvxVariable(name, initial_value)
        constraint =  bounds.min <= variable.value <= bounds.max
        self._variable.append(variable.value)
        self._constraint.append(constraint)
        return variable


    def add_binary_variable(self, name: str, initial_value: float) -> IOptimisationVariable:
        variable = CvxVariable(name, initial_value, VariableType.Binary)
        self._variable.append(variable.value)
        return variable

    def add_constraint(self, name: str, constraint: OptimisationExpression) -> IOptimisationVariable:
        cvx_constraint = CvxConstraint(constraint)
        self._constraint.append(constraint.value)
        return cvx_constraint

    def add_objective(self, name: str, objective: OptimisationExpression):
        if self._objective is None:
            self._objective = CvxObjective(objective)

    def update_objective(self, variable: IOptimisationVariable,
                         obj_callable: Callable, *args):
        cvx_expr = OptimisationExpression(obj_callable(variable.value, *args))
        if self._objective is None:
            self._objective = CvxObjective(cvx_expr)
        else:
            self._objective = self._objective.add_objective(cvx_expr)

    def add_timeindex_parameter(self, name: str, value: TimeseriesModel):
        index = [i for i, _ in enumerate(value.timestamps)]
        cvx_index_parameter = CvxIndexParameter(name, index, value.values)
        return cvx_index_parameter

    def add_timeindex_variable(self, name: str, bound: BoundTimeseries, initial_value: TimeseriesModel):
        index = [i for i, _ in enumerate(bound.timestamps)]
        cvx_power_var = CvxIndexVariable(name=name, index=index, value=initial_value.values)
        self._variable.extend(cvx_power_var.value)
        self._constraint.extend(
            generate_cvx_index_bound_constraint(cvx_power_var.value, bound)
        )
        return cvx_power_var


    def add_timeindex_binary_variable(self, name: str, initial_value: TimeseriesModel):
        index = [i for i, _ in enumerate(initial_value.timestamps)]
        cvx_power_var = CvxIndexVariable(name=name, index=index, value=initial_value.values,
                                         variable_type=VariableType.Binary)
        self._variable.extend(cvx_power_var)
        return cvx_power_var

    def add_timeindex_constraint(self, name: str, constraint: List[OptimisationExpression]):
        cvx_constraint = CvxIndexConstraint(name, [OptimisationExpression(c) for c in constraint])
        self._constraint.extend(cvx_constraint.value)
        return cvx_constraint
