import logging

from data_loader.grid_forming_unit import StoragePowerPlantDataLoader, ThermalGeneratorDataLoader
from model.domain import SEC_TO_HOUR_FACTOR, UnitSimulationData
from model.generator_interface import IGeneratorComponent
from data_loader.generator_interface import IGeneratorDataLoader

logger = logging.getLogger(__name__)



class GridFormingPowerUnit(IGeneratorComponent):
    def __init__(self, name: str, data_loader: IGeneratorDataLoader):
        super().__init__(name, data_loader)
        self._is_grid_forming_unit = True



class StoragePowerPlant(GridFormingPowerUnit):
    def __init__(self, name: str, data_loader: StoragePowerPlantDataLoader):
        super().__init__(name, data_loader)
        self._data_loader = data_loader
        self._current_energy = self._data_loader.initial_energy

    @property
    def charge_efficiency(self):
        return self._data_loader._charge_efficiency

    @property
    def discharge_efficiency(self):
        return self._data_loader._discharge_efficiency

    @property
    def current_energy(self):
        return self._current_energy


    def step(self, timestamp: int):
        prev_timestamp = self.current_timestamp
        self._check_step_timestamp(timestamp)
        time_delta_hrs = (timestamp - prev_timestamp) * SEC_TO_HOUR_FACTOR

        self._current_power = self.power_setpoint + self.power_sharing

        if self.current_power >= 0:
            energy = self.current_energy - time_delta_hrs*(1 / self.discharge_efficiency)*self.current_power
        else:
            energy = self.current_energy - time_delta_hrs * (self.charge_efficiency) * self.current_power

        if energy < self._data_loader.energy_bounds.min or energy > self._data_loader.energy_bounds.max:
            logger.warning(f"energy update in the unit {self._name} violating the energy bounds")

        self._current_energy = energy

    def current_simulation_data(self) -> UnitSimulationData:
        values = {'current_energy': self.current_energy,
                  'power_sharing': self.power_sharing,
                  'power_setpoint': self.power_setpoint,
                  'current_power': self.current_power}

        return UnitSimulationData(self._name, values=values)


class ThermalGenerator(GridFormingPowerUnit):
    def __init(self, name: str, data_loader: ThermalGeneratorDataLoader):

        super().__init__(name, data_loader)
        self._data_loader = data_loader
        self._switch_state = data_loader.switch_state
        self._power_setpoint = 0

    @property
    def switch_state(self):
        return self._switch_state

    @property
    def power_setpoint(self):
        return self._power_setpoint

    @power_setpoint.setter
    def power_setpoint(self, value: float):
        if self._data_loader.power_bounds.min  <= value <= self._data_loader.power_bounds.max:
            self._power_setpoint = value
            self._switch_state = True
        elif value == 0:
            self._power_setpoint = 0
            self._switch_state = False
        else:
            raise ValueError(f"power set point to set in not satisfying the bounds "
                             f"in the unit {self._name}")


    def droop_gain_inverse(self):
        if self.switch_state:
            return 1/self._data_loader.droop_gain
        else:
            return 0

    def step(self, timestamp: int):
        self._check_step_timestamp(timestamp)
        self._current_power = self.power_sharing + self._power_setpoint

    def current_simulation_data(self) -> UnitSimulationData:
        values = {'power_setpoint': self.power_setpoint,
                  'power_sharing': self.power_sharing,
                  'current_power': self.current_power,
                  'switch_state': self.switch_state}

        return UnitSimulationData(name=self._name, values=values)


