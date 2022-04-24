import pytest

from data_loader.component.renewable_unit import RenewableUnitDataLoader
from data_loader.domain import SamplePointsToPowerTable, UnitDataLoaderError
from shared.timeseries import SimulationTimeSeries


class TestRenewableUnitDataLoader:
    def test_get_data(self):
        timestamps = list(range(0, 600, 60))
        values = list(range(0, 60, 6))
        simulation_time_series = SimulationTimeSeries(timestamps=timestamps, values=values)
        points = list(range(0, 60, 6))
        power_values = list(range(0, 1200, 120))
        sample_point_to_power = SamplePointsToPowerTable(
            points=points, power_values=power_values
        )
        renewable_data_loader = RenewableUnitDataLoader(
            initial_timestamp= 0, simulation_time_series=simulation_time_series,
            sample_point_to_power=sample_point_to_power
        )

        data = renewable_data_loader.get_data(500)
        assert renewable_data_loader.power_bounds.min == 0
        assert renewable_data_loader.power_bounds.max == 1080
        assert data == 1000

    def test_timestamp_not_simulation_data(self, caplog):
        timestamps = list(range(0, 600, 60))
        values = list(range(0, 60, 6))
        simulation_time_series = SimulationTimeSeries(timestamps=timestamps, values=values)
        points = list(range(0, 60, 6))
        power_values = list(range(0, 1200, 120))
        sample_point_to_power = SamplePointsToPowerTable(
            points=points, power_values=power_values
        )
        renewable_data_loader = RenewableUnitDataLoader(
            initial_timestamp=10, simulation_time_series=simulation_time_series,
            sample_point_to_power=sample_point_to_power
        )

        data = renewable_data_loader.get_data(1000)
        assert caplog.records[0].message == 'cannot get data at the timestamp'

    def test_demand_modelling_error_initial_timestamp(self):
        timestamps = list(range(0, 600, 60))
        values = list(range(0, 60, 6))
        simulation_time_series = SimulationTimeSeries(timestamps=timestamps, values=values)
        points = list(range(0, 60, 6))
        power_values = list(range(0, 1200, 120))
        sample_point_to_power = SamplePointsToPowerTable(
            points=points, power_values=power_values
        )

        with pytest.raises(UnitDataLoaderError):
            RenewableUnitDataLoader(
            initial_timestamp=600, simulation_time_series=simulation_time_series,
            sample_point_to_power=sample_point_to_power
        )
