from model.exception import StepPreviousTimestamp
from shared.component import BUS_ID, ComponentSimulationData
from shared.data_loader import IComponentDataLoader
from shared.storage import IComponentDataStorage


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

    def add_simulation_data(self, data_storage: IComponentDataStorage):
        data = self.current_simulation_data()
        data_storage.add_simulation_data(
            current_timestamp=self._current_timestamp, data=data
        )

    def _check_step_timestamp(self, timestamp: int):
        if timestamp <= self._current_timestamp:
            raise StepPreviousTimestamp('Cannot step to past timestamp than current timestamp')
        self._current_timestamp = timestamp

    def current_simulation_data(self) -> ComponentSimulationData:
        raise NotImplementedError

    def get_simulation_data(self, timestamp: int, data_storage: IComponentDataStorage):
        data_storage.get_historical_data(self._name, since=timestamp)


class IGridNetwork(IComponent):
    @property
    def buses(self):
        raise NotImplementedError

    def validate_grid_model(self) -> bool:
        raise NotImplementedError

    def set_bus_power(self, bus_id: BUS_ID, power: float):
        raise NotImplementedError
