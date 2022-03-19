from data_loader.microgrid_model import MicrogridModelDataLoader
from model.domain import UnitSimulationData, BUS_ID, Bounds
from tests.utils.test_mocks import MockUnitConfig, MockComponentDataLoader, MockGeneratorConfig, MockGeneratorDataLoader



def generate_mock_generator_config(name: str, bus_id: str):
    power_bounds = Bounds(0, 10)
    mock_generator_data_loader = MockGeneratorDataLoader(10, power_bounds)
    return MockGeneratorConfig(name, mock_generator_data_loader,
                               bus_id=BUS_ID(bus_id))

class TestMicrogridModel:
    def test_component_addition(self):
        microgrid_model_data = MicrogridModelDataLoader(name='mock_mg')

        expected_generator_name = ['mock_generator', 'mock_generator_1',
                                   'mock_generator_2']
        expected_bus_id = ['bus_0', 'bus_1', 'bus_2', 'bus_0']
        expected_demand_names = ['mock_unit']

        data = UnitSimulationData('mock_unit', values={'power': 1})
        mock_data_loader = MockComponentDataLoader(10, data)

        mock_unit_config = MockUnitConfig(expected_demand_names[0], mock_data_loader,
                                          bus_id=BUS_ID(expected_bus_id[3]))

        microgrid_model_data.add_demand_unit(mock_unit_config)

        mock_generator_configs = []
        for name, bus_id in zip(expected_generator_name, expected_bus_id):
            mock_generator_configs.append(
                generate_mock_generator_config(name, bus_id)
            )

        microgrid_model_data.add_storage_power_plant(mock_generator_configs[0])
        microgrid_model_data.add_thermal_power_plant(mock_generator_configs[1])
        microgrid_model_data.add_renewable_unit(mock_generator_configs[2])

        bus_ids = [microgrid_model_data.get_component_bus_id(name)
                            for name in expected_generator_name]
        bus_ids.append(microgrid_model_data.get_component_bus_id(expected_demand_names[0]))

        assert len(microgrid_model_data.get_renewable_units()) == 1
        assert len(microgrid_model_data.get_storage_power_plants()) == 1
        assert len(microgrid_model_data.get_thermal_generators()) == 1
        assert len(microgrid_model_data.get_load_demands()) == 1
        assert bus_ids == expected_bus_id

    def test_unknown_component_in_model(self):
        microgrid_model_data = MicrogridModelDataLoader(name='mock_mg')

        assert microgrid_model_data.get_component_bus_id('unknown') is None