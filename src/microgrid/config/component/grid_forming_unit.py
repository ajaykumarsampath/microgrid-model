from dataclasses import dataclass

from microgrid.data_loader.component.grid_forming_unit import StoragePowerPlantDataLoader, \
    ThermalGeneratorDataLoader
from microgrid.model.component.grid_forming_unit import StoragePowerPlant, ThermalGenerator
from microgrid.shared.component import ComponentType, Bounds
from microgrid.config.interface import IGeneratorComponentConfig, ComponentConfigRegistryData, \
    ClassImportModuler
from microgrid.shared.data_loader import IComponentDataLoaderData, IGeneratorConfigData


@dataclass
class StoragePowerPlantDataLoaderData(IComponentDataLoaderData):
    power_bounds: Bounds
    droop_gain: float
    energy_bounds: Bounds
    initial_energy: float = 0
    charge_efficiency: float = 1
    discharge_efficiency: float = 1


@dataclass
class StoragePowerPlantConfigData(IGeneratorConfigData):
    data_loader_data: StoragePowerPlantDataLoaderData

    def __post_init__(self):
        self.component_type = ComponentType.Storage


class StoragePowerPlantConfig(IGeneratorComponentConfig):

    def __init__(self, config_data: StoragePowerPlantConfigData):
        super().__init__(config_data)
        self.config_data = config_data

    def create_unit(self):
        data_loader = self.create_data_loader()
        return StoragePowerPlant(self.name, data_loader)

    def create_data_loader(self) -> StoragePowerPlantDataLoader:
        data_loader_data = self.config_data.data_loader_data
        return StoragePowerPlantDataLoader(
            self.config_data.initial_timestamp, data_loader_data.power_bounds,
            data_loader_data.droop_gain, data_loader_data.energy_bounds,
            data_loader_data.initial_energy, data_loader_data.charge_efficiency,
            data_loader_data.discharge_efficiency
        )


@dataclass
class ThermalGeneratorDataLoaderData(IComponentDataLoaderData):
    power_bounds: Bounds
    droop_gain: float
    switch_state: bool = False


@dataclass
class ThermalGeneratorConfigData(IGeneratorConfigData):
    data_loader_data: ThermalGeneratorDataLoaderData

    def __post_init__(self):
        self.component_type = ComponentType.Thermal


class ThermalGeneratorConfig(IGeneratorComponentConfig):
    def __init__(self, config_data: ThermalGeneratorConfigData):
        super().__init__(config_data)
        self.config_data = config_data

    def create_unit(self):
        data_loader = self.create_data_loader()
        return ThermalGenerator(self.name, data_loader)

    def create_data_loader(self) -> ThermalGeneratorDataLoader:
        return ThermalGeneratorDataLoader(
            self.config_data.initial_timestamp, self.config_data.data_loader_data.power_bounds,
            self.config_data.data_loader_data.droop_gain,
            self.config_data.data_loader_data.switch_state
        )


default_thermal_config_registry = ComponentConfigRegistryData(
    'THERMAL_GENERATOR',
    ClassImportModuler(ThermalGeneratorConfig.__module__, ThermalGeneratorConfig.__name__),
    ClassImportModuler(ThermalGeneratorConfigData.__module__, ThermalGeneratorConfigData.__name__)
)

default_storage_config_registry = ComponentConfigRegistryData(
    'STORAGE_POWERPLANT',
    ClassImportModuler(StoragePowerPlantConfig.__module__, StoragePowerPlantConfig.__name__),
    ClassImportModuler(StoragePowerPlantConfigData.__module__, StoragePowerPlantConfigData.__name__)
)
