import logging
from dataclasses import dataclass
from typing import List

from data_loader.microgrid_model import MicrogridModelDataLoader
from config.unit import ThermalGeneratorConfig, StoragePowerPlantConfig, \
    RenewableUnitConfig, LoadDemandConfig, GridNetworkConfig

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
    grid_network_config: GridNetworkConfig
    # unit_bus_mapper: List[UNIT_BUS_ID_MAP]


def generate_microgrid_model_data_creator(microgrid_model_config: MicrogridModelConfig):
    data_loader = MicrogridModelDataLoader(microgrid_model_config.name)

    for load_config in microgrid_model_config.load_config:
        data_loader.add_demand_unit(load_config)

    for thermal_config in microgrid_model_config.thermal_generator_config:
        data_loader.add_thermal_power_plant(thermal_config)

    for storage_config in microgrid_model_config.storage_config:
        data_loader.add_storage_power_plant(storage_config)

    for renewable_config in microgrid_model_config.renewable_config:
        data_loader.add_renewable_unit(renewable_config)

    data_loader.add_grid_model(microgrid_model_config.grid_network_config)

    return data_loader


def generate_microgrid_config_from_data_loader(data_loader: MicrogridModelDataLoader):
    microgrid_data = data_loader.microgrid_model_data()
    name = microgrid_data.name

    thermal_generators = data_loader.get_thermal_generators()
    thermal_config = []
    for generator in thermal_generators:
        current_unit_config = ThermalGeneratorConfig(
            generator.name, data_loader=generator.data_loader
        )
        thermal_config.append(current_unit_config)

    storage_power_plants = data_loader.get_storage_power_plants()
    storage_config = []
    for generator in storage_power_plants:
        current_unit_config = StoragePowerPlantConfig(
            generator.name, data_loader=generator.data_loader
        )
        storage_config.append(current_unit_config)

    renewable_units = data_loader.get_renewable_units()
    renewable_config = []
    for generator in renewable_units:
        current_unit_config = RenewableUnitConfig(
            generator.name, data_loader=generator.data_loader
        )
        renewable_config.append(current_unit_config)

    load_demands = data_loader.get_load_demands()
    load_config = []
    for load in load_demands:
        current_unit_config = LoadDemandConfig(
            load.name, data_loader=load.data_loader
        )
        load_config.append(current_unit_config)

    return MicrogridModelConfig(
        name, thermal_config,
    )