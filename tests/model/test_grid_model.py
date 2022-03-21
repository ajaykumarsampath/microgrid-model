import time

import numpy as np

from model.domain import GridLine, UnknownComponentError
from model.grid_model import GridNetwork
from data_loader.grid_model import GridNetworkDataLoader, SingleBusGridNetworkDataLoader
import pytest


class TestGridModel:
    def test_single_bus_grid_model(self):
        initial_timestamp = 1645825124
        grid_network_data = SingleBusGridNetworkDataLoader(initial_timestamp=initial_timestamp)
        grid_network = GridNetwork(name='network', data_loader=grid_network_data)

        assert len(grid_network.grid_lines) == 0
        assert len(grid_network.buses) == 1
        assert grid_network.admittance_matrix == np.zeros((1, 1))
        assert len(grid_network.dc_power_flow_matrix) == 0
        assert grid_network.get_bus_grid_line(grid_network_data.SLACK_BUS_ID) == []
        assert grid_network.get_bus_neighbours(grid_network_data.SLACK_BUS_ID) == []
        assert grid_network.get_bus_grid_line('abs') == []

    def test_grid_model_with_grid_lines(self):
        initial_timestamp = 1645825124
        admittance = 20
        grid_lines = [GridLine(from_bus='bus_0', to_bus='bus_1', admittance=admittance), ]
        grid_network_data = GridNetworkDataLoader(
            initial_timestamp=initial_timestamp, grid_line=grid_lines)
        grid_network = GridNetwork(name='network', data_loader=grid_network_data)

        expected_bus_ids = ['bus_0', 'bus_1']
        expected_admittance = np.array([[admittance, -admittance],
                                    [-admittance, admittance]])

        assert grid_network.grid_lines[0] == grid_lines[0]
        assert all([b in expected_bus_ids for b in grid_network.buses])
        assert np.linalg.norm(grid_network.admittance_matrix -  expected_admittance) == 0
        assert grid_network.get_bus_grid_line('bus_0')[0] == grid_lines[0]
        assert grid_network.get_bus_grid_line('bus_1')[0] == grid_lines[0]

    def test_set_bus_power(self):
        initial_timestamp = int(time.time())
        grid_lines = [GridLine(from_bus='bus_0', to_bus='bus_1', admittance=20),
                      GridLine(from_bus='bus_1', to_bus='bus_2', admittance=20), ]
        grid_network_data = GridNetworkDataLoader(
            initial_timestamp=initial_timestamp, grid_line=grid_lines
        )
        grid_network = GridNetwork(name='network', data_loader=grid_network_data)

        grid_network.set_bus_power(bus_id='bus_0', power=-3)
        grid_network.set_bus_power(bus_id='bus_1', power=5)
        grid_network.set_bus_power(bus_id='bus_2', power=-2)

        expected_bus_power = [-3, 5, -2]
        expected_buses = ['bus_0', 'bus_1', 'bus_2']

        assert all([p in expected_bus_power for p in grid_network.buses_power])
        assert all([bus in expected_buses for bus in grid_network.buses])

    def test_calculate_line_power(self):
        initial_timestamp = int(time.time())
        grid_lines = [GridLine(from_bus='bus_0', to_bus='bus_1', admittance=20),
                      GridLine(from_bus='bus_1', to_bus='bus_2', admittance=20),]
        grid_network_data = GridNetworkDataLoader(
            initial_timestamp=initial_timestamp, grid_line=grid_lines
        )
        grid_network = GridNetwork(name='network', data_loader=grid_network_data)

        grid_network.set_bus_power(bus_id='bus_0', power=-3)
        grid_network.set_bus_power(bus_id='bus_1', power=5)
        grid_network.set_bus_power(bus_id='bus_2', power=-2)
        line_power = grid_network.calculate_line_power()

        assert pytest.approx(line_power[0], -3, 1e-5)
        assert pytest.approx(line_power[1], 2, 1e-5)

    def test_wrong_set_bus_power(self):
        initial_timestamp = int(time.time())
        grid_lines = [GridLine(from_bus='bus_0', to_bus='bus_1', admittance=20)]
        grid_network_data = GridNetworkDataLoader(
            initial_timestamp=initial_timestamp, grid_line=grid_lines
        )
        grid_network = GridNetwork(name='network', data_loader=grid_network_data)

        with pytest.raises(UnknownComponentError):
            grid_network.set_bus_power(bus_id='bus_4', power=-3)

        initial_timestamp = 1645825124
        grid_network_data = SingleBusGridNetworkDataLoader(initial_timestamp=initial_timestamp)
        grid_network = GridNetwork(name='network', data_loader=grid_network_data)

        with pytest.raises(UnknownComponentError):
            grid_network.set_bus_power('bus_1', power=0)

    def test_single_bus_step(self):
        initial_timestamp = 1645825124
        grid_network_data = SingleBusGridNetworkDataLoader(initial_timestamp=initial_timestamp)
        grid_network = GridNetwork(name='network', data_loader=grid_network_data)

        grid_network.set_bus_power('slack', 0)
        grid_network.step(initial_timestamp + 900)

        data = grid_network.current_simulation_data()

        assert grid_network.buses_power == 0
        assert len(grid_network.current_power) == 0
        assert len(data.values['current_power']) == 0
        assert data.values['bus_power'] == 0

    def test_multiple_line_bus_step(self):
        initial_timestamp = 1645825124
        grid_lines = [GridLine(from_bus='bus_0', to_bus='bus_1', admittance=20)]
        grid_network_data = GridNetworkDataLoader(
            initial_timestamp=initial_timestamp, grid_line=grid_lines
        )
        grid_network = GridNetwork(name='network', data_loader=grid_network_data)

        grid_network.set_bus_power('bus_0', 1)
        grid_network.set_bus_power('bus_1', -1)
        grid_network.step(initial_timestamp + 900)

        expected_bus_power = [1, -1]

        assert abs(grid_network.current_power) == 1
        assert all([p in expected_bus_power for p in grid_network.buses_power])

if __name__ == '__main__':

    test_grid = TestGridModel()
    test_grid.test_calculate_line_power()
    # grid_network = test_grid.create_single_bus_grid_model()
    # grid_network = test_grid.create_sample_grid_model()
    # print(grid_network.admittance_matrix)
    # print(grid_network.dc_power_flow_matrix)
    # print(grid_network.buses())

    # print(grid_network.is_grid_connected())


    # test_grid_data_loader = TestGridDataLoader()
    # test_grid_data_loader.test_connected_grid_data()
    # test_grid_data_loader.test_invalid_grid_data()
    # test_grid_data_loader.test_duplicate_grid_data()
    # test_grid_data_loader.test_add_grid_data()
    print("completed")
