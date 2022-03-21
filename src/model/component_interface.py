from model.domain import BUS_ID, StepPreviousTimestamp, UnitSimulationData, ComponentType
from src.utils.storage import IUnitDataStorage

class IComponentDataLoader:
    def __init__(self, initial_timestamp: int):
        self._initial_timestamp = initial_timestamp

    @property
    def initial_timestamp(self)  -> int:
        return self._initial_timestamp


class IComponent:
    def __init__(self, name: str, data_loader: IComponentDataLoader):
        self._name = name
        self._data_loader = data_loader
        self._current_power = 0
        self._current_timestamp = self._data_loader.initial_timestamp

    @property
    def name(self):
        return self._name

    @property
    def data_loader(self):
        return self._data_loader

    def step(self, timestamp: int):
        raise NotImplementedError

    @property
    def current_power(self):
        return self._current_power

    def get_initial_timestamp(self):
        return self._data_loader.initial_timestamp

    @property
    def current_timestamp(self):
        return self._current_timestamp

    def add_simulation_data(self, data_storage: IUnitDataStorage):
        data = self.current_simulation_data()
        data_storage.add_simulation_data(
            current_timestamp=self._current_timestamp, data=data
        )

    def _check_step_timestamp(self, timestamp: int):
        if timestamp <= self._current_timestamp:
            raise StepPreviousTimestamp('Cannot step to past timestamp than current timestamp')
        self._current_timestamp = timestamp

    def current_simulation_data(self) -> UnitSimulationData:
        raise NotImplementedError

    def get_simulation_data(self, timestamp: int, data_storage: IUnitDataStorage):
        data_storage.get_historical_data(self._name, since=timestamp)

class IGridNetwork(IComponent):
    @property
    def buses(self):
        raise NotImplementedError

    def validate_grid_model(self) -> bool:
        raise NotImplementedError

    def set_bus_power(self, bus_id: BUS_ID, power: float):
        raise NotImplementedError

class IUnitConfig:
    def __init__(self, name: str, data_loader: IComponentDataLoader, bus_id: BUS_ID):
        self.name = name
        self.data_loader = data_loader
        self.bus_id = bus_id
        self._component_type = ComponentType.Unknown

    @property
    def component_type(self) -> ComponentType:
        return self._component_type

    def create_unit(self) -> IComponent:
        raise NotImplementedError


class IGridNetworkConfig:
    def __init__(self, name: str, data_loader: IComponentDataLoader):
        self.name = name
        self.data_loader = data_loader
        self._component_type = ComponentType.Unknown

    @property
    def component_type(self) -> ComponentType:
        return self._component_type

    def create_grid_network(self) -> IGridNetwork:
       raise NotImplementedError
