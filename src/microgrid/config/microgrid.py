import logging
from dataclasses import dataclass
from typing import List

from microgrid.config.interface import (
    IGridNetworkConfig,
    Reference,
    UnknownComponentConfigType,
)
from microgrid.config.registry import IComponentRegistry
from microgrid.config.component.grid_forming_unit import (
    ThermalGeneratorConfig,
    StoragePowerPlantConfig,
)
from microgrid.config.component.renewable_unit import RenewableUnitConfig
from microgrid.config.component.load_demand import LoadDemandConfig
from microgrid.data_loader.microgrid_model import MicrogridModelDataLoader

logger = logging.getLogger(__name__)


class UnitConfigurationNameBusMapperError(ValueError):
    pass


@dataclass
class MicrogridModelConfig:
    name: str
    thermal_generator_config: List[ThermalGeneratorConfig]
    storage_config: List[StoragePowerPlantConfig]
    renewable_config: List[RenewableUnitConfig]
    load_config: List[LoadDemandConfig]
    grid_network_config: List[IGridNetworkConfig]


class MicrogridModelConfigBuilder:
    def __init__(self, component_registry: IComponentRegistry):
        self.registry = component_registry

    def add_unit_config_data(
        self, microgrid_config: MicrogridModelConfig, reference: Reference, data: dict
    ) -> MicrogridModelConfig:
        config_registry_data = self.registry.get_component_config(reference)
        config = config_registry_data.create_config_class(data)

        if reference in self.registry.get_thermal_config_references():
            microgrid_config.thermal_generator_config.append(config)
        elif reference in self.registry.get_storage_config_references():
            microgrid_config.storage_config.append(config)
        elif reference in self.registry.get_renewable_config_references():
            microgrid_config.renewable_config.append(config)
        elif reference in self.registry.get_load_config_references():
            microgrid_config.load_config.append(config)
        elif reference in self.registry.get_grid_config_references():
            microgrid_config.grid_network_config = [config]
        else:
            raise UnknownComponentConfigType(f"{reference} not in component registry")

        return microgrid_config

    def generate_microgrid_model_data_loader(self, microgrid_config: MicrogridModelConfig) -> MicrogridModelDataLoader:
        data_loader = MicrogridModelDataLoader(microgrid_config.name)

        for load_config in microgrid_config.load_config:
            config_reference = self.registry.get_component_config_reference(load_config)
            data_loader.add_demand_unit(load_config, config_reference)

        for thermal_config in microgrid_config.thermal_generator_config:
            config_reference = self.registry.get_component_config_reference(thermal_config)
            data_loader.add_thermal_power_plant(thermal_config, config_reference)

        for storage_config in microgrid_config.storage_config:
            config_reference = self.registry.get_component_config_reference(storage_config)
            data_loader.add_storage_power_plant(storage_config, config_reference)

        for renewable_config in microgrid_config.renewable_config:
            config_reference = self.registry.get_component_config_reference(renewable_config)
            data_loader.add_renewable_unit(renewable_config, config_reference)

        grid_config = microgrid_config.grid_network_config[0]
        config_reference = self.registry.get_component_config_reference(grid_config)
        data_loader.add_grid_model(grid_config, config_reference)

        return data_loader

    def generate_microgrid_config_from_data_loader(self, data_loader: MicrogridModelDataLoader) -> MicrogridModelConfig:
        microgrid_data = data_loader.microgrid_model_data()
        name = microgrid_data.name

        microgrid_config = MicrogridModelConfig(name, [], [], [], [], [])
        references = data_loader.get_generator_references()

        for reference, bus_id, generator in zip(
            references, microgrid_data.generator_bus_ids, microgrid_data.generators
        ):
            data_ = {
                "name": generator.name,
                "initial_timestamp": generator.get_initial_timestamp(),
                "bus_id": bus_id,
                "data_loader": generator.data_loader,
            }
            microgrid_config = self.add_unit_config_data(microgrid_config, reference, data_)

        references = data_loader.get_load_references()

        for reference, bus_id, load in zip(references, microgrid_data.load_bus_ids, microgrid_data.loads):
            data_ = {
                "name": load.name,
                "initial_timestamp": load.get_initial_timestamp(),
                "bus_id": bus_id,
                "data_loader": load.data_loader,
            }
            microgrid_config = self.add_unit_config_data(microgrid_config, reference, data_)

        grid_reference = data_loader.get_grid_network_references()
        grid = microgrid_data.grid_model

        data_ = {
            "name": grid.name,
            "initial_timestamp": grid.get_initial_timestamp(),
            "data_loader": grid.data_loader,
        }

        microgrid_config = self.add_unit_config_data(microgrid_config, grid_reference[0], data_)

        return microgrid_config
