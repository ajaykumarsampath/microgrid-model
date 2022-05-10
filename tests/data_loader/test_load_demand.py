import pytest

from data_loader.domain import UnitDataLoaderError
from data_loader.component.load_demand import LoadDemandDataLoader
from shared.timeseries import SimulationTimeSeries


class TestLoadDemandDataLoader:
    def test_get_data(self):
        timestamps = list(range(0, 600, 60))
        values = list(range(0, -60, -6))
        demand_time_series = SimulationTimeSeries(timestamps=timestamps, values=values)
        load_demand_loader = LoadDemandDataLoader(10, demand_time_series)

        data = load_demand_loader.get_data(540)
        assert data == -54


    def test_get_data_unknown_timestamp(self, caplog):
        timestamps = list(range(0, 600, 60))
        values = list(range(0, -60, -6))
        demand_time_series = SimulationTimeSeries(timestamps=timestamps, values=values)
        load_demand_loader = LoadDemandDataLoader(10, demand_time_series)

        load_demand_loader.get_data(6000)
        assert caplog.records[0].message == 'cannot get the data at the timestamp'

    def test_demand_modelling_error_initial_timestamp(self):
        timestamps = list(range(0, 600, 60))
        values = list(range(0, -60, -6))
        demand_time_series = SimulationTimeSeries(timestamps=timestamps, values=values)
        with pytest.raises(UnitDataLoaderError):
            LoadDemandDataLoader(610, demand_time_series)
