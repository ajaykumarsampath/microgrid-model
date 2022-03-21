from unittest import TestCase

from data_loader.renewable_unit import IRenewableUnitDataLoader
from model.domain import Bounds, StepPreviousTimestamp
from model.renewable_unit import RenewablePowerUnit
from tests.utils.test_mocks import MockDataStorage


class MockRenewableUnitDataLoader(IRenewableUnitDataLoader):
    def __init__(self, initial_timestamp: int, power_bounds: Bounds, value: float):
        super().__init__(initial_timestamp=initial_timestamp, power_bounds=power_bounds)
        self._value = value

    def get_data(self, timestamp: int):
        return max(min(self._value, self.power_bounds.max), self.power_bounds.min)


class TestRenewableUnit(TestCase):
    def test_renewable_available_power(self):
        initial_timestamp = 1639396720
        value = 4
        mock_renewable_loader = MockRenewableUnitDataLoader(
            initial_timestamp=initial_timestamp, power_bounds=Bounds(0, 10), value=value)

        pv_model = RenewablePowerUnit('pv_model', mock_renewable_loader)

        assert pv_model.calculate_available_power(initial_timestamp + 900) == value

    def test_current_power_power_setpoint(self):
        initial_timestamp = 1639396720
        available_power = 5
        power_setpoint = 2
        mock_renewable_loader = MockRenewableUnitDataLoader(
            initial_timestamp=initial_timestamp, power_bounds=Bounds(0, 10), value=available_power)

        pv_model = RenewablePowerUnit('pv_model', mock_renewable_loader)

        pv_model.power_setpoint = power_setpoint
        pv_model.step(initial_timestamp + 900)

        assert pv_model.current_power == power_setpoint


    def test_current_power_available_power(self):
        initial_timestamp = 1639396720
        available_power = 5
        mock_renewable_loader = MockRenewableUnitDataLoader(
            initial_timestamp=initial_timestamp, power_bounds=Bounds(0, 10), value=available_power)

        pv_model = RenewablePowerUnit('pv_model', mock_renewable_loader)

        pv_model.power_setpoint = 6
        pv_model.step(initial_timestamp + 900)

        assert pv_model.current_power == available_power
        assert pv_model.current_timestamp == initial_timestamp + 900

    def test_step_simulation_timestamp(self):
        initial_timestamp = 1639396720
        available_power = 5
        power_setpoint = 6
        mock_renewable_loader = MockRenewableUnitDataLoader(
            initial_timestamp=initial_timestamp, power_bounds=Bounds(0, 10), value=available_power)

        pv_model = RenewablePowerUnit('pv_model', mock_renewable_loader)

        pv_model.power_setpoint = power_setpoint
        pv_model.step(initial_timestamp + 900)

        self.assertRaises(StepPreviousTimestamp, pv_model.step, initial_timestamp + 900)

    def test_current_simulation_data(self):
        initial_timestamp = 1639396720
        available_power = 5
        mock_renewable_loader = MockRenewableUnitDataLoader(
            initial_timestamp=initial_timestamp, power_bounds=Bounds(0, 10), value=available_power)

        pv_model = RenewablePowerUnit('pv_model', mock_renewable_loader)

        mock_storage = MockDataStorage()
        pv_model.add_simulation_data(mock_storage)

        data = pv_model.current_simulation_data()

        assert data.values['current_power'] == 0
        assert data.values['available_power'] == 0
        assert data.values['power_setpoint'] == 0