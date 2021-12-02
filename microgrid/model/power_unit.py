from typing import List

from microgrid.model.domain import Bounds, UnitSimulationData, HistoricalData


class UnitDataStorage(object):
    def __int__(self, initial_timestamp: int):
        self.initial_timestamp = initial_timestamp
        self.current_timestamp = initial_timestamp
        self.historical_data = HistoricalData([], [])


    def add_simulation_data(self, current_timestamp, data: UnitSimulationData):
        self.current_timestamp = current_timestamp
        self.historical_data.time_stamps.append(current_timestamp)
        self.historical_data.data.append(data)


    def get_historical_data(self, since: int, until:int=None) -> List[UnitSimulationData]:
        pass


class Unit:
    def __init__(self, name: str, initial_timestamp: int):
        self.name = name
        self._storage = UnitDataStorage(initial_timestamp)
        self._current_power = 0

    def step(self, timestamp: int):
        raise NotImplementedError

    @property
    def current_power(self):
        return self._current_power

    def get_initial_timestamp(self):
        return self._storage.initial_timestamp

    def current_timestamp(self):
        return self._storage.current_timestamp

    def _add_simulation_data(self, timestamp: int, data: UnitSimulationData):
        self._storage.add_simulation_data(current_timestamp=timestamp, data=data)

    def _generate_simulation_data(self) -> UnitSimulationData:
        raise NotImplementedError


class PowerUnit(Unit):
    def __init__(self, name: str, initial_timestamp: int, power_bounds: Bounds):
        super().__init__(name, initial_timestamp)
        self.power_bounds = power_bounds
        self._power_setpoint = 0

    def step(self, timestamp: int):
        raise NotImplementedError

    def is_grid_forming_unit(self) -> bool:
        return False

    @property
    def power_setpoint(self):
        return self._power_setpoint

    @power_setpoint.setter
    def power_setpoint(self, value: float):
        if self.power_bounds.min  <= value <= self.power_bounds.max:
            self._power_setpoint = value
        else:
            raise ValueError(f"power set point to set in not satisfying the bounds "
                             f"in the unit {self.name}")
