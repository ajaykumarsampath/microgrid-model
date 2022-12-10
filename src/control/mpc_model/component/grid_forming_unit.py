import logging

from common.model.component import ComponentType
from common.timeseries.domain import ConstantTimeseriesData, \
    BoundTimeseries
from control.mpc_model.control_data_model import ControlStoragePowerPlantData, ControlThermalGeneratorData
from control.mpc_model.domain import IControlComponent
from control.optimisation_engine.interface import IOptimisationEngine
from control.optimisation_engine.variable import TimeIndexVariable, TimeIndexConstraint, Constraint

logger = logging.getLogger(__name__)


class ControlStoragePowerPlant(IControlComponent):
    def __init__(self, data: ControlStoragePowerPlantData):
        self._component_type = ComponentType.Storage
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
    def energy(self) -> TimeIndexVariable:
        return self._energy

    @property
    def component_type(self):
        return self._component_type

    def _generate_variables(self):
        power_bounds = BoundTimeseries(
            min=ConstantTimeseriesData(self.timestamps, self._data.power_bounds.min),
            max=ConstantTimeseriesData(self.timestamps, self._data.power_bounds.max)
        )

        self._power = TimeIndexVariable(
            f'{self.name}_power', bounds=power_bounds,
            initial_value=ConstantTimeseriesData(self.timestamps, 0)
        )

        energy_bounds = BoundTimeseries(
            min=ConstantTimeseriesData(self.timestamps, self._data.energy_bounds.min),
            max=ConstantTimeseriesData(self.timestamps, self._data.energy_bounds.max)
        )

        self._energy = TimeIndexVariable(
            f'{self.name}_energy', bounds=energy_bounds,
            initial_value=ConstantTimeseriesData(self.timestamps, 0)
        )

    def _generate_constraint(self):
        constraint = [
            self._energy.get_value_index(i + 1) == self._energy.get_value_index(i) +
            (self.timestamps.values[i + 1] - self.timestamps.values[i]) *
            self._power.get_value_index(i) / 3600
            for i, t in enumerate(self.timestamps) if t < self.timestamps.values[-1]
        ]
        self._dynamics_constraint = TimeIndexConstraint(
            f'{self.name}_dynamic_constraint', self.timestamps.slice(0, len(self.timestamps) - 1),
            constraint
        )
        self._initial_energy_constraint = Constraint(
            f'{self.name}_initial_energy', self._energy[0] == self._data.current_energy
        )

    def extend_optimisation_model(self, optimisation_engine: IOptimisationEngine):
        self._power.optimisation_value = optimisation_engine.add_timeindex_variable(
            self._power.name, self._power.bounds, self._power.initial_value
        )

        self._energy.optimisation_value = optimisation_engine.add_timeindex_variable(
            self._energy.name, self._energy.bounds, self._energy.initial_value
        )

        self._dynamics_constraint.optimisation_value = optimisation_engine.add_timeindex_constraint(
            self._dynamics_constraint.name,
            [v.constraint_expression.value for v in self._dynamics_constraint.value]
        )

        self._initial_energy_constraint.value = optimisation_engine.add_constraint(
            f'{self.name}_initial_energy', self._initial_energy_constraint.constraint_expression.value
        )


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
    def component_type(self):
        return self._component_type

    def _generate_variables(self):
        self._power_lb = TimeIndexVariable(
            f'{self.name}_power_lb', bounds=BoundTimeseries(
                ConstantTimeseriesData(self.timestamps, 0),
                ConstantTimeseriesData(self.timestamps, self._data.power_bounds.min)
            ), initial_value=ConstantTimeseriesData(self.timestamps, 0)
        )
        self._power_ub = TimeIndexVariable(
            f'{self.name}_power_ub', bounds=BoundTimeseries(
                ConstantTimeseriesData(self.timestamps, 0),
                ConstantTimeseriesData(self.timestamps, self._data.power_bounds.max)
            ), initial_value=ConstantTimeseriesData(self.timestamps, 0)
        )

        self._power = TimeIndexVariable(
            f'{self.name}_power', bounds=BoundTimeseries(
                ConstantTimeseriesData(self.timestamps, 0),
                ConstantTimeseriesData(self.timestamps, self._data.power_bounds.max)
            ), initial_value=ConstantTimeseriesData(self.timestamps, 0)
        )

        self._switch_state = TimeIndexVariable(
            f'{self.name}_switch_state', bounds=BoundTimeseries(
                ConstantTimeseriesData(self.timestamps, 0),
                ConstantTimeseriesData(self.timestamps, 1)
            ), initial_value=ConstantTimeseriesData(self.timestamps, 0)
        )

    def _generate_constraint(self):
        self._lb_constraint = TimeIndexConstraint(
            f'{self.name}_lb_constraint', self.timestamps,
            constraint_expression=[
                self._power_lb.get_value_timestamp(t) == self._switch_state.get_value_timestamp(t) *
                self._data.power_bounds.min
                for t in self.timestamps]
        )
        self._ub_constraint = TimeIndexConstraint(
            f'{self.name}_ub_constraint', self.timestamps,
            constraint_expression=[
                self._power_ub.get_value_timestamp(t) ==
                self._switch_state.get_value_timestamp(t) * self._data.power_bounds.max
                for t in self.timestamps]
        )
        self._power_lb_constraint = TimeIndexConstraint(
            f'{self.name}_ub_constraint', self.timestamps,
            constraint_expression=[
                self._power.get_value_timestamp(t) >= self._power_lb.get_value_timestamp(t)
                for t in self.timestamps
            ]
        )
        self._power_ub_constraint = TimeIndexConstraint(
            f'{self.name}_ub_constraint', self.timestamps,
            constraint_expression=[
                self._power.get_value_timestamp(t) <= self._power_ub.get_value_timestamp(t)
                for t in self.timestamps
            ]
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
        self._lb_constraint.optimisation_value = optimisation_engine.add_timeindex_constraint(
            self._lb_constraint.name,
            [v.constraint_expression.value for v in self._lb_constraint.value]
        )
        self._ub_constraint.optimisation_value = optimisation_engine.add_timeindex_constraint(
            self._ub_constraint.name,
            [v.constraint_expression.value for v in self._ub_constraint.value]
        )
        self._power_lb_constraint.optimisation_value = optimisation_engine.add_timeindex_constraint(
            self._lb_constraint.name,
            [v.constraint_expression.value for v in self._power_lb_constraint.value]
        )
        self._power_ub_constraint.optimisation_value = optimisation_engine.add_timeindex_constraint(
            self._ub_constraint.name,
            [v.constraint_expression.value for v in self._power_ub_constraint.value]
        )
