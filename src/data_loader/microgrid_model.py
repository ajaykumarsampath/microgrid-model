import logging
from typing import List, Optional

from src.data_loader.domain import DuplicateUnitNameError
from model.domain import BUS_ID, UNIT_BUS_ID_MAP
from model.component_interface import IUnitConfig, IGridNetworkConfig, IComponent, IGridNetwork
from model.generator_interface import IGeneratorComponent, IGeneratorComponentConfig
from model.microgrid_model import MicrogridModelData

logger = logging.getLogger(__name__)


class MicrogridModelDataLoader:
    def __init__(self, name: str):
        self._name = name
        self._generators:List[IGeneratorComponent] = []
        self._loads:List[IComponent] = []
        self._grid_model: Optional[IGridNetwork] = None
        self._generator_bus_ids: List[BUS_ID] = []
        self._load_bus_ids: List[BUS_ID] = []
        self._unit_bus_mapper: List[UNIT_BUS_ID_MAP] = []
        self._thermal_generator_index: List[int] = []
        self._storage_power_plant_index: List[int] = []
        self._renewable_unit_index: List[int] = []


    def microgrid_model_data(self):
        return MicrogridModelData(
            name=self._name,
            generators=self._generators,
            loads=self._loads,
            grid_model=self._grid_model,
            generator_bus_ids=self._generator_bus_ids,
            load_bus_ids=self._load_bus_ids
        )

    def add_demand_unit(self, unit_config: IUnitConfig):
        bus_id = unit_config.bus_id
        current_unit_name = [id for id, bus_id in self._unit_bus_mapper]
        if unit_config.name not in current_unit_name:
            load = unit_config.create_unit()
            self._loads.append(load)
            self._load_bus_ids.append(bus_id)
            self._unit_bus_mapper.append((unit_config.name, bus_id))
        else:
            raise DuplicateUnitNameError(f'{unit_config.name} of the unit must be unique')

    def _add_unit(self, unit_config: IGeneratorComponentConfig):
        bus_id = unit_config.bus_id
        current_unit_name = [id for id, bus_id in self._unit_bus_mapper]
        if unit_config.name not in current_unit_name:
            unit = unit_config.create_unit()
            self._generators.append(unit)
            self._generator_bus_ids.append(bus_id)
            self._unit_bus_mapper.append((unit_config.name, bus_id))
        else:
            raise DuplicateUnitNameError(f'{unit_config.name} of the unit must be unique')

    def add_thermal_power_plant(self, unit_config: IGeneratorComponentConfig):
        current_number_unit = len(self._generators)
        self._add_unit(unit_config)
        self._thermal_generator_index.append(current_number_unit)

    def add_storage_power_plant(self, unit_config: IGeneratorComponentConfig):
        current_number_unit = len(self._generators)
        self._add_unit(unit_config)
        self._storage_power_plant_index.append(current_number_unit)

    def add_renewable_unit(self, unit_config: IGeneratorComponentConfig):
        current_number_unit = len(self._generators)
        self._add_unit(unit_config)
        self._renewable_unit_index.append(current_number_unit)

    def add_grid_model(self, grid_config: IGridNetworkConfig):
        if self._grid_model is not None:
            self._grid_model = grid_config.create_grid_network()
        else:
            logger.warning(f"replacing the grid model of the {self._name}")
            self._grid_model = grid_config.create_grid_network()

    def get_thermal_generators(self) -> List[IGeneratorComponent]:
        return [self._generators[i] for i in self._thermal_generator_index]

    def get_storage_power_plants(self) -> List[IGeneratorComponent]:
        return [self._generators[i] for i in self._storage_power_plant_index]

    def get_renewable_units(self) -> List[IGeneratorComponent]:
        return [self._generators[i] for i in self._renewable_unit_index]

    def get_load_demands(self) -> List[IComponent]:
        return self._loads

    def get_component_bus_id(self, generator_id: str):
        generator_name = [g.name for g in self._generators]
        load_name = [l.name for l in self._loads]
        try:
            if generator_id in generator_name:
                return self._generator_bus_ids[generator_name.index(generator_id)]
            else:
                return self._load_bus_ids[load_name.index(generator_id)]
        except ValueError:
            logger.warning(f'{generator_id} is in the microgrid model')
            return None
