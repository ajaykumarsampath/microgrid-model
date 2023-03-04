from typing import List

import numpy as np

from common.model.component import GridLine, BUS_ID


class GridNetworkUtils:
    @staticmethod
    def check_bus_grid_lines(buses: List[BUS_ID], grid_lines: List[GridLine]) -> bool:
        if len(grid_lines) == 0 and len(buses) == 1:
            return True
        else:
            try:
                for line in grid_lines:
                    assert line.to_bus in buses
                    assert line.from_bus in buses
                    assert line.to_bus != line.from_bus

                return True
            except AttributeError:
                return False

    @staticmethod
    def _get_bus_grid_line(bus_id: BUS_ID, grid_lines: List[GridLine]) -> List[GridLine]:
        return [line for line in grid_lines if line.is_connected_to_bus(bus_id)]

    @classmethod
    def calculate_admittance_matrix(cls, buses: List[BUS_ID], grid_lines: List[GridLine]):
        if cls.check_bus_grid_lines(buses, grid_lines):
            admittance_matrix = np.zeros((len(buses), len(buses)))
            for count, bus_id in enumerate(buses):
                lines = cls._get_bus_grid_line(bus_id, grid_lines)
                for line in lines:
                    if line.to_bus == bus_id:
                        from_bus_index = buses.index(line.from_bus)
                        admittance_matrix[count, from_bus_index] = -line.admittance
                    else:
                        to_bus_index = buses.index(line.to_bus)
                        admittance_matrix[count, to_bus_index] = -line.admittance

            admittance_matrix = admittance_matrix + np.diag(
                [-admittance_matrix[i, :].sum() for i in range(0, len(buses))]
            )
            return admittance_matrix

    @classmethod
    def calculate_dc_power_flow_matrix(cls, buses: List[BUS_ID], grid_lines: List[GridLine]):
        connected_status = cls.check_grid_network_connected(grid_lines)

        if connected_status and cls.check_bus_grid_lines(buses, grid_lines):
            num_buses = len(buses)
            dc_power_flow = cls.calculate_admittance_matrix(buses, grid_lines)
            dc_power_flow[0, :] = np.zeros((1, num_buses))
            dc_power_flow[:, 0] = np.zeros((num_buses,))
            dc_power_flow[0, 0] = 1
            dc_power_flow = np.linalg.inv(dc_power_flow)
            return dc_power_flow
        else:
            return np.array([])

    @classmethod
    def check_grid_network_connected(cls, grid_lines: List[GridLine]) -> bool:
        bus_set = []
        for line in grid_lines:
            bus_set = cls._update_bus_set(line, bus_set)

        if len(bus_set) == 1:
            return True
        else:
            return False

    @staticmethod
    def _update_bus_set(line: GridLine, list_set_buses: List[List[BUS_ID]]):
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
                    pass
                else:
                    from_bus_set = list_set_buses.pop(from_bus_set_index)
                    list_set_buses[to_bus_set_index] = list_set_buses[to_bus_set_index] + from_bus_set

        return list_set_buses
