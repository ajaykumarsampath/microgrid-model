from common.model.component import BUS_ID
from common.timeseries.domain import Bounds
from microgrid.data_loader.microgrid_model import MicrogridModelDataLoader
from microgrid.shared.simulation_data import ComponentSimulationData
from tests.utils.test_mocks import MockUnitConfig, MockGeneratorConfig, \
    MockUnitConfigData, MockComponentDataLoaderData, MockGeneratorDataLoaderData, \
    MockGeneratorConfigData


def generate_mock_generator_config(name: str, bus_id: str):
    power_bounds = Bounds(0, 10)
    data_loader_data = MockGeneratorDataLoaderData(power_bounds=power_bounds)
    config_data = MockGeneratorConfigData(
        name, initial_timestamp=10, data_loader_data=data_loader_data, bus_id=BUS_ID(bus_id))
    return MockGeneratorConfig(config_data)


class TestMicrogridModel:
    def test_component_addition(self):
        microgrid_model_data = MicrogridModelDataLoader(name='mock_mg')

        expected_generator_name = ['mock_generator', 'mock_generator_1',
                                   'mock_generator_2']
        expected_bus_id = ['bus_0', 'bus_1', 'bus_2', 'bus_0']

        data = ComponentSimulationData('mock_unit', values={'power': 1})
        mock_data_loader_data = MockComponentDataLoaderData(data=data)

        config = MockUnitConfigData(name='mock_unit', initial_timestamp=10,
                                    data_loader_data=mock_data_loader_data,
                                    bus_id=BUS_ID(expected_bus_id[3]))

        mock_unit_config = MockUnitConfig(config)

        microgrid_model_data.add_demand_unit(mock_unit_config)

        mock_generator_configs = []
        for name, bus_id in zip(expected_generator_name, expected_bus_id):
            mock_generator_configs.append(
                generate_mock_generator_config(name, bus_id)
            )

    def test_unknown_component_in_model(self):
        microgrid_model_data = MicrogridModelDataLoader(name='mock_mg')

        assert microgrid_model_data.get_component_bus_id('unknown') is None
