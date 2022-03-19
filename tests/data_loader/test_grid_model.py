import pytest

from data_loader.domain import DuplicateGridModelError
from data_loader.grid_model import GridNetworkDataLoader, SingleBusGridNetworkDataLoader
from model.domain import GridLine

class TestGridDataLoader:
    def test_single_bus_grid_data(self):
        initial_timestamp = 10
        grid_data_loader = SingleBusGridNetworkDataLoader(initial_timestamp=initial_timestamp)

        assert len(grid_data_loader.grid_lines) == 0
        assert len(grid_data_loader.buses()) == 1
        assert grid_data_loader.validate_grid_line_data() == True
        assert grid_data_loader.check_grid_network_connected() == True

    def test_connected_grid_data(self):
        initial_timestamp = 10
        grid_lines = [GridLine(from_bus='bus_0', to_bus='bus_1', admittance=20),
                      GridLine(from_bus='bus_1', to_bus='bus_2', admittance=20),
                      GridLine(from_bus='bus_3', to_bus='bus_4', admittance=20),]
        grid_data_loader = GridNetworkDataLoader(initial_timestamp = initial_timestamp, grid_line=grid_lines)
        valid_data_flag = grid_data_loader.check_grid_network_connected()

        assert valid_data_flag == False

    def test_invalid_grid_data(self):
        grid_lines = [GridLine(from_bus='bus_0', to_bus='bus_1', admittance=20),
                      GridLine(from_bus='bus_2', to_bus='bus_2', admittance=20),]
        grid_data_loader = GridNetworkDataLoader(grid_line=grid_lines)
        valid_data_flag = grid_data_loader.validate_grid_line_data()

        assert valid_data_flag == False

    def test_duplicate_grid_data(self):
        initial_timestamp = 10
        grid_lines = [GridLine(from_bus='bus_0', to_bus='bus_1', admittance=20),
                      GridLine(from_bus='bus_1', to_bus='bus_2', admittance=20),
                      GridLine(from_bus='bus_1', to_bus='bus_2', admittance=40),
                      ]

        with pytest.raises(DuplicateGridModelError):
            grid_data_loader = GridNetworkDataLoader(
                initial_timestamp=initial_timestamp, grid_line=grid_lines
            )

    def test_grid_data_without_grid_lines(self):
        initial_timestamp = 10
        grid_data_loader = GridNetworkDataLoader(initial_timestamp, grid_line=[])

        assert len(grid_data_loader.grid_lines) == 0
        assert grid_data_loader.validate_grid_line_data() == True
        assert grid_data_loader.check_grid_network_connected() == False


    def test_add_grid_data(self):
        initial_timestamp = 10
        grid_line = [GridLine(from_bus='bus_0', to_bus='bus_1', admittance=20),
                     GridLine(from_bus='bus_1', to_bus='bus_2', admittance=20)]
        grid_data_loader = GridNetworkDataLoader(initial_timestamp, grid_line=grid_line)

        grid_data_loader.add_grid_line(GridLine(from_bus='bus_3', to_bus='bus_1', admittance=20))

        assert len(grid_data_loader.grid_lines) == 3
        assert grid_data_loader.validate_grid_line_data() == True
        assert grid_data_loader.check_grid_network_connected() == True

    def test_add_duplicate_grid_data(self):
        initial_timestamp = 10
        grid_line = [GridLine(from_bus='bus_0', to_bus='bus_1', admittance=20),
                     GridLine(from_bus='bus_1', to_bus='bus_2', admittance=20),
                     ]

        grid_data_loader = GridNetworkDataLoader(initial_timestamp, grid_line=grid_line)

        grid_data_loader.add_grid_line(GridLine(from_bus='bus_0', to_bus='bus_2', admittance=20))

        # print(grid_data_loader.check_grid_network_connected())
        # print(grid_data_loader.buses())
        assert len(grid_data_loader.grid_lines) == 3
        assert grid_data_loader.validate_grid_line_data() == True
        assert grid_data_loader.check_grid_network_connected() == True


if __name__ == '__main__':
    pass