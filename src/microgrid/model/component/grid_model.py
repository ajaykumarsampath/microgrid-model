import logging
from typing import List

from common.model.component import (
    ComponentType,
    GridLine,
    GridControlComponentData,
    BUS_ID,
)
from microgrid.data_loader.interface import IGridNetworkDataLoader
from microgrid.model.exception import UnknownComponentError, SimulationGridError
from microgrid.shared.simulation_data import ComponentSimulationData
import numpy as np

from microgrid.model.component_interface import IGridNetwork
from common.model.grid_network_util import GridNetworkUtils

logger = logging.getLogger(__name__)


class GridNetwork(IGridNetwork):
    def __init__(self, name: str, data_loader: IGridNetworkDataLoader):
        super().__init__(name, data_loader)
        self._current_power = np.mat([])
        self._data_loader = data_loader
        self._bus_power = np.array([])
        self._component_type = ComponentType.Grid
        if not data_loader.check_grid_network_connected():
            logger.warning("grid network is not connected and therefore cannot form")
            self._validate_flag = False
        else:
            self._validate_flag = True
            num_grid_lines = len(self.grid_lines)
            num_buses = len(self.buses)
            self._admittance_matrix = GridNetworkUtils.calculate_admittance_matrix(self.buses, self.grid_lines)
            self._dc_power_flow_matrix = GridNetworkUtils.calculate_dc_power_flow_matrix(self.buses, self.grid_lines)
            self._current_power = np.zeros(num_grid_lines)
            self._data_loader = data_loader
            self._bus_power = np.zeros(num_buses)

    @property
    def data_loader(self):
        return self._data_loader

    @property
    def buses(self):
        return self._data_loader.buses()

    @property
    def grid_lines(self) -> List[GridLine]:
        return self._data_loader.grid_lines

    @property
    def control_component_data(self) -> GridControlComponentData:
        return GridControlComponentData(
            name=self.name,
            component_type=self.component_type,
            grid_lines=self.grid_lines,
        )

    @property
    def admittance_matrix(self) -> np.mat:
        return self._admittance_matrix

    @property
    def dc_power_flow_matrix(self) -> np.mat:
        return self._dc_power_flow_matrix

    def validate_grid_model(self) -> bool:
        return self._validate_flag

    @property
    def buses_power(self):
        return self._bus_power

    def set_bus_power(self, bus_id: BUS_ID, power: float):
        try:
            self._bus_power[self.buses.index(bus_id)] = power
        except Exception:
            raise UnknownComponentError("Bus id not in the grid model")

    def get_bus_neighbours(self, bus_id: BUS_ID):
        neighbour_ids = []
        for line in self.grid_lines:
            if bus_id == line.to_bus:
                neighbour_ids.append(line.from_bus)
            elif bus_id == line.from_bus:
                neighbour_ids.append(line.to_bus)

        return list(set(neighbour_ids))

    def get_bus_grid_line(self, bus_id: BUS_ID) -> List[GridLine]:
        return [line for line in self.grid_lines if line.is_connected_to_bus(bus_id)]

    def calculate_line_power(self):
        power = self._bus_power
        if len(self.grid_lines) > 0:
            line_power = np.zeros(len(self.grid_lines))

            phase_angle = self._dc_power_flow_matrix @ power.T
            phase_angle[0] = 0

            for count, line in enumerate(self.grid_lines):
                to_bus_index = self.buses.index(line.to_bus)
                from_bus_index = self.buses.index(line.from_bus)
                line_power[count] = line.admittance * (phase_angle[from_bus_index] - phase_angle[to_bus_index])
            return line_power
        else:
            return np.array([])

    def step(self, timestamp: int):
        self._check_step_timestamp(timestamp)
        if self.buses_power.sum() == 0 and len(self.buses_power) > 0 and self.validate_grid_model():

            self._current_power = self.calculate_line_power()
        else:
            logger.warning("either bus power not correctly error or the grid model is not complete")
            raise SimulationGridError("either bus power not correctly error or " "the grid model is not complete")

    def current_simulation_data(self) -> ComponentSimulationData:
        values = {"current_power": self._current_power, "bus_power": self.buses_power}
        return ComponentSimulationData(name=self._name, values=values)
