from common.model.component import ComponentType, ControlComponentData, GridControlComponentData, BUS_ID
from microgrid.model.exception import StepPreviousTimestamp
from microgrid.shared.simulation_data import ComponentSimulationData
from microgrid.shared.data_loader import IComponentDataLoader
from microgrid.shared.storage import IComponentDataStorage
from microgrid.shared.timeseries import Timestamp


class IComponent:
    def __init__(self, name: str, data_loader: IComponentDataLoader):
        self._name = name
        self._data_loader = data_loader
        self._current_power = 0
        self._current_timestamp: Timestamp = self._data_loader.initial_timestamp
        self._component_type = ComponentType.Unknown

    @property
    def name(self):
        return self._name

    @property
    def data_loader(self):
        return self._data_loader

    @property
    def component_type(self) -> ComponentType:
        return self._component_type

    def step(self, timestamp: int):
        raise NotImplementedError

    @property
    def control_component_data(self) -> ControlComponentData:
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
    def control_component_data(self) -> GridControlComponentData:
        raise NotImplementedError

    @property
    def buses(self):
        raise NotImplementedError

    def validate_grid_model(self) -> bool:
        raise NotImplementedError

    def set_bus_power(self, bus_id: BUS_ID, power: float):
        raise NotImplementedError
