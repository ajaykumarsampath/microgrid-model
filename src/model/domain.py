from dataclasses import dataclass, field
from enum import Enum
from typing import List, Tuple, Optional

import numpy as np
from scipy.interpolate import interp1d


@dataclass
class Bounds:
    min: float
    max: float


BUS_ID = str
GRID_LINE = Tuple[BUS_ID, BUS_ID, float]
UNIT_BUS_ID_MAP = [str, BUS_ID]
SEC_TO_HOUR_FACTOR = 1/3600

class StepPreviousTimestamp(ValueError):
    pass

class UnknownComponentError(Exception):
    pass

class SimulationTimeseriesError(ValueError):
    pass

class SimulationGridError(Exception):
    pass

class MicrogirdModellingError(Exception):
    pass

class MicrogridSimulationError(Exception):
    pass


@dataclass
class UnitSimulationData:
    name: str
    values: dict


@dataclass
class HistoricalData:
    timestamps: List[int]
    data: List[UnitSimulationData]

    def __post_init__(self):
        if len(self.timestamps) > 0:
            if np.diff(self.timestamps).min() <= 0 or len(self.timestamps) != len(self.data):
                raise SimulationTimeseriesError('time stamps in the historical data should be increasing')

    def add_data(self, timestamp: int, data: UnitSimulationData):
        if len(self.timestamps) > 0:
            if timestamp <= self.timestamps[-1]:
                raise SimulationTimeseriesError('time stamps in the historical data should be increasing')
            else:
                self.timestamps.append(timestamp)
                self.data.append(data)
        else:
            self.timestamps.append(timestamp)
            self.data.append(data)



@dataclass
class GridLine:
    from_bus: BUS_ID
    to_bus: BUS_ID
    admittance: Optional[float] = field(default=None)
    bounds: Optional[Bounds] = field(default=None)

    def __eq__(self, other):
        try:
            if other.to_bus in [self.to_bus, self.from_bus] and \
                    other.from_bus in [self.to_bus, self.from_bus] and \
                    self.admittance == other.admittance:
                return True
            else:
                return False
        except AttributeError:
            return False

    def __post_init__(self):
        if self.to_bus == self.from_bus:
            raise ValueError('to_bus and from_bus of the line are same')


class SimulationTimeSeries:

    def __init__(self, timestamps: List[int], values:List[float]):
        try:
            self.timestamps = timestamps
            self.values = values
            self._function = interp1d(x=self.timestamps, y=self.values, kind='linear',
                                      fill_value="extrapolate")
        except Exception as err:
            raise SimulationTimeseriesError(f'{err}')


    def resample(self, timestamp: int):
        return self._function(timestamp)


class ComponentType(Enum):
    Load = 'Load'
    Renewable = 'Renewable'
    Storage = 'Storage'
    Thermal = 'Thermal'
    Grid = 'Grid'
    Unknown = 'None'