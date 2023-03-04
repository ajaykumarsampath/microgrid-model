from common.model.component import ComponentType
from common.timeseries.domain import BoundTimeseries, ConstantTimeseriesData
from control.mpc_model.control_data_model import ControlThermalGeneratorData
from control.mpc_model.domain import IControlComponent
from control.optimisation_engine.interface import IOptimisationEngine
from control.optimisation_engine.variable import TimeIndexVariable, TimeIndexConstraint


class ControlThermalGenerator(IControlComponent):
    def __init__(self, data: ControlThermalGeneratorData):
        self._component_type = ComponentType.Thermal
        self._data = data

        self._generate_variables()
        self._generate_constraint()

    @property
    def name(self):
        return self._data.name

    @property
    def timestamps(self):
        return self._data.timestamps

    @property
    def power(self) -> TimeIndexVariable:
        return self._power

    @property
    def switch_state(self) -> TimeIndexVariable:
        return self._switch_state

    @property
    def component_type(self):
        return self._component_type

    def _generate_variables(self):
        self._power_lb = TimeIndexVariable(
            f"{self.name}_power_lb",
            bounds=BoundTimeseries.constant_bound_timeseries(self.timestamps, 0, self._data.power_bounds.min),
            initial_value=ConstantTimeseriesData(self.timestamps, 0),
        )
        self._power_ub = TimeIndexVariable(
            f"{self.name}_power_ub",
            bounds=BoundTimeseries.constant_bound_timeseries(self.timestamps, 0, self._data.power_bounds.max),
            initial_value=ConstantTimeseriesData(self.timestamps, 0),
        )

        self._power = TimeIndexVariable(
            f"{self.name}_power",
            bounds=BoundTimeseries.constant_bound_timeseries(self.timestamps, 0, self._data.power_bounds.max),
            initial_value=ConstantTimeseriesData(self.timestamps, 0),
        )

        self._switch_state = TimeIndexVariable(
            f"{self.name}_switch_state",
            bounds=BoundTimeseries.constant_bound_timeseries(self.timestamps, 0, 1),
            initial_value=ConstantTimeseriesData(self.timestamps, 0),
        )

    def _generate_constraint(self):
        self._lb_constraint = TimeIndexConstraint(
            f"{self.name}_lb_constraint",
            self.timestamps,
            constraint_expression=[
                self._power_lb.get_value_timestamp(t) ==
                self._switch_state.get_value_timestamp(t) * self._data.power_bounds.min
                for t in self.timestamps
            ],
        )
        self._ub_constraint = TimeIndexConstraint(
            f"{self.name}_ub_constraint",
            self.timestamps,
            constraint_expression=[
                self._power_ub.get_value_timestamp(t) ==
                self._switch_state.get_value_timestamp(t) * self._data.power_bounds.max
                for t in self.timestamps
            ],
        )
        self._power_lb_constraint = TimeIndexConstraint(
            f"{self.name}_ub_constraint",
            self.timestamps,
            constraint_expression=[
                self._power.get_value_timestamp(t) >= self._power_lb.get_value_timestamp(t) for t in self.timestamps
            ],
        )
        self._power_ub_constraint = TimeIndexConstraint(
            f"{self.name}_ub_constraint",
            self.timestamps,
            constraint_expression=[
                self._power.get_value_timestamp(t) <= self._power_ub.get_value_timestamp(t) for t in self.timestamps
            ],
        )

    def extend_optimisation_model(self, optimisation_engine: IOptimisationEngine):
        self._power.optimisation_value = optimisation_engine.add_timeindex_variable(
            self._power.name, self._power.bounds, self._power.initial_value
        )
        self._power_lb.optimisation_value = optimisation_engine.add_timeindex_variable(
            self._power_lb.name, self._power_lb.bounds, self._power_lb.initial_value
        )
        self._power_ub.optimisation_value = optimisation_engine.add_timeindex_variable(
            self._power_ub.name, self._power_ub.bounds, self._power_ub.initial_value
        )

        self._switch_state.optimisation_value = optimisation_engine.add_timeindex_binary_variable(
            self._switch_state.name, self._switch_state.initial_value
        )

        # constraints
        self._lb_constraint.optimisation_value = optimisation_engine.add_index_constraint(
            self._lb_constraint.name,
            [v.constraint_expression for v in self._lb_constraint.value],
        )
        self._ub_constraint.optimisation_value = optimisation_engine.add_index_constraint(
            self._ub_constraint.name,
            [v.constraint_expression for v in self._ub_constraint.value],
        )

        self._power_lb_constraint.optimisation_value = optimisation_engine.add_index_constraint(
            self._lb_constraint.name,
            [v.constraint_expression for v in self._power_lb_constraint.value],
        )
        self._power_ub_constraint.optimisation_value = optimisation_engine.add_index_constraint(
            self._ub_constraint.name,
            [v.constraint_expression for v in self._power_ub_constraint.value],
        )
