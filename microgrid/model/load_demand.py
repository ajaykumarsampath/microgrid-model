from microgrid.model.domain import SimulationTimeSeries, Bounds, UnitSimulationData
from microgrid.model.power_unit import PowerUnit, UnitDataStorage, Unit


class LoadDemand(Unit):
    def __init__(self, name: str, initial_timestamp: int,
                 demand_time_series: SimulationTimeSeries):

        super().__init__(name, initial_timestamp)
        min_demand_timestamp = min(demand_time_series.timestamps)
        max_demand_timestamp = max(demand_time_series.timestamps)
        assert min_demand_timestamp <= initial_timestamp <= max_demand_timestamp

        self.__demand_time_series = demand_time_series
        self._add_simulation_data(timestamp=initial_timestamp,
                                  data=self._generate_simualation_data())

    def _generate_simulation_data(self):
        values = {'current_power': self._current_power}
        return UnitSimulationData(values=values)

    def step(self, timestamp: int):
        self._current_power = self.__demand_time_series.resample(timestamp=timestamp)
        self._add_simulation_data(timestamp, data=self._generate_simulation_data())
