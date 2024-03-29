from unittest import TestCase

from common.model.component import ComponentType
from microgrid.data_loader.interface import ILoadDemandDataLoader
from microgrid.model.component.load_demand import LoadDemand


class MockLoadDemandDataLoader(ILoadDemandDataLoader):
    def __init__(self, initial_timestamp: int, value: float):
        super().__init__(initial_timestamp=initial_timestamp)
        self._value = value

    def get_data(self, timestamp: int):
        return self._value


class TestLoadDemand(TestCase):
    def test_step_simulation_timestamp(self):
        initial_timestamp = 1639396720
        value = -4
        mock_load_demand_loader = MockLoadDemandDataLoader(
            initial_timestamp=initial_timestamp, value=value)

        load_model = LoadDemand('load_model', mock_load_demand_loader)

        load_model.step(initial_timestamp + 900)

        assert load_model.current_power == value
        assert load_model.current_timestamp == initial_timestamp + 900

    def test_control_component_data(self):
        initial_timestamp = 1639396720
        value = -4
        mock_renewable_loader = MockLoadDemandDataLoader(
            initial_timestamp=initial_timestamp, value=value)

        load_model = LoadDemand('load_model', mock_renewable_loader)

        control_component_data = load_model.control_component_data
        assert control_component_data.name == 'load_model'
        assert control_component_data.component_type == ComponentType.Load

    def test_current_simulation_data(self):
        initial_timestamp = 1639396720
        power = -5
        mock_load_demand_loader = MockLoadDemandDataLoader(
            initial_timestamp=initial_timestamp, value=power)

        load_model = LoadDemand('load_model', mock_load_demand_loader)

        data = load_model.current_simulation_data()

        assert data.values['current_power'] == 0
