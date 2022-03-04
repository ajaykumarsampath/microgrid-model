import pytest

from data_loader.domain import SamplePointsToPowerTable


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
