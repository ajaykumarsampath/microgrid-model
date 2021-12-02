from microgrid.model.domain import Bounds, UnitSimulationData
from microgrid.model.power_unit import PowerUnit


class PCCConnection(PowerUnit):
    def __init__(self, name: str, initial_timestamp: int, power_bounds: Bounds):
        super().__init__(name, initial_timestamp, power_bounds)
        self._add_simulation_data(timestamp=initial_timestamp,
                                  data=self._generate_simulation_data())

    def step(self, timestamp: int):
        self.current_power = self.power_setpoint
        self._add_simulation_data(timestamp,data=self._generate_simulation_data())

    def _generate_simulation_data(self) -> UnitSimulationData:
        values = {'current_power': self.current_power, 'power_setpoint': self.power_setpoint}
        return UnitSimulationData(values)
