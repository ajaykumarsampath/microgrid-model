from dataclasses import dataclass
from typing import List

from microgrid.data_loader.component.grid_model import SingleBusGridNetworkDataLoader, GridNetworkDataLoader
from microgrid.model.component.grid_model import GridNetwork
from microgrid.config.interface import IGridNetworkConfig, ComponentConfigRegistryData, ClassImportModuler
from microgrid.shared.component import ComponentType, GridLine
from microgrid.shared.data_loader import IComponentDataLoaderData, IGridNetworkConfigData
from microgrid.shared.timeseries import Timestamp


@dataclass
class SingleGridNetworkDataLoaderData(IComponentDataLoaderData):
    pass


@dataclass
class GridNetworkDataLoaderData(IComponentDataLoaderData):
    grid_lines: List[GridLine]


@dataclass
class SingleGridNetworkConfigData(IGridNetworkConfigData):
    name: str
    initial_timestamp: Timestamp
    data_loader_data: SingleGridNetworkDataLoaderData


@dataclass
class GridNetworkConfigData(IGridNetworkConfigData):
    name: str
    initial_timestamp: Timestamp
    data_loader_data: GridNetworkDataLoaderData

    def __post_init__(self):
        self.component_type = ComponentType.Grid


class SingleGridNetworkConfig(IGridNetworkConfig):
    def __init__(self, config_data: SingleGridNetworkConfigData):
        super().__init__(config_data)

    @property
    def name(self):
        return self.config_data.name

    def create_grid_network(self) -> GridNetwork:
        data_loader = self.create_data_loader()
        return GridNetwork(self.name, data_loader)

    def create_data_loader(self) -> SingleBusGridNetworkDataLoader:
        return SingleBusGridNetworkDataLoader(self.config_data.initial_timestamp)


class GridNetworkConfig(IGridNetworkConfig):
    def __init__(self, config_data: GridNetworkConfigData):
        super().__init__(config_data)
        self.config_data = config_data

    @property
    def name(self):
        return self.config_data.name

    def create_grid_network(self) -> GridNetwork:
        data_loader = self.create_data_loader()
        return GridNetwork(self.name, data_loader)

    def create_data_loader(self) -> GridNetworkDataLoader:
        return GridNetworkDataLoader(
            self.config_data.initial_timestamp, self.config_data.data_loader_data.grid_lines
        )


default_single_grid_network_registry = ComponentConfigRegistryData(
    'SINGLE_GRID_NETWORK',
    ClassImportModuler(SingleGridNetworkConfig.__module__, SingleGridNetworkConfig.__name__),
    ClassImportModuler(SingleGridNetworkConfigData.__module__, SingleGridNetworkConfigData.__name__)
)

default_grid_network_registry = ComponentConfigRegistryData(
    'GRID_NETWORK',
    ClassImportModuler(GridNetworkConfig.__module__, GridNetworkConfig.__name__),
    ClassImportModuler(GridNetworkConfigData.__module__, GridNetworkConfigData.__name__)
)
