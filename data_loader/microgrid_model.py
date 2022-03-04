import logging
from typing import List, Optional

from data_loader.domain import DuplicateUnitNameError
from model.domain import BUS_ID, UNIT_BUS_ID_MAP
from model.grid_model import GridNetwork
from model.component_interface import IUnitConfig, IGridNetworkConfig, IComponent
from model.generator_interface import IGeneratorComponent, IGeneratorComponentConfig
from model.microgrid_model import MicrogridModelData

logger = logging.getLogger(__name__)


class MicrogridModelDataLoader:
    def __init__(self, name: str):
        self._name = name
        self._generators:List[IGeneratorComponent] = []
        self._loads:List[IComponent] = []
        self._grid_model: Optional[GridNetwork] = None
        self._generator_bus_ids: List[BUS_ID] = []
        self._load_bus_ids: List[BUS_ID] = []
        self._unit_bus_mapper: List[UNIT_BUS_ID_MAP] = []
        self._thermal_generator_index: List[int] = []
        self._storage_power_plant_index: List[int] = []
        self._renewable_unit_index: List[int] = []
        # self._grid_model_data: Optional[GridNetworkDataLoader] = None


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
        self._thermal_generator_index.append(current_number_unit + 1)

    def add_storage_power_plant(self, unit_config: IGeneratorComponentConfig):
        current_number_unit = len(self._generators)
        self._add_unit(unit_config)
        self._storage_power_plant_index.append(current_number_unit + 1)

    def add_renewable_unit(self, unit_config: IGeneratorComponentConfig):
        current_number_unit = len(self._generators)
        self._add_unit(unit_config)
        self._renewable_unit_index.append(current_number_unit + 1)

    def add_grid_model(self, grid_config: IGridNetworkConfig):
        if self._grid_model is not None:
            self._grid_model = grid_config.create_grid_network()
        else:
            logger.warning(f"replacing the grid model of the {self._name}")
            self._grid_model = grid_config.create_grid_network()

    def get_thermal_generators(self) -> Optional[List[IGeneratorComponent]]:
        if len(self._thermal_generator_index) > 0:
            return [self._generators[i] for i in self._thermal_generator_index]
        else:
            return None

    def get_storage_power_plants(self) -> Optional[List[IGeneratorComponent]]:
        if len(self._storage_power_plant_index) > 0:
            return [self._generators[i] for i in self._storage_power_plant_index]
        else:
            return None

    def get_renewable_units(self) -> Optional[List[IGeneratorComponent]]:
        if len(self._renewable_unit_index) > 0:
            return [self._generators[i] for i in self._renewable_unit_index]
        else:
            return None

    def get_load_demands(self) -> Optional[List[IComponent]]:
        if len(self._loads) > 0:
            return self._loads
        else:
            return None


    def get_unit_bus_id(self, unit: IComponent):
        generator_name = [g.name for g in self._generators]
        load_name = [l.name for l in self._loads]
        if unit.name in generator_name:
            return self._generators[generator_name.index(unit.name)]
        elif unit.name in load_name :
            return self._generators[generator_name.index(unit.name)]
        else:
            return None