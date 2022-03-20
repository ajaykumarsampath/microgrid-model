from typing import List

from scipy.interpolate import interp1d


class SamplePointsToPowerTable:

    def __init__(self, points: List[float], power_values: List[float]):
        assert points[0] == 0
        assert power_values[0] == 0
        self._points = points
        self._power_values = power_values
        try:
            self.point_to_power_function = interp1d(x=self._points, y = self._power_values)
        except Exception:
            raise ValueError("Input data is not of the same length ")

    def maximum(self):
        return max(self._power_values)

    def minimum(self):
        return min(self._power_values)

    def available_power_at_sample_point(self, point: float):
        try:
            return self.point_to_power_function(x=point)
        except ValueError:
            raise ValueError("point is not part of the table and cannot be extrapolated")

class DuplicateUnitNameError(ValueError):
    pass

class UnitDataLoaderError(Exception):
    pass

class DuplicateGridModelError(ValueError):
    pass

class UnknownComponentQueryError(ValueError):
    pass
