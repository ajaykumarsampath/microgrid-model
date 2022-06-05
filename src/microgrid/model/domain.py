from dataclasses import dataclass
from functools import cached_property
from typing import List

import numpy as np

from microgrid.model.component_interface import IComponent, IGridNetwork
from microgrid.model.generator_interface import IGeneratorComponent
from microgrid.shared.component import BUS_ID

UNIT_BUS_ID_MAP = [str, BUS_ID]
SEC_TO_HOUR_FACTOR = 1 / 3600


@dataclass(frozen=True)
class MicrogridModelData:
    name: str
    generators: List[IGeneratorComponent]
    loads: List[IComponent]
    grid_model: IGridNetwork
    generator_bus_ids: List[BUS_ID]
    load_bus_ids: List[BUS_ID]

    @cached_property
    def model_bus_ids(self) -> List[BUS_ID]:
        unique_bus = []
        for i, e in enumerate(self.generator_bus_ids + self.load_bus_ids):
            if e not in unique_bus:
                unique_bus.append(e)
        return unique_bus

    @cached_property
    def valid_data(self):
        grid_buses = self.grid_model.buses
        try:
            self._check_non_unique_ids(self.generators)
            self._check_non_unique_ids(self.loads)
            assert len(self.generators) == len(self.generator_bus_ids)
            assert len(self.loads) == len(self.load_bus_ids)
            assert len(grid_buses) == len(self.model_bus_ids)
            assert all([bus in self.model_bus_ids for bus in grid_buses])
            return self.grid_model.validate_grid_model()
        except AssertionError:
            return False

    def _check_non_unique_ids(self, components: List[IComponent]):
        component_names = [c.name for c in components]
        assert len(component_names) == len(set(component_names))

    def unit_bus_matrix(self):
        num_generators = len(self.generator_bus_ids)
        num_loads = len(self.load_bus_ids)
        cols_unit_bus_mat = len(self.model_bus_ids)
        _unit_bus_mat = np.zeros((num_generators + num_loads, cols_unit_bus_mat))

        for count, bus_id in enumerate(self.generator_bus_ids):
            bus_id_index = self.model_bus_ids.index(bus_id)
            _unit_bus_mat[count, bus_id_index] = 1

        for count, bus_id in enumerate(self.load_bus_ids):
            bus_id_index = self.model_bus_ids.index(bus_id)
            _unit_bus_mat[count + num_generators, bus_id_index] = 1

        return _unit_bus_mat
