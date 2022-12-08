from common.timeseries.domain import Bounds
from microgrid.data_loader.domain import UnitDataLoaderError
from microgrid.data_loader.interface import IThermalGeneratorDataLoader, IStoragePowerPlantDataLoader
import logging

logger = logging.getLogger(__name__)

"""
class GridFormingUnitDataLoader(IGeneratorDataLoader):
    def __init__(self, initial_timestamp: int, power_bounds: Bounds, droop_gain: float,
                 grid_forming_unit_flag: bool = True):
        if droop_gain <= 0:
            logger.warning('Droop gain should be positive')
        else:
            super().__init__(initial_timestamp, power_bounds, droop_gain, grid_forming_unit_flag)
"""


class StoragePowerPlantDataLoader(IStoragePowerPlantDataLoader):
    def __init__(self, initial_timestamp: int, power_bounds: Bounds, droop_gain: float,
                 energy_bounds: Bounds, initial_energy: float = 0, charge_efficiency: float = 1,
                 discharge_efficiency: float = 1):
        self._energy_bounds = energy_bounds

        if droop_gain < 0:
            raise UnitDataLoaderError('storage: Droop gain should be positive')
        else:
            super().__init__(initial_timestamp, power_bounds, droop_gain,
                             grid_forming_unit_flag=True)

        if self.energy_bounds.min <= initial_energy <= self.energy_bounds.max:
            self._initial_energy = initial_energy
        else:
            raise UnitDataLoaderError('storage: initial energy is not '
                                      'contained in the energy bounds')

        if 0 < charge_efficiency <= 1:
            self._charge_efficiency = charge_efficiency
        else:
            raise UnitDataLoaderError('storage: charging efficiency should be between (0, 1]')

        if 0 < discharge_efficiency <= 1:
            self._discharge_efficiency = discharge_efficiency
        else:
            raise UnitDataLoaderError('storage: discharging efficiency should be between (0, 1]')

    @property
    def charge_efficiency(self):
        return self._charge_efficiency

    @property
    def discharge_efficiency(self):
        return self._discharge_efficiency

    @property
    def initial_energy(self):
        return self._initial_energy

    @property
    def energy_bounds(self):
        return self._energy_bounds

    @initial_energy.setter
    def initial_energy(self, value):
        if self.energy_bounds.min <= value <= self.energy_bounds.max:
            self._initial_energy = value
        else:
            logger.warning("current value is not energy bounds")


class ThermalGeneratorDataLoader(IThermalGeneratorDataLoader):
    def __init__(self, initial_timestamp, power_bounds: Bounds, droop_gain: float,
                 switch_state: bool = False):

        if droop_gain < 0:
            raise UnitDataLoaderError('storage: Droop gain should be positive')
        else:
            super().__init__(initial_timestamp, power_bounds, droop_gain,
                             grid_forming_unit_flag=True)

        self._switch_state = switch_state

    @property
    def switch_state(self):
        return self._switch_state
