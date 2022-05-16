from typing import List

from data_loader.domain import DuplicateGridModelError
from data_loader.interface import IGridNetworkDataLoader
import logging

from shared.component import GridLine
from shared.timeseries import Timestamp

logger = logging.getLogger(__name__)


class SingleBusGridNetworkDataLoader(IGridNetworkDataLoader):
    SLACK_BUS_ID = 'slack'

    def __init__(self, initial_timestamp: Timestamp):
        super().__init__(initial_timestamp)
        self._grid_lines = []

    def buses(self):
        return [self.SLACK_BUS_ID]

    @property
    def grid_lines(self):
        return self._grid_lines

    def validate_grid_line_data(self):
        return True

    def check_grid_network_connected(self):
        return True


class GridNetworkDataLoader(IGridNetworkDataLoader):
    def __init__(self, initial_timestamp: Timestamp, grid_line: List[GridLine]):
        super(GridNetworkDataLoader, self).__init__(initial_timestamp)
        if self._check_duplicate_grid_lines(grid_line):
            self._grid_lines = grid_line
        else:
            raise DuplicateGridModelError("model has duplicated lines")

    @property
    def grid_lines(self):
        return self._grid_lines

    def validate_grid_line_data(self) -> bool:
        if len(self.grid_lines) > 0:
            return all([line.from_bus != line.to_bus for line in self.grid_lines])
        else:
            return True

    @staticmethod
    def _check_duplicate_grid_lines(grid_lines: List[GridLine]) -> bool:
        bool_flag = True
        if len(grid_lines) > 1:
            for count, line in enumerate(grid_lines[:-1]):
                if line in grid_lines[count + 1:]:
                    bool_flag = False
        return bool_flag

    def add_grid_line(self, grid_line: GridLine):
        if self._validate_grid_line(grid_line):
            self.grid_lines.append(grid_line)
        else:
            # raise DuplicateGridModelError("Line cannot be added either the line already exists")
            logger.warning("Line cannot be added either the line already exists")

    def _validate_grid_line(self, grid_line: GridLine) -> bool:
        if grid_line in self.grid_lines:
            return False
        else:
            return True

    def buses(self):
        bus = []
        for line in self.grid_lines:
            if line.to_bus not in bus:
                bus.append(line.to_bus)
            if line.from_bus not in bus:
                bus.append(line.from_bus)
        return bus

    def check_grid_network_connected(self) -> bool:
        bus_set = []
        for line in self.grid_lines:
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
                    # logger.warning(f"duplicate line {line}")
                    pass
                else:
                    from_bus_set = list_set_buses.pop(from_bus_set_index)
                    list_set_buses[to_bus_set_index] = \
                        list_set_buses[to_bus_set_index] + from_bus_set

        return list_set_buses


if __name__ == '__main__':
    a = {'GridNetworkDataLoader': GridNetworkDataLoader}
