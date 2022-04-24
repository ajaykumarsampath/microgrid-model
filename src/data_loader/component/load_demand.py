import logging

from data_loader.domain import UnitDataLoaderError
from data_loader.interface import ILoadDemandDataLoader
from shared.timeseries import SimulationTimeSeries

logger = logging.getLogger(__name__)


class LoadDemandDataLoader(ILoadDemandDataLoader):
    def __init__(self, initial_timestamp: int, demand_time_series: SimulationTimeSeries):
        super().__init__(initial_timestamp)
        self._demand_time_series = demand_time_series
        self._min_demand_timestamp = min(demand_time_series.timestamps)
        self._max_demand_timestamp = max(demand_time_series.timestamps)
        if initial_timestamp > self._max_demand_timestamp:
            raise UnitDataLoaderError(f'load demand simulation timestamps are '
                                      f'past compared to the initial time')


    def get_data(self, timestamp: int):
        if self._min_demand_timestamp <= timestamp <= self._max_demand_timestamp:
            return self._demand_time_series.resample(timestamp=timestamp)
        else:
            logger.warning(f'cannot get the data at the timestamp' )
            return 0
