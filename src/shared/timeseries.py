from typing import List

from scipy.interpolate import interp1d

Timestamp = int

class SimulationTimeSeries:

    def __init__(self, timestamps: List[Timestamp], values:List[float]):
        try:
            self.timestamps = timestamps
            self.values = values
            self._function = interp1d(x=self.timestamps, y=self.values, kind='linear',
                                      fill_value="extrapolate")
        except Exception as err:
            raise SimulationTimeseriesError(f'{err}')


    def resample(self, timestamp: Timestamp):
        return self._function(timestamp)


class SimulationTimeseriesError(ValueError):
    pass