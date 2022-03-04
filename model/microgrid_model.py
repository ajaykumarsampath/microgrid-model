import logging
from dataclasses import dataclass
from functools import cached_property
from typing import List
import numpy as np

from model.domain import BUS_ID, MicrogirdModellingError, UnknownComponentError, StepPreviousTimestamp, \
    SimulationGridError
from model.component_interface import IComponent, IGridNetwork
from model.generator_interface import IGeneratorComponent
from util.storage import IUnitDataStorage

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class MicrogridModelData:
    name: str
    generators: List[IGeneratorComponent]
    loads: List[IComponent]
    grid_model: IGridNetwork
    generator_bus_ids: List[BUS_ID]
    load_bus_ids: List[BUS_ID]

    @cached_property
    def model_bus_ids(self) -> List[BUS_ID]:
        unique_bus = []
        for i, e in enumerate(self.generator_bus_ids + self.load_bus_ids):
            if e not in unique_bus:
                unique_bus.append(e)
        return unique_bus

    @cached_property
    def valid_data(self):
        grid_buses = self.grid_model.buses
        try:
            self._check_non_unique_ids(self.generators)
            self._check_non_unique_ids(self.loads)
            assert len(self.generators) == len(self.generator_bus_ids)
            assert len(self.loads) == len(self.load_bus_ids)
            assert len(grid_buses) == len(self.model_bus_ids)
            assert all([bus in self.model_bus_ids for bus in grid_buses])
            return self.grid_model.validate_grid_model()
        except AssertionError:
            return False

    def _check_non_unique_ids(self, components: List[IComponent]):
        component_names = [c.name for c in components]
        assert len(component_names) == len(set(component_names))

    def unit_bus_matrix(self):
        num_generators = len(self.generator_bus_ids)
        num_loads = len(self.load_bus_ids)
        cols_unit_bus_mat = len(self.model_bus_ids)
        _unit_bus_mat = np.zeros((num_generators + num_loads, cols_unit_bus_mat))

        for count, bus_id in enumerate(self.generator_bus_ids):
            bus_id_index = self.model_bus_ids.index(bus_id)
            _unit_bus_mat[count, bus_id_index] = 1

        for count, bus_id in enumerate(self.load_bus_ids):
            bus_id_index = self.model_bus_ids.index(bus_id)
            _unit_bus_mat[count + num_generators, bus_id_index] = 1

        return _unit_bus_mat

class MicrogridModel:
    def __init__(self, microgrid_model_data: MicrogridModelData):
        if microgrid_model_data.valid_data:
            self._name = microgrid_model_data.name
            self._model_data = microgrid_model_data
            self._generator_bus_ids = microgrid_model_data.generator_bus_ids
            self._load_bus_ids = microgrid_model_data.load_bus_ids
            self._unit_to_bus = microgrid_model_data.unit_bus_matrix()
            self._generator_ids = [g.name for g in self._model_data.generators]
            self._load_ids = [l.name for l in self._model_data.loads]
        else:
            raise MicrogirdModellingError(f'Microgrid data is not valid at '
                                          f'{microgrid_model_data.name}')

    @property
    def name(self):
        return self._name

    @property
    def generators(self):
        return self._model_data.generators

    @property
    def loads(self):
        return self._model_data.loads

    @property
    def grid_model(self):
        return self._model_data.grid_model

    @property
    def current_power(self) -> np.array:
        num_generators = len(self._generator_ids)
        num_loads = len(self._load_ids)
        power = np.zeros(num_generators + num_loads)

        for count, unit in enumerate(self.generators):
            power[count] = unit._current_power

        for count, unit in enumerate(self.loads):
            power[num_generators + count] = unit._current_power

        return power

    def get_current_power(self, unit_id: str):
        if unit_id in self._generator_ids:
            return self.generators[self._generator_ids.index[unit_id]].current_power
        elif unit_id in self._load_ids:
            return self.loads[self._load_ids.index[unit_id]].current_power
        else:
            raise UnknownComponentError(f'unit {unit_id} to getting is not in microgrid')


    def convert_unit_power_bus_power(self, power: np.array):
        try:
            return self._unit_to_bus.T@power
        except Exception as err:
            raise UnknownComponentError(f'input power and bus dimension does not match {err}')

    def set_power_setpoint(self, unit_id: str, power: float):
        try:
            self.generators[self._generator_ids.index(unit_id)].power_setpoint = power
        except IndexError:
            raise UnknownComponentError(f'unit {unit_id} trying to set power is not in microgrid')


    def set_power_setpoints(self, power_setpoints: List[float]):
        try:
            assert len(power_setpoints) == len(self.generators)
            for power, unit in zip(power_setpoints, self.generators):
                unit.power_setpoint = power
        except AssertionError:
            logger.warning("Power set points cannot be set as the length is not sufficient")

    @cached_property
    def sum_inverse_droop_gain(self):
        inverse_droop = [g.droop_gain_inverse() for g in self.generators]
        return sum(inverse_droop)

    def calculate_delta_frequency(self):
        delta_power = 0
        for load in self.loads:
            delta_power = delta_power + load.current_power

        for generator in self.generators:
            if generator.is_grid_forming_unit():
                delta_power = delta_power + generator.power_setpoint
            else:
                delta_power = delta_power + generator.current_power

        if self.sum_inverse_droop_gain > 0:
            return 1/self.sum_inverse_droop_gain * delta_power
        else:
            logger.warning("sum of droop gain inverse is zero.")
            return 0

    def step(self, timestamp: int):
        try:
            for load in self.loads:
                load.step(timestamp)

            for unit in self.generators:
                if not unit.is_grid_forming_unit():
                    unit.step(timestamp=timestamp)

            delta_frequency = self.calculate_delta_frequency()

            for unit in self.generators:
                if unit.is_grid_forming_unit():
                    unit.participate_power_sharing(delta_frequency)
                    unit.step(timestamp)

            bus_power = self.convert_unit_power_bus_power(self.current_power)

            for bus_id, power in zip(self._model_data.model_bus_ids, bus_power):
                self.grid_model.set_bus_power(bus_id, power)

            self.grid_model.step(timestamp)

        except StepPreviousTimestamp:
            raise StepPreviousTimestamp(f'timestamps at {self.name} is at historical timestamp')
        except SimulationGridError as err:
            raise SimulationGridError(f'{err}')


    def add_simulation_data(self, data_storage: IUnitDataStorage):
        for generator in self.generators:
            generator.add_simulation_data(data_storage)

        for load in self.loads:
            load.add_simulation_data(data_storage)

        self.grid_model.add_simulation_data(data_storage)
