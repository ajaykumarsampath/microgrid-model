from model.component_interface import IComponentDataLoader
from model.domain import Bounds


class IGeneratorDataLoader(IComponentDataLoader):
    def __init__(self, initial_timestamp: int, power_bounds: Bounds, droop_gain: float = 0,
                 grid_forming_unit_flag: bool = False):
        super().__init__(initial_timestamp)
        self._power_bounds = power_bounds
        self._droop_gain = droop_gain
        self._grid_forming_unit_flag = grid_forming_unit_flag

    @property
    def power_bounds(self):
        return self._power_bounds

    @property
    def grid_forming_unit_flag(self):
        return self._grid_forming_unit_flag

    @property
    def droop_gain(self) -> float:
        return self._droop_gain