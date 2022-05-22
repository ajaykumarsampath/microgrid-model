import logging

from microgrid.data_loader.interface import ILoadDemandDataLoader
from microgrid.shared.component import ComponentSimulationData
from microgrid.model.component_interface import IComponent

logger = logging.getLogger('__name__')


class LoadDemand(IComponent):
    def __init__(self, name: str, data_loader: ILoadDemandDataLoader):

        super().__init__(name, data_loader)
        self._data_loader = data_loader

    def current_simulation_data(self) -> ComponentSimulationData:
        values = {'current_power': self._current_power}
        return ComponentSimulationData(self._name, values=values)

    def step(self, timestamp: int):
        self._check_step_timestamp(timestamp)
        self._current_power = self._data_loader.get_data(timestamp)
