import logging

import numpy as np

from common.model.component import ComponentType
from common.timeseries.domain import ConstantTimeseriesData, BoundTimeseries
from control.mpc_model.control_data_model import (
    ControlStoragePowerPlantData,
)
from control.mpc_model.domain import IControlComponent
from control.optimisation_engine.interface import IOptimisationEngine
from control.optimisation_engine.variable import (
    TimeIndexVariable,
    TimeIndexConstraint,
    Constraint,
)

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
            max=ConstantTimeseriesData(self.timestamps, self._data.power_bounds.max),
        )

        self._power = TimeIndexVariable(
            f"{self.name}_power",
            bounds=power_bounds,
            initial_value=ConstantTimeseriesData(self.timestamps, 0),
        )

        energy_bounds = BoundTimeseries(
            min=ConstantTimeseriesData(self.timestamps, self._data.energy_bounds.min),
            max=ConstantTimeseriesData(self.timestamps, self._data.energy_bounds.max),
        )

        self._energy = TimeIndexVariable(
            f"{self.name}_energy",
            bounds=energy_bounds,
            initial_value=ConstantTimeseriesData(self.timestamps, 0),
        )

    def _generate_constraint(self):
        constraint = [
            self._energy.get_value_index(i + 1) ==
            self._energy.get_value_index(i) - d * self._power.get_value_index(i) / 3600
            for i, d in enumerate(np.diff(self.timestamps))
        ]
        self._dynamics_constraint = TimeIndexConstraint(
            f"{self.name}_dynamic_constraint",
            self.timestamps.slice(0, len(self.timestamps) - 1),
            constraint,
        )
        self._initial_energy_constraint = Constraint(
            f"{self.name}_initial_energy", self._energy[0] == self._data.current_energy
        )

    def extend_optimisation_model(self, optimisation_engine: IOptimisationEngine):
        self._power.optimisation_value = optimisation_engine.add_timeindex_variable(
            self._power.name, self._power.bounds, self._power.initial_value
        )

        self._energy.optimisation_value = optimisation_engine.add_timeindex_variable(
            self._energy.name, self._energy.bounds, self._energy.initial_value
        )

        self._dynamics_constraint.optimisation_value = optimisation_engine.add_index_constraint(
            self._dynamics_constraint.name,
            [v.constraint_expression for v in self._dynamics_constraint.value],
        )

        self._initial_energy_constraint.value = optimisation_engine.add_constraint(
            f"{self.name}_initial_energy",
            self._initial_energy_constraint.constraint_expression,
        )
