from dataclasses import dataclass

from common.model.component import BUS_ID, ComponentType
from microgrid.data_loader.component.load_demand import LoadDemandDataLoader
from microgrid.model.component.load_demand import LoadDemand
from microgrid.config.interface import IUnitConfig, ComponentConfigRegistryData, ClassImportModuler
from microgrid.shared.data_loader import IUnitConfigData, IComponentDataLoaderData
from microgrid.shared.timeseries import SimulationTimeSeries, Timestamp

"""
@dataclass
class ILoadDemandDataLoaderData(IComponentDataLoaderData):
    pass

@dataclass
class ILoadDemandConfigData(IUnitConfigData):
    initial_timestamp: Timestamp
    name: str
    data_loader_data: ILoadDemandDataLoaderData
    bus_id: BUS_ID
"""


@dataclass
class LoadDemandDataLoaderData(IComponentDataLoaderData):
    demand_time_series: SimulationTimeSeries


@dataclass
class LoadDemandConfigData(IUnitConfigData):
    initial_timestamp: Timestamp
    name: str
    data_loader_data: LoadDemandDataLoaderData
    bus_id: BUS_ID


class LoadDemandConfig(IUnitConfig):
    def __init__(self, config_data: LoadDemandConfigData):
        super().__init__(config_data)
        self.initial_timestamp = config_data.initial_timestamp
        self._component_type = ComponentType.Load

    def create_unit(self) -> LoadDemand:
        data_loader = self.create_data_loader()
        return LoadDemand(self.name, data_loader)

    def create_data_loader(self) -> LoadDemandDataLoader:
        return LoadDemandDataLoader(
            self.initial_timestamp, self.data_loader_data.demand_time_series
        )


default_load_config_registry = ComponentConfigRegistryData(
    'LOAD_DEMAND', ClassImportModuler(LoadDemandConfig.__module__, LoadDemandConfig.__name__),
    ClassImportModuler(LoadDemandConfigData.__module__, LoadDemandConfigData.__name__)
)
