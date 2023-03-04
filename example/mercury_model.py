from microgrid.config.microgrid import MicrogridModelConfigBuilder, MicrogridModelConfig
from microgrid.config.registry import default_component_registry
import numpy as np

from microgrid.data_loader.domain import SamplePointsToPowerTable
from microgrid.model.microgrid_model import MicrogridModel
from microgrid.shared.timeseries import SimulationTimeSeries


def solar_data():
    timestamps = np.arange(0, 100, 10).tolist()
    values = np.arange(0, 5, 1).tolist()
    values.extend(np.arange(5, 0, -1).tolist())

    power = np.arange(0, 1, 0.1).tolist()
    power[1:3] = [0, 0]
    points = np.arange(0, 10, 1).tolist()

    data = {'name': 'solar', 'initial_timestamp': 0, 'bus_id': '1',
            'data_loader_data':
                {'sample_point_to_power': SamplePointsToPowerTable(points=points, power_values=power),
                 'simulation_time_series': SimulationTimeSeries(timestamps=timestamps, values=values)
            }
    }
    return data


def wind_data():
    timestamps = np.arange(0, 100, 10).tolist()
    values = np.arange(0, 5, 1).tolist()
    values.extend(np.arange(5, 0, -1).tolist())

    power = np.arange(0, 1.5, 0.15).tolist()
    power[1:3] = [0, 0]
    points = np.arange(0, 10, 1).tolist()

    data = {'name': 'wind', 'initial_timestamp': 0, 'bus_id': '2',
            'data_loader_data':
                {'sample_point_to_power': SamplePointsToPowerTable(points=points, power_values=power),
                 'simulation_time_series': SimulationTimeSeries(timestamps=timestamps, values=values)
                 }
            }
    return data


def storage_data():
    data = {'name': 'battery', 'initial_timestamp': 0, 'bus_id': '2',
            'data_loader_data':
                {'power_bounds': {'min': -1, 'max': 1}, 'droop_gain': 1,
                 'energy_bounds': {'min': 0, 'max': 6}, 'initial_energy': 2}
            }
    return data


def load_data():
    timestamps = np.arange(0, 100, 10).tolist()
    values = np.arange(0, 0.5, 0.1).tolist()
    values.extend(np.arange(0.5, 0, -0.1).tolist())
    data = {'name': 'load', 'initial_timestamp': 0, 'bus_id': '3',
            'data_loader_data':
                {'demand_time_series':
                    SimulationTimeSeries(timestamps=timestamps, values=values)
                }
            }
    return data


def thermal_data():
    data = {'name': 'thermal', 'initial_timestamp': 0, 'bus_id': '4',
            'data_loader_data':
                {'power_bounds': {'min': 0.2, 'max': 1}, 'droop_gain': 1}
            }
    return data


def grid_network_data():
    data = {'name': 'grid', 'initial_timestamp': 0,
            'data_loader_data': {
                'grid_lines':
                [{'from_bus': '1', 'to_bus': '2', 'admittance': 20, 'bounds': {'min': -1, 'max': 1}},
                 {'from_bus': '1', 'to_bus': '3', 'admittance': 20, 'bounds': {'min': -1, 'max': 1}},
                 {'from_bus': '2', 'to_bus': '3', 'admittance': 20, 'bounds': {'min': -1, 'max': 1}},
                 {'from_bus': '4', 'to_bus': '3', 'admittance': 20, 'bounds': {'min': -1, 'max': 1}}]
                }
            }
    return data


def mercury_model_config():
    registry = default_component_registry()
    builder = MicrogridModelConfigBuilder(registry)
    microgrid_config = MicrogridModelConfig('mercury', [], [], [], [], [])

    # add load
    microgrid_config = builder.add_unit_config_data(
        microgrid_config, reference=registry.get_load_config_references()[0],
        data=load_data()
    )
    # add wind
    microgrid_config = builder.add_unit_config_data(
        microgrid_config, reference=registry.get_renewable_config_references()[0],
        data=wind_data()
    )
    # add solar
    microgrid_config = builder.add_unit_config_data(
        microgrid_config, reference=registry.get_renewable_config_references()[0],
        data=solar_data()
    )
    # add storage
    microgrid_config = builder.add_unit_config_data(
        microgrid_config, reference=registry.get_storage_config_references()[0],
        data=storage_data()
    )

    # add thermal
    microgrid_config = builder.add_unit_config_data(
        microgrid_config, reference=registry.get_thermal_config_references()[0],
        data=thermal_data()
    )

    # add grid model
    microgrid_config = builder.add_unit_config_data(
        microgrid_config, reference=registry.get_grid_config_references()[1],
        data=grid_network_data()
    )

    return microgrid_config


def mercury_model():
    registry = default_component_registry()
    builder = MicrogridModelConfigBuilder(registry)
    microgrid_config = mercury_model_config()
    data_loader = builder.generate_microgrid_model_data_loader(microgrid_config)

    data = data_loader.microgrid_model_data()
    microgrid = MicrogridModel(data)

    return microgrid


if __name__ == '__main__':
    mercury_config = mercury_model_config()
