import numpy as np

import pytest
from model.domain import SimulationTimeSeries, SimulationTimeseriesError
from data_loader.domain import SamplePointsToPowerTable



class TestSimulationTimeSeries:
    def test_simulation_timeseries(self):
        timestamps = list(range(0, 4500, 900))
        values = np.array(list(range(0, 50, 10)))
        simulation_series = SimulationTimeSeries(timestamps, values)

        assert simulation_series.resample(900) == 10
        assert simulation_series.resample(1350) == 15
        assert simulation_series.resample(-900) == -10

    def test_unequal_simulation_timeseries(self):
        timestamps = list(range(0, 4500, 900))
        values = np.array(list(range(0, 60, 10)))
        with pytest.raises(SimulationTimeseriesError):
            SimulationTimeSeries(timestamps, values)




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


if __name__ == '__main__':
    test_simulation_series = TestSimulationTimeSeries()
    test_simulation_series.test_simulation_timeseries()
    test_simulation_series.test_unequal_simulation_timeseries()

    test_sample_power_table = TestSamplePointsToPowerTable()
    test_sample_power_table.test_sample_point_to_table()
    test_sample_power_table.test_unequal_sample_point_to_table()
    test_sample_power_table.test_not_existance_sample_point_to_table()
