import logging

from data_loader.load_demand import ILoadDemandDataLoader
from model.domain import UnitSimulationData
from model.component_interface import IComponent

logger = logging.getLogger('__name__')


class LoadDemand(IComponent):
    def __init__(self, name: str, data_loader: ILoadDemandDataLoader):

        super().__init__(name, data_loader)
        self._data_loader = data_loader

    def current_simulation_data(self) -> UnitSimulationData:
        values = {'current_power': self._current_power}
        return UnitSimulationData(self._name, values=values)

    def step(self, timestamp: int):
        self._check_step_timestamp(timestamp)
        self._current_power = self._data_loader.get_data(timestamp)
