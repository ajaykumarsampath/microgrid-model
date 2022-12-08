from dataclasses import dataclass

from common.model.component import ComponentType
from microgrid.data_loader.component.renewable_unit import RenewableUnitDataLoader
from microgrid.data_loader.domain import SamplePointsToPowerTable
from microgrid.model.component.renewable_unit import RenewablePowerUnit
from microgrid.config.interface import IGeneratorComponentConfig, ComponentConfigRegistryData,\
    ClassImportModuler
from microgrid.shared.data_loader import IComponentDataLoaderData, IGeneratorConfigData
from microgrid.shared.timeseries import SimulationTimeSeries


@dataclass
class RenewableComponentDataLoaderData(IComponentDataLoaderData):
    sample_point_to_power: SamplePointsToPowerTable
    simulation_time_series: SimulationTimeSeries


@dataclass
class RenewableComponentConfigData(IGeneratorConfigData):
    data_loader_data: RenewableComponentDataLoaderData

    def __post_init__(self):
        self.component_type: ComponentType = ComponentType.Renewable


class RenewableUnitConfig(IGeneratorComponentConfig):
    def __init__(self, config_data: RenewableComponentConfigData):
        super().__init__(config_data)
        self.config_data = config_data
        self._component_type = ComponentType.Renewable

    def create_unit(self):
        data_loader = self.create_data_loader()
        return RenewablePowerUnit(self.name, data_loader)

    def create_data_loader(self) -> RenewableUnitDataLoader:
        return RenewableUnitDataLoader(
            self.config_data.initial_timestamp,
            self.config_data.data_loader_data.sample_point_to_power,
            self.config_data.data_loader_data.simulation_time_series)


default_renewable_config_registry = ComponentConfigRegistryData(
    'RENEWABLE_UNIT', ClassImportModuler(
        RenewableUnitConfig.__module__, RenewableUnitConfig.__name__),
    ClassImportModuler(
        RenewableComponentConfigData.__module__, RenewableComponentConfigData.__name__)
)
