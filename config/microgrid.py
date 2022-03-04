import logging
from dataclasses import dataclass
from typing import List

from data_loader.microgrid_model import MicrogridModelDataLoader
from model.config.unit import ThermalGeneratorConfig, StoragePowerPlantConfig, \
    RenewableUnitConfig, LoadDemandConfig, GridNetworkConfig
from model.domain import UNIT_BUS_ID_MAP

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
    unit_bus_mapper: List[UNIT_BUS_ID_MAP]


def generate_microgrid_model_config(microgrid_model_config: MicrogridModelConfig):
    microgrid_model_data_creator = MicrogridModelDataLoader(microgrid_model_config.name)
    unit_names = [unit_bus_id[0] for unit_bus_id in microgrid_model_config.unit_bus_mapper]
    for load_config in microgrid_model_config.load_config:
        try:
            unit_name_index = unit_names.index(load_config.name)
            bus_id = microgrid_model_config.unit_bus_mapper[unit_name_index][1]
            microgrid_model_data_creator.add_demand_unit(load_config)
        except UnitConfigurationNameBusMapperError:
            raise UnitConfigurationNameBusMapperError(
                f'Configuration error for the load in MG {microgrid_model_config.name}')

    for thermal_config in microgrid_model_config.thermal_generator_config:
        try:
            unit_name_index = unit_names.index(thermal_config.name)
            bus_id = microgrid_model_config.unit_bus_mapper[unit_name_index][1]
            microgrid_model_data_creator.add_thermal_power_plant(thermal_config)
        except UnitConfigurationNameBusMapperError:
            raise UnitConfigurationNameBusMapperError(
                f'Configuration error for thermal unit config in MG {microgrid_model_config.name}')

    for storage_config in microgrid_model_config.storage_config:
        try:
            unit_name_index = unit_names.index(storage_config.name)
            bus_id = microgrid_model_config.unit_bus_mapper[unit_name_index][1]
            microgrid_model_data_creator.add_storage_power_plant(storage_config)
        except UnitConfigurationNameBusMapperError:
            raise UnitConfigurationNameBusMapperError(
                f'Configuration error for storage unit config in MG {microgrid_model_config.name}')

    for renewable_config in microgrid_model_config.renewable_config:
        try:
            unit_name_index = unit_names.index(renewable_config.name)
            bus_id = microgrid_model_config.unit_bus_mapper[unit_name_index][1]
            microgrid_model_data_creator.add_storage_power_plant(renewable_config)
        except UnitConfigurationNameBusMapperError:
            raise UnitConfigurationNameBusMapperError(
                f'Configuration error for renewable unit config in MG {microgrid_model_config.name}')
