from typing import List

from model.domain import UnitSimulationData, HistoricalData


class IUnitDataStorage:
    """
    def initial_timestamp(self):
        raise NotImplementedError

    def get_last_updated_timestamp(self):
        raise NotImplementedError
    """

    def add_simulation_data(self, current_timestamp: int, data: UnitSimulationData):
        raise NotImplementedError

    def get_historical_data(self, unit_id: str, since: int, until: int=None) -> List[UnitSimulationData]:
        raise NotImplementedError


class UnitDataStorage(IUnitDataStorage):
    def __init__(self, initial_timestamp: int):
        self._initial_timestamp = initial_timestamp
        self._current_timestamp = initial_timestamp
        self.historical_data = HistoricalData([], [])

    @property
    def initial_timestamp(self):
        return self._initial_timestamp

    @property
    def current_timestamp(self):
        return self._current_timestamp

    def add_simulation_data(self, current_timestamp, data: UnitSimulationData):
        self._current_timestamp = current_timestamp
        self.historical_data.timestamps.append(current_timestamp)
        self.historical_data.data.append(data)

    def get_historical_data(self, since: int, until:int=None, unit_id: str=None) -> List[UnitSimulationData]:
        pass