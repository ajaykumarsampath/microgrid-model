from dataclasses import dataclass
from typing import List

import numpy as np

from microgrid.shared.simulation_data import ComponentSimulationData
from microgrid.shared.storage import IComponentDataStorage
from microgrid.shared.timeseries import Timestamp, SimulationTimeseriesError


@dataclass
class HistoricalData:
    timestamps: List[Timestamp]
    data: List[ComponentSimulationData]

    def __post_init__(self):
        if len(self.timestamps) > 0:
            if np.diff(self.timestamps).min() <= 0 or len(self.timestamps) != len(self.data):
                raise SimulationTimeseriesError("time stamps in the historical data should be increasing")

    def add_data(self, timestamp: int, data: ComponentSimulationData):
        if len(self.timestamps) > 0:
            if timestamp <= self.timestamps[-1]:
                raise SimulationTimeseriesError("time stamps in the historical data should be increasing")
            else:
                self.timestamps.append(timestamp)
                self.data.append(data)
        else:
            self.timestamps.append(timestamp)
            self.data.append(data)


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

    def get_historical_data(self, since: int, until: int = None, unit_id: str = None) -> List[ComponentSimulationData]:
        pass
