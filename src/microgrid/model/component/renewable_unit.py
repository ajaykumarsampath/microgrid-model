from common.model.component import ComponentType, ControlComponentData
from microgrid.data_loader.interface import IRenewableUnitDataLoader
from microgrid.model.generator_interface import IGeneratorComponent
import logging

from microgrid.shared.simulation_data import ComponentSimulationData
from microgrid.shared.timeseries import Timestamp

logger = logging.getLogger(__name__)


class RenewablePowerUnit(IGeneratorComponent):
    def __init__(self, name: str, data_loader: IRenewableUnitDataLoader):

        super().__init__(name, data_loader)
        self._data_loader = data_loader
        self._available_power = 0
        self._component_type = ComponentType.Renewable

    @property
    def control_component_data(self) -> ControlComponentData:
        return ControlComponentData(
            self._name, self._component_type, self._current_timestamp,
            self._data_loader.power_bounds
        )

    def calculate_available_power(self, timestamp: Timestamp):
        return self._data_loader.get_data(timestamp)

    def step(self, timestamp: Timestamp):
        self._check_step_timestamp(timestamp)
        self._available_power = self.calculate_available_power(timestamp=timestamp)
        self._current_power = min(self._available_power, self.power_setpoint)

    def current_simulation_data(self) -> ComponentSimulationData:
        values = {'current_power': self._current_power, 'available_power': self._available_power,
                  'power_setpoint': self._power_setpoint}
        return ComponentSimulationData(self._name, values=values)
