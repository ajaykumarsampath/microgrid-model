from dataclasses import dataclass
from typing import List

import numpy as np
from numpy.random._generator import default_rng

from common.model.component import BUS_ID
from common.timeseries.domain import Bounds
from microgrid.config.interface import IUnitConfig, IGeneratorComponentConfig
from microgrid.data_loader.component.renewable_unit import RenewableUnitDataLoader
from microgrid.data_loader.domain import SamplePointsToPowerTable
from microgrid.data_loader.interface import IGeneratorDataLoader
from microgrid.model.component.renewable_unit import RenewablePowerUnit

from microgrid.model.component_interface import IComponent, IGridNetwork
from microgrid.model.generator_interface import IGeneratorComponent
from microgrid.shared.simulation_data import ComponentSimulationData
from microgrid.shared.data_loader import IComponentDataLoader, IComponentDataLoaderData, IUnitConfigData, \
    IGeneratorConfigData
from microgrid.shared.timeseries import SimulationTimeSeries
from microgrid.shared.storage import IComponentDataStorage
from microgrid.utils.memory_storage import HistoricalData


class MockDataStorage(IComponentDataStorage):
    def __init__(self, data: HistoricalData = HistoricalData([], [])):
        self._data = data

    def add_simulation_data(self, current_timestamp: int, data: ComponentSimulationData):
        self._data.add_data(current_timestamp, data)

    def get_historical_data(self, unit_id: str, since: int, until: int = None)\
            -> List[ComponentSimulationData]:
        return [d for t, d in zip(self._data.timestamps, self._data.data) if t > since]


def generate_solar_irradiance_days(days: int = 14, scale: int = 100, resolution: int = 900)\
        -> np.ndarray:
    values = np.zeros((days, int(24 * 3600 / resolution)))
    r = default_rng()
    samples = int(24 * 3600 / resolution)

    for day in range(0, days):
        start_sun_rise = int(samples / 8) + r.integers(int(samples / 4))
        end_sun_rise = int(samples / 2) + r.integers(int(samples / 3))
        day_scale = scale * r.random(1)
        per_day_values = np.zeros(samples)
        per_day_values[start_sun_rise:end_sun_rise] = \
            day_scale * np.sin([i * np.pi / (end_sun_rise - start_sun_rise)
                                for i in range(0, end_sun_rise - start_sun_rise)])
        values[day, :] = per_day_values

    return values


def generate_wind_speed_days(days: int = 14, scale: int = 100, resolution: int = 900) \
        -> np.ndarray:
    values = np.zeros((days, int(24 * 3600 / resolution)))
    r = default_rng()
    samples = int(24 * 3600 / resolution)

    for day in range(0, days):
        day_scale = scale * r.random(1)
        per_day_values = day_scale * np.sin(r.uniform(size=samples, low=-np.pi, high=np.pi))
        values[day, :] = per_day_values

    return values


def create_pv_plant(initial_timestamp: int = 1639396720, past_days: int = 4, future_days: int = 10):
    power = [p if p <= 1000 else 1000 for p in list(range(0, 1500, 100))]
    power = [0 if p <= 200 else p for p in power]
    irradiance = list(range(0, 15 * 15, 15))
    irradiance_to_power = SamplePointsToPowerTable(points=irradiance, power_values=power)
    initial_timestamp = initial_timestamp
    irradiance_values = generate_solar_irradiance_days(days=14, resolution=900, scale=100)
    irradiance_values = irradiance_values.reshape((1, irradiance_values.size))[0]
    irradiance_time_series = SimulationTimeSeries(
        timestamps=list(range(initial_timestamp - past_days * 24 * 3600,
                              initial_timestamp + future_days * 24 * 3600, 900)),
        values=irradiance_values
    )
    pv_data_loader = RenewableUnitDataLoader(initial_timestamp=initial_timestamp,
                                             sample_point_to_power=irradiance_to_power,
                                             simulation_time_series=irradiance_time_series)

    pv_plant = RenewablePowerUnit(name='pv_model', data_loader=pv_data_loader)

    return pv_plant


class MockComponentDataLoader(IComponentDataLoader):
    def __init__(self, initial_timestamp: int, data: ComponentSimulationData):
        super().__init__(initial_timestamp)
        self.data = data


class MockComponent(IComponent):
    def __init__(self, name: str, data_loader: MockComponentDataLoader):
        super().__init__(name, data_loader)
        self._data_loader = data_loader

    def step(self, timestamp: int):
        self._check_step_timestamp(timestamp)

    def current_simulation_data(self) -> ComponentSimulationData:
        return self._data_loader.data


class MockGeneratorDataLoader(IGeneratorDataLoader):
    pass


class MockGeneratorUnit(IGeneratorComponent):
    def step(self, timestamp: int):
        self._check_step_timestamp(timestamp)
        self._current_power = self.power_setpoint


class MockGridNetwork(IGridNetwork):
    def __init__(self, name: str, data_loader: MockComponentDataLoader,
                 buses: List[BUS_ID]):
        super().__init__(name, data_loader)
        self._data_loader = data_loader
        self._buses = buses
        self._bus_power = np.zeros(len(buses))
        self._current_power = np.zeros(len(buses))

    @property
    def buses(self):
        return self._buses

    def validate_grid_model(self) -> bool:
        return True

    def set_bus_power(self, bus_id: BUS_ID, power: float):
        try:
            self._current_power[self._buses.index(bus_id)] = power
        except Exception:
            raise ValueError(f'{bus_id} not in the grid buses')

    def step(self, timestamp: int):
        pass


@dataclass
class MockComponentDataLoaderData(IComponentDataLoaderData):
    data: ComponentSimulationData


@dataclass
class MockUnitConfigData(IUnitConfigData):
    data_loader_data: MockComponentDataLoaderData


class MockUnitConfig(IUnitConfig):
    def __init__(self, config_data: MockUnitConfigData):
        super().__init__(config_data)
        self.initial_timestamp = config_data.initial_timestamp

    def create_unit(self) -> IComponent:
        data_loader = self.create_data_loader()
        return MockComponent(self.name, data_loader)

    def create_data_loader(self) -> MockComponentDataLoader:
        return MockComponentDataLoader(
            self.initial_timestamp, self.data_loader_data.data
        )


@dataclass
class MockGeneratorDataLoaderData(IComponentDataLoaderData):
    power_bounds: Bounds


@dataclass
class MockGeneratorConfigData(IGeneratorConfigData):
    data_loader_data: MockGeneratorDataLoaderData


class MockGeneratorConfig(IGeneratorComponentConfig):
    def __init__(self, config_data: MockGeneratorConfigData,
                 # name: str, data_loader: MockGeneratorDataLoader, bus_id: BUS_ID,
                 # component_type: ComponentType = ComponentType.Unknown
                 ):
        super().__init__(config_data)
        self.config_data = config_data
        # self.data_loader = data_loader
        # self._component_type = component_type

    def create_unit(self):
        data_loader = self.create_data_loader()
        return MockGeneratorUnit(self.name, data_loader)

    def create_data_loader(self) -> MockGeneratorDataLoader:
        return MockGeneratorDataLoader(
            self.config_data.initial_timestamp, self.data_loader_data.power_bounds
        )
