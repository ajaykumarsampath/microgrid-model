from data_loader.interface import IRenewableUnitDataLoader
from data_loader.domain import SamplePointsToPowerTable, UnitDataLoaderError
import logging

from shared.component import Bounds
from shared.timeseries import SimulationTimeSeries, Timestamp

logger = logging.getLogger(__name__)


class RenewableUnitDataLoader(IRenewableUnitDataLoader):
    def __init__(self, initial_timestamp: Timestamp,
                 sample_point_to_power: SamplePointsToPowerTable,
                 simulation_time_series: SimulationTimeSeries):

        power_bounds = Bounds(
            min=sample_point_to_power.minimum(), max=sample_point_to_power.maximum()
        )

        super().__init__(initial_timestamp=initial_timestamp, power_bounds=power_bounds)

        self._simulation_time_series = simulation_time_series
        self._sample_point_to_power = sample_point_to_power
        self._min_simulation_timestamp = min(simulation_time_series.timestamps)
        self._max_simulation_timestamp = max(simulation_time_series.timestamps)
        if initial_timestamp > self._max_simulation_timestamp:
            raise UnitDataLoaderError('renewable unit simulation timestamps are '
                                      'past compared to the initial time')

    def get_data(self, timestamp: int):
        if self._min_simulation_timestamp <= timestamp <= self._max_simulation_timestamp:
            sample_data = self._simulation_time_series.resample(timestamp=timestamp)
            return self._sample_point_to_power.available_power_at_sample_point(sample_data)
        else:
            logger.warning("cannot get data at the timestamp")
            return 0
