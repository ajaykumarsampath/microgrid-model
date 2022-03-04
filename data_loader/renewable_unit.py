from data_loader.power_unit import IUnitDataLoader
from model.domain import SimulationTimeSeries, Bounds
from data_loader.domain import SamplePointsToPowerTable
import logging

logger = logging.getLogger(__name__)

class IRenewableUnitDataLoader(IUnitDataLoader):
    def get_data(self, timestamp: int):
        raise NotImplementedError

class RenewableUnitDataLoader(IRenewableUnitDataLoader):
    def __init__(self, initial_timestamp: int, sample_point_to_power: SamplePointsToPowerTable,
                 simulation_time_series: SimulationTimeSeries):

        power_bounds = Bounds(min = sample_point_to_power.minimum(),
                                    max = sample_point_to_power.maximum())

        super().__init__(initial_timestamp=initial_timestamp, power_bounds=power_bounds)

        self._simulation_time_series = simulation_time_series
        self._sample_point_to_power = sample_point_to_power
        self._min_simulation_timestamp = min(simulation_time_series.timestamps)
        self._max_simulation_timestamp = max(simulation_time_series.timestamps)

    def get_data(self, timestamp: int):
        if self._min_simulation_timestamp <= timestamp <= self._max_simulation_timestamp:
            sample_data = self._simulation_time_series.resample(timestamp=timestamp)
            return self._sample_point_to_power.available_power_at_sample_point(sample_data)
        else:
            logger.warning("cannot get data at the timestamp")
            return 0