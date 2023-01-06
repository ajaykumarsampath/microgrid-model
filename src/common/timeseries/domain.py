from dataclasses import dataclass
from typing import List, Union, Optional

Timestamp = Union[int, float]


@dataclass
class Timestamps:
    values: List[Timestamp]

    def __len__(self):
        return len(self.values)

    def __post_init__(self):
        try:
            assert all([self.values[i + 1] - self.values[i] > 0
                        for i, t in enumerate(self.values) if i < len(self.values) - 1])
            assert all([t >= 0 for t in self.values])
            self._iter = 0
        except AssertionError:
            raise AssertionError('Timestamp values can take only positive and increasing values')

    def get_timestamp_index(self, timestamp: Timestamp):
        try:
            return self.values.index(timestamp)
        except ValueError:
            raise UnknownTimestampError(f'timestamp {timestamp} is not part of the timestamps')

    def __next__(self):
        self._iter = self._iter + 1
        if self._iter <= len(self.values):
            return self.values[self._iter - 1]
        else:
            self._iter = 0
            raise StopIteration

    def __iter__(self):
        return self

    def __getitem__(self, item):
        return self.values[item]

    def slice(self, from_index: int, to_index: int, delta: int = 1):
        return Timestamps(self.values[from_index:to_index:delta])


@dataclass
class TimeseriesData:
    timestamps: Timestamps
    values: List[Optional[float]]

    def __post_init__(self):
        try:
            assert len(self.values) == len(self.timestamps.values)
        except AssertionError:
            raise AssertionError('data and timestamps are not of the same size')

    def get_value(self, timestamp: Timestamp):
        index = self.timestamps.get_timestamp_index(timestamp)
        return self.values[index]


@dataclass
class ConstantTimeseriesData:
    timestamps: Timestamps
    value: Optional[float]

    def get_value(self, timestamp: Timestamp):
        self.timestamps.get_timestamp_index(timestamp)
        return self.value

    @property
    def values(self):
        return [self.value for _ in self.timestamps]


@dataclass
class Bounds:
    min: float
    max: float

    def __post_init__(self):
        if self.min > self.max:
            raise ValueError('Bounds are not correct: min should be less than max')


TimeseriesModel = Union[TimeseriesData, ConstantTimeseriesData]


@dataclass
class BoundTimeseries:
    min: TimeseriesModel
    max: TimeseriesModel

    def __post_init__(self):
        try:
            assert len(self.min.timestamps.values) == len(self.max.timestamps.values)
            assert all([t_1 == t_2 for t_1, t_2 in zip(self.min.timestamps.values,
                                                       self.max.timestamps.values)])
            assert all([self.min.get_value(t) < self.max.get_value(t)
                        for t in self.min.timestamps.values])
        except AssertionError:
            raise AssertionError('min value, max value have either unequal to timestamps '
                                 'or max value less than min value')

    @classmethod
    def constant_bound_timeseries(cls, timestamps: Timestamps, min_value: float,
                                  max_value: float) -> 'BoundTimeseries':
        return cls(ConstantTimeseriesData(timestamps, min_value),
                   ConstantTimeseriesData(timestamps, max_value))


    def get_value(self, timestamp: Timestamp) -> (float, float):
        return (self.min.get_value(timestamp), self.max.get_value(timestamp))

    def get_value_as_bound(self, timestamp: Timestamp) -> Bounds:
        return Bounds(self.min.get_value(timestamp), self.max.get_value(timestamp))

    @property
    def timestamps(self):
        return self.min.timestamps


class UnknownTimestampError(Exception):
    pass
