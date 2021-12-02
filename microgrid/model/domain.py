from dataclasses import dataclass
from typing import List, Tuple

from scipy.interpolate import interp1d

from microgrid.model.grid_model import GridLine


class Bounds:
    def __init__(self, min: float, max: float):
        self.min = min
        self.max = max


class SimulationTimeSeries:

    def __init__(self, timestamps: List[int], values:List[int]):
        self.timestamps = timestamps
        self.values = values
        self._function = interp1d(x=self.timestamps, y=values, kind='liner',
                                  fill_value="extrapolate")

    def resample(self, timestamp: int):
        return self._function(timestamp)


class SamplePointsToPowerTable:

    def __init__(self, point_and_power: List[Tuple[float, float]]):
        assert point_and_power[0] == (0, 0)
        self.points = [p[0] for p in point_and_power]
        self.power_values = [p[1] for p in point_and_power]
        self.point_to_power_function = interp1d(x=self.power_values, y = self.power_values)

    def maximum(self):
        return max(self.power_values)

    def minimum(self):
        return min(self.power_values)

    def available_power_at_sample_point(self, point: float):
        return self.point_to_power_function(x=point)


SEC_TO_HOUR_FACTOR = 1/3600


@dataclass
class RenewableUnitControlConfig:
    power_bounds: Bounds
    power_set_point: float
    forecaster: None

@dataclass
class ThermalUnitControlConfig:
    power_bounds: Bounds
    power_set_point: float
    switch_state: bool

@dataclass
class StorageUnitControlConfig:
    power_bounds: Bounds
    energy_bounds: Bounds
    power_set_point: float
    current_energy: float

@dataclass
class GridModelControlConfig:
    grid_lines: List[GridLine]


@dataclass
class UnitSimulationData:
    values: dict


class HistoricalData:
    time_stamps: List[int]
    data: List[UnitSimulationData]