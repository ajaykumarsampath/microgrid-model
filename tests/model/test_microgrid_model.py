import copy

import pytest

from model.domain import UnitSimulationData, Bounds, MicrogirdModellingError, StepPreviousTimestamp
from model.microgrid_model import MicrogridModelData, MicrogridModel
from tests.utils.test_mocks import MockGeneratorUnit, MockComponent, MockComponentDataLoader, \
    MockGeneratorDataLoader, MockGridNetwork


def test_microgrid_model_data():
    initial_timestamp = 1639396720
    expected_bus_ids = ['BUS_1', 'BUS_2']
    mock_data = UnitSimulationData(name='mock', values={'power': 1})
    data_loaders = MockComponentDataLoader(initial_timestamp, mock_data)

    unit_data_loader = MockGeneratorDataLoader(initial_timestamp, power_bounds=Bounds(0, 10))
    generators = [MockGeneratorUnit('generator', unit_data_loader),
                  # MockPowerUnit('generator_1', copy.deepcopy(unit_data_loader))
                  ]
    loads = [MockComponent('load', data_loaders)]

    grid_loader = MockComponentDataLoader(initial_timestamp, UnitSimulationData('grid', values={}))
    mock_grid = MockGridNetwork('grid', grid_loader, buses=expected_bus_ids)
    data = MicrogridModelData(name='microgrid', generators=generators,
                              loads=loads, grid_model= mock_grid,
                              generator_bus_ids=[expected_bus_ids[0]],
                              load_bus_ids=[expected_bus_ids[-1]])

    assert [id in expected_bus_ids for id in data.model_bus_ids]
    assert data.valid_data == True
    assert data.unit_bus_matrix().shape[0] == 2
    assert data.unit_bus_matrix().shape[1] == 2
    assert data.generator_bus_ids[0] == expected_bus_ids[0]
    assert data.load_bus_ids[-1] == expected_bus_ids[-1]

def test_microgrid_duplicate_model_data():
    initial_timestamp = 1639396720
    expected_bus_ids = ['BUS_1']
    mock_data = UnitSimulationData(name='mock', values={'power': 1})
    data_loaders = MockComponentDataLoader(initial_timestamp, mock_data)

    unit_data_loader = MockGeneratorDataLoader(initial_timestamp, power_bounds=Bounds(0, 10))

    generators = [MockGeneratorUnit('generator', unit_data_loader),
                  MockGeneratorUnit('generator', copy.deepcopy(unit_data_loader))
                  ]
    loads = [MockComponent('load', data_loaders)]

    grid_loader = MockComponentDataLoader(initial_timestamp, UnitSimulationData('grid', values={}))
    mock_grid = MockGridNetwork('grid', grid_loader, buses=expected_bus_ids)
    data = MicrogridModelData(name='microgrid', generators=generators, loads=loads,
                              grid_model= mock_grid, generator_bus_ids=[expected_bus_ids[0]],
                              load_bus_ids=[expected_bus_ids[-1]])
    data_no_unit = MicrogridModelData(name='microgrid', generators=[generators[0]], loads=[],
                              grid_model=mock_grid, generator_bus_ids=[expected_bus_ids[0]],
                              load_bus_ids=[expected_bus_ids[-1]])

    assert data.valid_data == False
    assert data_no_unit.valid_data == False

def test_microgrid_modelling_error():
    initial_timestamp = 1639396720
    expected_bus_ids = ['BUS_1', 'BUS_2']
    mock_data = UnitSimulationData(name='mock', values={'power': 1})
    data_loaders = MockComponentDataLoader(initial_timestamp, mock_data)

    unit_data_loader = MockGeneratorDataLoader(initial_timestamp, power_bounds=Bounds(-5, 5))
    generators = [MockGeneratorUnit('generator', unit_data_loader),
                  MockGeneratorUnit('generator_1', copy.deepcopy(unit_data_loader))
                  ]
    loads = [MockComponent('load', data_loaders)]

    grid_loader = MockComponentDataLoader(initial_timestamp, UnitSimulationData('grid', values={}))
    mock_grid = MockGridNetwork('grid', grid_loader, buses=expected_bus_ids)
    data = MicrogridModelData(name='microgrid', generators=generators, loads=loads, grid_model=mock_grid,
                              generator_bus_ids=[expected_bus_ids[0]],
                              load_bus_ids=[expected_bus_ids[-1]])

    with pytest.raises(MicrogirdModellingError):
        MicrogridModel(data)

# @pytest.fixture()
def microgird_model_data(initial_timestamp, droop_gain:float=1):
    # initial_timestamp = 1639396720
    expected_bus_ids = ['BUS_1', 'BUS_2']
    mock_data = UnitSimulationData(name='mock', values={'power': 1})
    data_loaders = MockComponentDataLoader(initial_timestamp, mock_data)

    unit_data_loader = MockGeneratorDataLoader(initial_timestamp, power_bounds=Bounds(-5, 5))
    unit_data_loader_1 = MockGeneratorDataLoader(initial_timestamp, power_bounds=Bounds(-5, 5),
                                                 droop_gain=droop_gain, grid_forming_unit_flag = True)

    generators = [MockGeneratorUnit('generator', unit_data_loader),
                  MockGeneratorUnit('generator_1', unit_data_loader_1)
                  ]
    loads = [MockComponent('load', data_loaders)]

    grid_loader = MockComponentDataLoader(initial_timestamp, UnitSimulationData('grid', values={}))
    mock_grid = MockGridNetwork('grid', grid_loader, buses=expected_bus_ids)
    data = MicrogridModelData(name='microgrid', generators=generators, loads=loads, grid_model=mock_grid,
                              generator_bus_ids=[expected_bus_ids[0], expected_bus_ids[0]],
                              load_bus_ids=[expected_bus_ids[-1]])

    return data

def test_microgrid_power_setpoint():
    initial_timestamp = 1639396720
    model_data = microgird_model_data(initial_timestamp)
    model = MicrogridModel(model_data)

    power_setpoints = [1, 0.5]
    for g, power in zip(model_data.generators, power_setpoints):
        model.set_power_setpoint(g.name, power)

    assert [g.power_setpoint for g in model_data.generators] == power_setpoints

    power_setpoints = [0.5, 1]
    model.set_power_setpoints(power_setpoints)
    assert [g.power_setpoint for g in model_data.generators] == power_setpoints


def test_simulation_previous_timestamp():
    initial_timestamp = 1639396720
    model_data = microgird_model_data(initial_timestamp)
    model = MicrogridModel(model_data)

    with pytest.raises(StepPreviousTimestamp):
        model.step(initial_timestamp - 900)


def test_simulation():
    initial_timestamp = 1639396720
    model_data = microgird_model_data(initial_timestamp)
    model = MicrogridModel(model_data)

    power_setpoints = [-1, 1]
    model.set_power_setpoints(power_setpoints)

    model.step(initial_timestamp + 900)

    assert model.current_power[0] == -1
    assert model.current_power[1] == 1
    assert model.current_power[2] == 0

def test_inverse_droop_gain():
    initial_timestamp = 1639396720
    droop_gain = 0.5
    model_data = microgird_model_data(initial_timestamp, droop_gain)
    model = MicrogridModel(model_data)
    assert model.sum_inverse_droop_gain == 1/droop_gain


def test_calculate_delta_frequency():
    initial_timestamp = 1639396720
    model_data = microgird_model_data(initial_timestamp)
    model = MicrogridModel(model_data)

    power_setpoints = [0, 1]
    model.set_power_setpoints(power_setpoints)

    delta_frequency = model.calculate_delta_frequency()
    assert delta_frequency == 1

    power_setpoints = [0.5, -1]
    model.set_power_setpoints(power_setpoints)

    delta_frequency = model.calculate_delta_frequency()
    assert delta_frequency == -1