import pytest

from common.timeseries.domain import Bounds
from microgrid.data_loader.interface import IGeneratorDataLoader
from microgrid.model.exception import StepPreviousTimestamp
from microgrid.shared.simulation_data import ComponentSimulationData
from microgrid.shared.timeseries import SimulationTimeseriesError
from microgrid.utils.memory_storage import HistoricalData
from tests.utils.test_mocks import MockGeneratorUnit, MockComponentDataLoader, MockComponent


def test_wrong_historical_data():
    wrong_timestamp = list(range(0, 10))
    wrong_timestamp[-1] = 8
    data = [ComponentSimulationData(name='a', values={'power': t}) for t in wrong_timestamp]

    with pytest.raises(SimulationTimeseriesError):
        HistoricalData(timestamps=wrong_timestamp, data=data)

    with pytest.raises(SimulationTimeseriesError):
        HistoricalData(timestamps=wrong_timestamp[0: 5], data=data)

    with pytest.raises(SimulationTimeseriesError):
        HistoricalData(timestamps=wrong_timestamp, data=data[0: 5])


def test_historical_data():
    timestamp = list(range(0, 10))
    data = [ComponentSimulationData(name='a', values={'power': t}) for t in timestamp]
    historical_data = HistoricalData(timestamps=timestamp, data=data)

    current_data = ComponentSimulationData(name='a', values={'power': 12})
    with pytest.raises(SimulationTimeseriesError):
        historical_data.add_data(timestamp=8, data=current_data)

    historical_data.add_data(timestamp=12, data=current_data)

    assert len(historical_data.timestamps) == 11
    assert len(historical_data.data) == 11


def test_component_interface():
    initial_timestamp = 10

    mock_data = ComponentSimulationData(name='mock', values={'power': 1})

    mock_loader = MockComponentDataLoader(initial_timestamp, data=mock_data)

    mock_unit = MockComponent(name='mock', data_loader=mock_loader)

    timestamp = list(range(0, initial_timestamp))
    data = [ComponentSimulationData(name='a', values={'power': t}) for t in timestamp]

    data = mock_unit.current_simulation_data()

    assert data.values == mock_data.values


def test_wrong_simulation_timestamp():
    initial_timestamp = 10

    mock_data = ComponentSimulationData(name='mock', values={'power': 1})

    mock_loader = MockComponentDataLoader(initial_timestamp, data=mock_data)

    mock_unit = MockComponent(name='mock', data_loader=mock_loader)

    current_timestamp = 10
    with pytest.raises(StepPreviousTimestamp):
        mock_unit.step(current_timestamp)


class TestPowerUnit:
    def test_power_set_points(self):
        data_loader = IGeneratorDataLoader(initial_timestamp=10, power_bounds=Bounds(0, 10))
        mock_power_unit = MockGeneratorUnit(name='mock', data_loader=data_loader)

        mock_power_unit.power_setpoint = 4
        assert mock_power_unit.power_setpoint == 4

        with pytest.raises(ValueError):
            mock_power_unit.power_setpoint = 11

        with pytest.raises(ValueError):
            mock_power_unit.power_setpoint = -1

    def test_droop_values(self):
        droop_gain = 10
        data_loader = IGeneratorDataLoader(initial_timestamp=10, droop_gain=droop_gain,
                                           power_bounds=Bounds(0, 10))
        mock_power_unit = MockGeneratorUnit(name='mock', data_loader=data_loader)

        assert mock_power_unit.droop_gain == droop_gain
        assert mock_power_unit.droop_gain_inverse() == 1 / droop_gain

    def test_zero_droop_value(self):
        droop_gain = 0
        data_loader = IGeneratorDataLoader(initial_timestamp=10, droop_gain=droop_gain,
                                           power_bounds=Bounds(0, 10))
        mock_power_unit = MockGeneratorUnit(name='mock', data_loader=data_loader)

        assert mock_power_unit.droop_gain == droop_gain
        assert mock_power_unit.droop_gain_inverse() == droop_gain
