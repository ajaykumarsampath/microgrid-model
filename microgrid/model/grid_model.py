import logging
from dataclasses import dataclass, field
from typing import List, Tuple, Dict, Optional

from microgrid.model.domain import Bounds, UnitSimulationData
from microgrid.model.power_unit import UnitDataStorage
import numpy as np

logger = logging.getLogger(__name__)


BUS_ID = str
GRID_LINE = Tuple[BUS_ID, BUS_ID, float]

@dataclass
class GridLine:
    from_bus: BUS_ID
    to_bus: BUS_ID
    admittance: Optional[float] = field(default=None)
    bounds: Optional[Bounds] = field(default=None)


class GridModelData:
    def __init__(self, grid_line: List[GridLine]):
        self.grid_lines = grid_line

    def validate_model_data(self) -> bool:
        if len(self.grid_lines) > 0:
            assert all([line.from_bus != line.to_bus for line in self.grid_lines])
            return True
        else:
            return False

    def add_grid_line(self, grid_line: GridLine):
        if self._validate_grid_line(grid_line):
            self.grid_lines.append(grid_line)
        else:
            logger.warning("Line cannot be added either the line already exists")

    def _validate_grid_line(self, grid_line: GridLine) -> bool:
        bus_1 = grid_line.from_bus
        bus_2 = grid_line.to_bus
        if bus_1 == bus_2:
            return False
        else:
            for line in self.grid_lines:
                if bus_1 in [line.to_bus, line.from_bus] and bus_2 in [line.to_bus, line.from_bus]:
                    return False
            return True

    def buses(self):
        bus = []
        bus.extend([line.to_bus for line in self.grid_lines])
        bus.extend([line.from_bus for line in self.grid_lines])
        return list(set(bus))



class ValidateGridModel:
    def _check_grid_model_connected(self, grid_lines: List[GridLine]) -> bool:
        bus_set = []
        for line in grid_lines:
            bus_set = self._update_bus_set(line, bus_set)

        if len(bus_set) == 1:
            return True
        else:
            return False

    def _update_bus_set(self, line: GridLine, list_set_buses: List):
        if len(list_set_buses) == 0:
            list_set_buses.append([line.to_bus, line.from_bus])
        else:
            to_bus_set_flag = [True if line.to_bus in s else False for s in list_set_buses]
            from_bus_set_flag = [True if line.from_bus in s else False for s in list_set_buses]

            num_to_bus_set = sum(to_bus_set_flag)
            num_from_bus_set = sum(from_bus_set_flag)

            if num_to_bus_set == 0 and num_from_bus_set == 0:
                list_set_buses.append([line.to_bus, line.from_bus])
            elif num_to_bus_set == 1 and num_from_bus_set == 0:
                bus_set_index = to_bus_set_flag.index(True)
                list_set_buses[bus_set_index].extend([line.from_bus])
            elif num_to_bus_set == 0 and num_from_bus_set == 1:
                bus_set_index = from_bus_set_flag.index(True)
                list_set_buses[bus_set_index].extend([line.to_bus])
            elif num_to_bus_set == 1 and num_from_bus_set == 1:
                to_bus_set_index = to_bus_set_flag.index(True)
                from_bus_set_index = from_bus_set_flag.index(True)
                if to_bus_set_index == from_bus_set_index:
                    logger.warning(f"duplicate line {line}")
                else:
                    from_bus_set = list_set_buses.pop(from_bus_set_index)
                    list_set_buses[to_bus_set_index] = list_set_buses[to_bus_set_index] \
                                                       + from_bus_set

        return list_set_buses

    def _validate_grid_line(self, grid_lines: GridLine, current_line: GridLine) -> bool:
        if current_line.from_bus == current_line.to_bus:
            return False
        else:
            return all([line == current_line for line in grid_lines])


class GridModel:
    def __init__(self, name: str, initial_timestamp: int, grid_model_data: GridModelData):
        self.name = name
        self._storage = UnitDataStorage(initial_timestamp)
        self._validate_grid_model = ValidateGridModel()

        if grid_model_data.validate_model_data() == True:
            self._grid_lines = grid_model_data.grid_lines
            self._buses = grid_model_data.buses()
            self._grid_connected = self.is_grid_connected()
            self._calculate_admittance_matrix()
            self._calculate_dc_power_flow_matrix()
        else:
            self._grid_lines = np.array([])
            self._adjacency_matrix = np.mat([])
            self._buses = []
            self._grid_connected = False
            self._admittance_matrix = np.mat([])
            self._dc_power_flow_matrix = np.mat([])

    def buses(self):
        return self._buses

    @property
    def grid_lines(self):
        return self._grid_lines

    @property
    def admittance_matrix(self) -> np.mat:
        return self._admittance_matrix

    def is_grid_connected(self) -> bool:
        return self._grid_connected

    def add_powerline(self, grid_line: GridLine):
        if self._validate_grid_model._validate_grid_line(self.grid_lines, grid_line):
            self._grid_lines.append(grid_line)
            self._update_buses(grid_line)
            self._check_grid_model_connected()
            self._calculate_dc_power_flow_matrix()

    def get_bus_neighbours(self, bus_id: BUS_ID):
        neighbour_ids = []
        for line in self._grid_lines:
            if bus_id == line.to_bus:
                neighbour_ids.append(line.from_bus)
            elif bus_id == line.from_bus:
                neighbour_ids.append(line.to_bus)

        return list(set(neighbour_ids))

    def get_bus_grid_line(self, bus_id: BUS_ID) -> List[GridLine]:
        return [ line for line in self._grid_lines if bus_id == line.to_bus or
                 bus_id == line.from_bus]

    def _update_buses(self, grid_line: GridLine):
        to_bus = grid_line.to_bus
        from_bus = grid_line.from_bus
        if to_bus not in self._buses:
            self._buses.append(to_bus)
        elif from_bus not in self._buses:
            self._buses.append(from_bus)

    """
    def _calculate_adjacency_matrix(self):
        num_buses = len(self._buses)
        self._adjacency_matrix = np.zeros((num_buses, num_buses))
        for grid_line in self._grid_lines:
            index_bus_1 = self._buses.index(grid_line.to_bus)
            index_bus_2 = self._buses.index(grid_line.from_bus)
            self._adjacency_matrix[index_bus_1][index_bus_2] = 1
            self._adjacency_matrix[index_bus_2][index_bus_1] = 1        
    """

    def _calculate_admittance_matrix(self):
        admittance_matrix = np.zeros(len(self._buses, self._buses))
        for count, bus_id in enumerate(self._buses):
            lines = self.get_bus_grid_line(bus_id)
            for line in lines:
                if line.to_bus == bus_id:
                    from_bus_index = self._buses.index(line.from_bus)
                    admittance_matrix[count, from_bus_index] = -line.admittance
                else:
                    to_bus_index = self._buses.index(line.to_bus)
                    admittance_matrix[count, to_bus_index] = -line.admittance

            admittance_matrix[count, count] = -admittance_matrix[count, :].sum()

        return admittance_matrix

    def calculate_line_power(self, bus_power: Dict[BUS_ID, float]):
        power = np.array([bus_power[bus_id]  for bus_id in self._buses])
        # phase_angle = np.zeros(len(self.grid_lines))
        phase_angle = self._dc_power_flow_matrix@power.T
        phase_angle[0, 0] = 0
        for count, line in enumerate(self.grid_lines):
            to_bus_index = self._buses.index(line.to_bus)
            from_bus_index = self._buses.index(line.from_bus)
            self.line_power[count] = line.admittance*(phase_angle[from_bus_index] -
                                                      phase_angle[to_bus_index])


    def _calculate_dc_power_flow_matrix(self):
        num_buses = len(self.buses)
        self._dc_power_flow = self._admittance_matrix
        self._dc_power_flow[0, :] = np.zeros((1, num_buses))
        self._dc_power_flow[:, 0] = np.zeros((num_buses,))
        self._dc_power_flow[0, 0] = 1
        self._dc_power_flow = np.linalg.inv(self._dc_power_flow)

    def step(self, timestamp: int, bus_powers: Dict[BUS_ID, float]):
        assert sum([power for bus_id, power in bus_powers.items()]) == 0
        if self.is_grid_connected():
            # dc_power_flow_matrix = self._calculate_dc_power_flow_matrix()
            # self.line_power = dc_power_flow_matrix@power.T
            self.calculate_line_power(bus_powers)
            self._storage.add_simulation_data(timestamp, data=self._generate_simulation_data())
        else:
            logger.warning("graph is not complete cannot compute the power line power")


    def _generate_simulation_data(self) -> UnitSimulationData:
        values = {'line_power': self.line_power}
        return UnitSimulationData(values=values)