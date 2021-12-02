from microgrid.model.domain import Bounds, SamplePointsToPowerTable, SimulationTimeSeries, UnitSimulationData
from microgrid.model.power_unit import PowerUnit
import logging

logger = logging.getLogger(__name__)


class IRenewablePowerUnit(PowerUnit):
    def __init__(self, name: str, initial_timestamp: int,
                 sample_point_to_power: SamplePointsToPowerTable,
                 simulation_time_series: SimulationTimeSeries):
        power_bounds = Bounds(min = sample_point_to_power.minimum(),
                              max = sample_point_to_power.minimum())
        super().__init__(name = name, initial_timestamp = initial_timestamp,
                         power_bounds = power_bounds)
        min_simulation_timestamp = min(simulation_time_series.timestamps)
        max_simulation_timestamp = max(simulation_time_series.timestamps)
        assert min_simulation_timestamp <= initial_timestamp <= max_simulation_timestamp

        self._sample_point_to_power = sample_point_to_power
        self.__simulation_time_series = simulation_time_series
        self._available_power = 0
        self._add_simulation_data(timestamp = initial_timestamp,
                                  data=self._generate_simulation_data())


    def calculate_available_power(self, timestamp: int):
        assert timestamp >= self.get_initial_timestamp()
        sample_data = self.__simulation_time_series.resample(timestamp=timestamp)
        return self._sample_point_to_power.available_power_at_sample_point(sample_data)

    def step(self, timestamp: int):
        self._available_power = self.calculate_available_power(timestamp=timestamp)
        self._current_power = min(self._available_power, self.power_setpoint)
        self._add_simulation_data(timestamp=timestamp,
                                  data=self._generate_simulation_data())

    def _generate_simulation_data(self):
        values = {'current_power': self._current_power, 'available_power': self._available_power,
                  'power_setpoint': self._power_setpoint}
        return UnitSimulationData(values=values)


class PVPlant(IRenewablePowerUnit):
    def __init__(self, name: str, initial_timestamp: int,
                 irradiation_to_power: SamplePointsToPowerTable,
                 simulation_time_series: SimulationTimeSeries, forecaster=None):
        super().__init__(name, initial_timestamp, irradiation_to_power, simulation_time_series)
        self.forecaster = forecaster


class WindTurbine(IRenewablePowerUnit):
    def __init__(self, name: str, initial_timestamp: int,
                 irradiation_to_power: SamplePointsToPowerTable,
                 simulation_time_series: SimulationTimeSeries, forecaster=None):
        super().__init__(name, initial_timestamp, irradiation_to_power, simulation_time_series)
        self.forecaster = forecaster
