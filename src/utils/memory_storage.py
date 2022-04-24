from typing import List

from shared.component import ComponentSimulationData
from shared.storage import IComponentDataStorage
from utils.storage import HistoricalData


class MemoryDataStorage(IComponentDataStorage):
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

    def add_simulation_data(self, current_timestamp, data: ComponentSimulationData):
        self._current_timestamp = current_timestamp
        self.historical_data.timestamps.append(current_timestamp)
        self.historical_data.data.append(data)

    def get_historical_data(self, since: int, until:int=None, unit_id: str=None) \
            -> List[ComponentSimulationData]:
        pass