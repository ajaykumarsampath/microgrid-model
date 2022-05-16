from dataclasses import dataclass
from typing import List

import numpy as np

from shared.component import ComponentSimulationData
from shared.timeseries import SimulationTimeseriesError, Timestamp


@dataclass
class HistoricalData:
    timestamps: List[Timestamp]
    data: List[ComponentSimulationData]

    def __post_init__(self):
        if len(self.timestamps) > 0:
            if np.diff(self.timestamps).min() <= 0 or \
                    len(self.timestamps) != len(self.data):
                raise SimulationTimeseriesError(
                    'time stamps in the historical data should be increasing')

    def add_data(self, timestamp: int, data: ComponentSimulationData):
        if len(self.timestamps) > 0:
            if timestamp <= self.timestamps[-1]:
                raise SimulationTimeseriesError(
                    'time stamps in the historical data should be increasing')
            else:
                self.timestamps.append(timestamp)
                self.data.append(data)
        else:
            self.timestamps.append(timestamp)
            self.data.append(data)
