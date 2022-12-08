from dataclasses import dataclass

from common.timeseries.domain import Timestamp, Timestamps
from control.optimisation_engine.interface import IOptimisationEngine


@dataclass
class Horizon:
    since: Timestamp
    until: Timestamp
    sampling_time: int
    # relative: bool = True

    def __post_init__(self):
        try:
            assert self.since >= 0 and self.until >= 0 and self.sampling_time >= 0
            assert self.until - self.since >= 0
            self.timestamps = Timestamps([t for t in range(self.since, self.until,
                                                           self.sampling_time)])
        except AssertionError:
            raise AssertionError('since and until is positive and until greater than since')


class IControlComponent:
    @property
    def timestamp(self):
        raise NotImplementedError

    @property
    def power(self):
        raise NotImplementedError

    def _generate_variables(self):
        raise NotImplementedError

    def _generate_constraint(self):
        raise NotImplementedError

    def extend_optimisation_model(self, optimisation_engine: IOptimisationEngine):
        raise NotImplementedError

    def get_results(self):
        raise NotImplementedError
