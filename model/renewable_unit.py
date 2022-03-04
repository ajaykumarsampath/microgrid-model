from data_loader.renewable_unit import IRenewableUnitDataLoader
from model.domain import UnitSimulationData
from model.generator_interface import IGeneratorComponent
import logging

logger = logging.getLogger(__name__)


class RenewablePowerUnit(IGeneratorComponent):
    def __init__(self, name: str, data_loader: IRenewableUnitDataLoader):

        super().__init__(name, data_loader)
        self._data_loader = data_loader
        self._available_power = 0

    def calculate_available_power(self, timestamp: int):
        return self._data_loader.get_data(timestamp)

    def step(self, timestamp: int):
        self._check_step_timestamp(timestamp)
        self._available_power = self.calculate_available_power(timestamp=timestamp)
        self._current_power = min(self._available_power, self.power_setpoint)

    def current_simulation_data(self) -> UnitSimulationData:
        values = {'current_power': self._current_power, 'available_power': self._available_power,
                  'power_setpoint': self._power_setpoint}
        return UnitSimulationData(self._name,values=values)
