import logging

from microgrid.model.domain import Bounds, SEC_TO_HOUR_FACTOR, UnitSimulationData
from microgrid.model.power_unit import PowerUnit

logger = logging.getLogger(__name__)


class GridFormingPowerUnit(PowerUnit):
    def __init__(self, name: str, initial_timestamp: int, power_bounds: Bounds, droop_gain: float):
        super().__init__(name, initial_timestamp, power_bounds)
        self._droop_gain = droop_gain

    @property
    def droop_gain(self):
        return self._droop_gain

    def is_grid_forming_unit(self) -> bool:
        return True

    """
    def step(self, timestamp: int, current_power: float, unit_enable: bool = True):
        if unit_enable == True:
            if self.power_bounds.min <= current_power <= self.power_bounds.max:
                logger.warning("current power does not satisfy the power bounds of the unit")
            self._current_power = 0
        else:
            self._current_power = 0
    """

    def unit_power_sharing(self, power_delta: float, power_sharing_factor: float):
        return power_delta


class StoragePowerPlant(GridFormingPowerUnit):
    def __init(self, name: str, initial_timestamp: int, power_bounds: Bounds, droop_gain: float,
               energy_bounds: Bounds, current_energy: float = 0,
               charge_efficiency: float = 1, discharge_efficiency: float=1):

        super().__init__(name, initial_timestamp, power_bounds, droop_gain)
        self.energy_bounds = energy_bounds
        self._current_energy = current_energy
        self._charge_efficiency = charge_efficiency
        self._discharge_efficiency = discharge_efficiency
        self._add_simulation_data(timestamp=initial_timestamp,
                                  data=self._generate_simulation_data())

    @property
    def charge_efficiency(self):
        return self._charge_efficiency

    @property
    def discharge_efficiency(self):
        return self._discharge_efficiency

    @property
    def current_energy(self):
        return self._current_energy

    def step(self, timestamp: int):
        prev_timestamp = self.current_timestamp()
        time_delta_hrs = (timestamp - prev_timestamp) * SEC_TO_HOUR_FACTOR
        if self.current_power >= 0:
            energy = self.current_energy - time_delta_hrs*(1 / self.discharge_efficiency)*self.current_power
        else:
            energy = self.current_energy + time_delta_hrs * (self.charge_efficiency) * self.current_power

        if energy < self.energy_bounds.min or energy > self.energy_bounds.max:
            logger.warning(f"energy update in the unit {self.name} violating the energy bounds")

        self._add_simulation_data(timestamp=timestamp,
                                  data = self._generate_simulation_data())

    def _generate_simulation_data(self) -> UnitSimulationData:
        values = {'current_energy': self.current_energy,
                  'power_setpoint': self.power_setpoint,
                  'current_power': self.current_power}

        return UnitSimulationData(values=values)



class ThermalGenerator(GridFormingPowerUnit):
    def __init(self, name: str, initial_timestamp: int, power_bounds: Bounds, droop_gain: float,
               switch_state: bool = False):

        super().__init__(name, initial_timestamp, power_bounds, droop_gain)
        self._switch_state = switch_state
        self._add_simulation_data(timestamp=initial_timestamp,
                                  data=self._generate_simulation_data())

    @property
    def switch_state(self):
        return self._switch_state

    @switch_state.setter
    def switch_state(self, value: bool):
        self._switch_state = value

    def step(self, timestamp: int):
        self._add_simulation_data(timestamp=timestamp, data= self._generate_simulation_data())

    def _generate_simulation_data(self) -> UnitSimulationData:
        values = {'power_setpoint': self.power_setpoint,
                  'current_power': self.current_power,
                  'switch_state': self.switch_state}

        return UnitSimulationData(values=values)
