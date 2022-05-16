import numpy as np

import pytest
from shared.component import ComponentSimulationData, GridLine
from shared.timeseries import SimulationTimeseriesError, SimulationTimeSeries
from utils.storage import HistoricalData

from tests.data_loader.test_domain import TestSamplePointsToPowerTable


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


class TestHistoricalData:
    def test_valid_historical_data(self):
        timestamps = [0, 10, 20, 30]
        data = [ComponentSimulationData('mock', values={'power': i}) for i in range(0, len(timestamps))]
        historical_data = HistoricalData(timestamps, data)

        assert historical_data.timestamps == timestamps
        assert historical_data.data == data

    def test_invalid_historical_data(self):
        timestamps = [0, 10, 20, 30]
        data = [ComponentSimulationData('mock', values={'power': i})
                for i in range(0, len(timestamps) - 1)]

        with pytest.raises(SimulationTimeseriesError):
            HistoricalData(timestamps, data)

    def test_duplicated_timestamps(self):
        timestamps = [0, 10, 20, 20]
        data = [ComponentSimulationData('mock', values={'power': i})
                for i in range(0, len(timestamps) - 1)]

        with pytest.raises(SimulationTimeseriesError):
            HistoricalData(timestamps, data)

    def test_add_data(self):
        timestamps = [0, 10, 20, 30]
        data = [ComponentSimulationData('mock', values={'power': i}) for i in range(0, len(timestamps))]

        historical_data = HistoricalData(timestamps, data)
        data_point = ComponentSimulationData('mock', values={'power': 8})
        historical_data.add_data(40, data_point)

        assert historical_data.data[-1] == data_point
        assert historical_data.timestamps[-1] == 40

    def test_add_existing_timestamp(self):
        timestamps = [0, 10, 20, 30]
        data = [ComponentSimulationData('mock', values={'power': i}) for i in range(0, len(timestamps))]

        historical_data = HistoricalData(timestamps, data)
        data_point = ComponentSimulationData('mock', values={'power': 8})
        with pytest.raises(SimulationTimeseriesError):
            historical_data.add_data(30, data_point)

        assert historical_data.data == data
        assert historical_data.timestamps == timestamps


def test_grid_line_comparison():
    grid_line_1 = GridLine(from_bus='bus_0', to_bus='bus_1', admittance=20)
    grid_line_2 = GridLine(from_bus='bus_1', to_bus='bus_0', admittance=20)
    grid_line_3 = GridLine(from_bus='bus_3', to_bus='bus_0', admittance=10)

    assert grid_line_1 == grid_line_2
    assert not grid_line_3 == grid_line_2
    assert not grid_line_1 == 1


def test_invalid_grid_line():
    with pytest.raises(ValueError):
        GridLine(from_bus='bus_0', to_bus='bus_0', admittance=20)


if __name__ == '__main__':
    test_simulation_series = TestSimulationTimeSeries()
    test_simulation_series.test_simulation_timeseries()
    test_simulation_series.test_unequal_simulation_timeseries()

    test_sample_power_table = TestSamplePointsToPowerTable()
    test_sample_power_table.test_sample_point_to_table()
    test_sample_power_table.test_unequal_sample_point_to_table()
    test_sample_power_table.test_not_existance_sample_point_to_table()
