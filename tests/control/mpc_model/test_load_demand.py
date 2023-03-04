from common.timeseries.domain import Timestamps, ConstantTimeseriesData, Bounds
from control.mpc_model.component.load_demand import LoadDemand
from control.mpc_model.control_data_model import ControlLoadDemandData
from tests.control.mock_optimisation_engine import MockOptimisationEngine


class TestLoadDemand:
    def test_extend_optimisation_model(self):
        timestamps = Timestamps([1, 2, 3, 4, 5])
        power_forecast = ConstantTimeseriesData(timestamps, 10)
        bounds = Bounds(0, 10)
        data = ControlLoadDemandData('load', timestamps, power_forecast, bounds)
        load = LoadDemand(data)

        mock_engine = MockOptimisationEngine()
        load.extend_optimisation_model(mock_engine)

        assert all([load.power[i].evaluate() == power_forecast.get_value(t)
                    for i, t in enumerate(timestamps)])
        assert mock_engine.variable[0] == load.power.optimisation_value
