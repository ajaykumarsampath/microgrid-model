from data_loader.generator_interface import IGeneratorDataLoader
from model.domain import BUS_ID, ComponentType
from model.component_interface import IComponent, IUnitConfig


class IGeneratorComponent(IComponent):
    def __init__(self, name: str, data_loader: IGeneratorDataLoader):
        super().__init__(name, data_loader)
        self._data_loader = data_loader
        self._power_setpoint = 0
        self._power_sharing = 0
        self._is_grid_forming_unit = data_loader.grid_forming_unit_flag

    def step(self, timestamp: int):
        raise NotImplementedError

    def is_grid_forming_unit(self) -> bool:
        return self._is_grid_forming_unit

    @property
    def power_setpoint(self):
        return self._power_setpoint

    @property
    def droop_gain(self) -> float:
        return self._data_loader.droop_gain

    def droop_gain_inverse(self):
        if self.droop_gain == 0:
            return 0
        else:
            return 1 / self.droop_gain

    @property
    def power_sharing(self):
        return self._power_sharing

    @power_setpoint.setter
    def power_setpoint(self, value: float):
        if self._data_loader.power_bounds.min  <= value <= self._data_loader.power_bounds.max:
            self._power_setpoint = value
        else:
            raise ValueError(f"power set point to set in not satisfying the bounds "
                             f"in the unit {self._name}")

    def participate_power_sharing(self, delta_frequency):
        if self.droop_gain_inverse() > 0:
            self._power_sharing = -delta_frequency * self.droop_gain_inverse()
        else:
            self._power_sharing = 0

class IGeneratorComponentConfig(IUnitConfig):
    def __init__(self, name: str, data_loader: IGeneratorDataLoader, bus_id: BUS_ID):
        super().__init__(name, data_loader, bus_id)

    def create_unit(self) -> IGeneratorComponent:
        raise NotImplementedError