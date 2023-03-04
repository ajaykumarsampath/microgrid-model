from common.timeseries.domain import Bounds, Timestamp
from microgrid.shared.data_loader import IComponentDataLoader


class IGeneratorDataLoader(IComponentDataLoader):
    def __init__(
        self,
        initial_timestamp: int,
        power_bounds: Bounds,
        droop_gain: float = 0,
        grid_forming_unit_flag: bool = False,
    ):
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


class IRenewableUnitDataLoader(IGeneratorDataLoader):
    def get_data(self, timestamp: Timestamp):
        raise NotImplementedError


class ILoadDemandDataLoader(IComponentDataLoader):
    def get_data(self, timestamp: Timestamp):
        raise NotImplementedError


class IGridNetworkDataLoader(IComponentDataLoader):
    @property
    def grid_lines(self):
        raise NotImplementedError

    def buses(self):
        raise NotImplementedError

    def validate_grid_line_data(self):
        raise NotImplementedError

    def check_grid_network_connected(self):
        raise NotImplementedError


class IThermalGeneratorDataLoader(IGeneratorDataLoader):
    @property
    def switch_state(self):
        raise NotImplementedError


class IStoragePowerPlantDataLoader(IGeneratorDataLoader):
    @property
    def initial_energy(self):
        raise NotImplementedError

    @property
    def energy_bounds(self):
        raise NotImplementedError
