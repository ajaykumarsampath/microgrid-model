from dataclasses import dataclass, field

from shared.component import BUS_ID, ComponentType
from shared.timeseries import Timestamp


class IComponentDataLoader:
    def __init__(self, initial_timestamp: Timestamp):
        self._initial_timestamp = initial_timestamp

    @property
    def initial_timestamp(self)  -> Timestamp:
        return self._initial_timestamp


@dataclass
class IComponentDataLoaderData:
    pass


@dataclass
class IUnitConfigData:
    name: str
    initial_timestamp: Timestamp
    data_loader_data: IComponentDataLoaderData
    bus_id: BUS_ID

    def __post_init__(self):
        self.component_type: ComponentType = ComponentType.Unknown

@dataclass
class IGeneratorConfigData(IUnitConfigData):
    pass

@dataclass
class IGridNetworkConfigData:
    name: str
    initial_timestamp: Timestamp
    data_loader_data: IComponentDataLoaderData

    def __post_init__(self):
        self.component_type: ComponentType = ComponentType.Grid
