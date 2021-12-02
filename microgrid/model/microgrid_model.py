import logging
from dataclasses import dataclass
from typing import List, Union, Optional
import numpy as np

from microgrid.model.grid_model import GridModel, BUS_ID, GridLine
from microgrid.model.power_unit import PowerUnit, Unit

logger = logging.getLogger(__name__)


@dataclass
class MicrogridModelData:
    generators: List[PowerUnit]
    loads: List[Unit]
    grid_model: Optional[GridModel]
    generator_bus_ids: List[BUS_ID]
    load_bus_ids: List[BUS_ID]

    def validate_date(self):
        try:
            assert len(self.generators) == len(self.generator_bus_ids)
            assert len(self.loads) == len(self.load_bus_ids)
            if self.grid_model is not None:
                assert set(self.generator_bus_ids) == set(self.load_bus_ids) == 1
            else:
                buses = self.grid_model.buses()
                assert all([b in buses for b in self.generator_bus_ids])
                assert all([b in buses for b in self.load_bus_ids])

        except AssertionError:
            logger.warning("Microgrid data is not accurate")
            return False


class MicrogridModel:
    def __init__(self, name: str, initial_timestamp:int, microgrid_model_data: MicrogridModelData = None):
        self.name = name
        self.initial_timestamp = initial_timestamp
        if microgrid_model_data is None:
            self.generators = []
            self.loads = []
            self._unit_to_bus = np.mat([])
            self.generator_bus_ids = []
            self.load_bus_ids = []
        else:
            if microgrid_model_data.validate_date():
                self.generators = microgrid_model_data.generators
                self.loads = microgrid_model_data.loads
                self.grid_model = microgrid_model_data.grid_model
                self.generator_bus_ids = microgrid_model_data.generator_bus_ids
                self.load_bus_ids = microgrid_model_data.load_bus_ids
                self._unit_to_bus = self._calculate_unit_bus_matrix()

        self.__validate_flag = False

    @property
    def unit_to_bus_matrix(self):
        return self._unit_to_bus

    def set_power_setpoints(self, power_setpoints: List[float]):
        assert len(power_setpoints) == len(self.generators)
        for power, unit in zip(power_setpoints, self.generators):
            unit.power_setpoint(power)

    def current_power(self) -> np.array:
        num_generators = len(self.generator_bus_ids)
        num_loads = len(self.load_bus_ids)
        power = np.zeros(num_generators + num_loads)

        for count, unit in self.generators:
            power[count] = unit.current_power

        for count, unit in self.loads:
            power[num_generators + count] = unit.current_power

        return power


    def step(self, timestamp: int):
        for unit in self.generators:
            if not unit.is_grid_forming_unit():
                unit.step(timestamp=timestamp)

    def add_demand_unit(self, unit: Unit, bus_id: BUS_ID):
        self.loads.append(unit)
        self.load_bus_ids.append(bus_id)
        self._calculate_unit_bus_matrix()
        self.__validate_flag = False

    def add_power_unit(self, power_unit: PowerUnit, bus_id: BUS_ID):
        self.generators.append(power_unit)
        self.generator_bus_ids.append(bus_id)
        self._calculate_unit_bus_matrix()
        self.__validate_flag = False

    def add_powerline(self, grid_line: GridLine):
        self.grid_model.add_powerline(grid_line)
        self.__validate_flag = False

    def _calculate_unit_bus_matrix(self):
        if len(self._unit_to_bus) == 0:
            unique_buses = list(set(self.generator_bus_ids + self.load_bus_ids))
            num_generators = len(self.generator_bus_ids)
            num_loads = len(self.load_bus_ids)
            cols_unit_bus_mat = len(unique_buses)
            self._unit_bus_mat = np.zeros((num_generators + num_loads, cols_unit_bus_mat))

            for count, bus_id in enumerate(self.generator_bus_ids):
                bus_id_index = unique_buses.index(bus_id)
                self._unit_to_bus[count, bus_id_index] = 1

            for count, bus_id in enumerate(self.load_bus_ids):
                bus_id_index = unique_buses.index(bus_id)
                self._unit_to_bus[count + num_generators, bus_id_index] = 1


    def _convert_unit_power_bus_power(self):
        return self.unit_to_bus@self.current_power()

    def __validate_model(self):
        model_buses = list(set(self.generator_bus_ids + self.load_bus_ids))
        if len(model_buses) > 1:
            grid_buses = self.grid_model.buses()
            try:
                assert len(grid_buses) == len(model_buses)
                assert all([bus in model_buses for bus in grid_buses])
                return self.grid_model.validate_grid_model()
            except AssertionError:
                return False
        else:
            return True
