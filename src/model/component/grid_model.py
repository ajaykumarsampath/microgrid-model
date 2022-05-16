import logging
from typing import List

from data_loader.interface import IGridNetworkDataLoader
from model.exception import UnknownComponentError, SimulationGridError
from shared.component import ComponentSimulationData, GridLine, BUS_ID
import numpy as np

from model.component_interface import IGridNetwork

logger = logging.getLogger(__name__)


class GridNetwork(IGridNetwork):
    def __init__(self, name: str, data_loader: IGridNetworkDataLoader):
        super().__init__(name, data_loader)
        self._current_power = np.mat([])
        self._data_loader = data_loader
        self._bus_power = np.array([])

        if not data_loader.check_grid_network_connected():
            logger.warning("grid network is not connected and therefore cannot form")
            self._validate_flag = False
        else:
            num_grid_lines = len(self.grid_lines)
            num_buses = len(self.buses)
            self._validate_flag = True
            self._admittance_matrix = self._calculate_admittance_matrix()
            self._dc_power_flow_matrix = self._calculate_dc_power_flow_matrix()
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
        return [line for line in self.grid_lines
                if bus_id == line.to_bus or bus_id == line.from_bus]

    def _calculate_admittance_matrix(self):
        admittance_matrix = np.zeros((len(self.buses), len(self.buses)))
        for count, bus_id in enumerate(self.buses):
            lines = self.get_bus_grid_line(bus_id)
            for line in lines:
                if line.to_bus == bus_id:
                    from_bus_index = self.buses.index(line.from_bus)
                    admittance_matrix[count, from_bus_index] = -line.admittance
                else:
                    to_bus_index = self.buses.index(line.to_bus)
                    admittance_matrix[count, to_bus_index] = -line.admittance

        admittance_matrix = admittance_matrix + \
            np.diag([-admittance_matrix[i, :].sum() for i in range(0, len(self.buses))])
        return admittance_matrix

    def calculate_line_power(self):
        power = self._bus_power
        if len(self.grid_lines) > 0:
            line_power = np.zeros(len(self.grid_lines))

            phase_angle = self._dc_power_flow_matrix @ power.T
            phase_angle[0] = 0

            for count, line in enumerate(self.grid_lines):
                to_bus_index = self.buses.index(line.to_bus)
                from_bus_index = self.buses.index(line.from_bus)
                line_power[count] = line.admittance * \
                    (phase_angle[from_bus_index] - phase_angle[to_bus_index])
            return line_power
        else:
            return np.array([])

    def _calculate_dc_power_flow_matrix(self):
        num_buses = len(self.buses)
        if len(self.grid_lines) > 0:
            dc_power_flow = self._admittance_matrix.copy()
            dc_power_flow[0, :] = np.zeros((1, num_buses))
            dc_power_flow[:, 0] = np.zeros((num_buses,))
            dc_power_flow[0, 0] = 1
            dc_power_flow = np.linalg.inv(dc_power_flow)
            return dc_power_flow
        else:
            return np.array([])

    def step(self, timestamp: int):
        self._check_step_timestamp(timestamp)
        if self.buses_power.sum() == 0 and len(self.buses_power) > 0 \
                and self.validate_grid_model():

            self._current_power = self.calculate_line_power()
        else:
            logger.warning("either bus power not correctly error or the grid model is not complete")
            raise SimulationGridError('either bus power not correctly error or '
                                      'the grid model is not complete')

    def current_simulation_data(self) -> ComponentSimulationData:
        values = {'current_power': self._current_power, 'bus_power': self.buses_power}
        return ComponentSimulationData(name=self._name, values=values)
