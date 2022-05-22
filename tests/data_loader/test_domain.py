import pytest

from microgrid.data_loader.domain import SamplePointsToPowerTable
from microgrid.data_loader.interface import IGeneratorDataLoader
from microgrid.shared.component import Bounds


class TestSamplePointsToPowerTable:
    def test_sample_point_to_table(self):
        points = list(range(0, 5))
        power_values = list(range(0, 50, 10))
        sample_point_table = SamplePointsToPowerTable(points=points, power_values=power_values)

        assert sample_point_table.maximum() == power_values[-1]
        assert sample_point_table.minimum() == power_values[0]

    def test_unequal_sample_point_to_table(self):
        points = list(range(0, 5))
        power_values = list(range(0, 50))

        with pytest.raises(ValueError):
            SamplePointsToPowerTable(points=points, power_values=power_values)

    def test_not_existance_sample_point_to_table(self):
        points = list(range(0, 5))
        power_values = list(range(0, 50, 10))
        point_power_table = SamplePointsToPowerTable(points=points, power_values=power_values)

        with pytest.raises(ValueError):
            point_power_table.available_power_at_sample_point(6)


class TestUnitDataLoader:
    def test_unit_data_loader(self):
        power_bounds = Bounds(0, 10)
        generator_loader = IGeneratorDataLoader(
            initial_timestamp=10, power_bounds=power_bounds)

        assert generator_loader.droop_gain == 0
        assert generator_loader.power_bounds == power_bounds
        assert not generator_loader.grid_forming_unit_flag

    def test_grid_forming_data_loader(self):
        power_bounds = Bounds(0, 10)
        generator_loader = IGeneratorDataLoader(
            initial_timestamp=10, power_bounds=power_bounds, grid_forming_unit_flag=True,
            droop_gain=1
        )

        assert generator_loader.droop_gain == 1
        assert generator_loader.power_bounds == power_bounds
        assert generator_loader.grid_forming_unit_flag
