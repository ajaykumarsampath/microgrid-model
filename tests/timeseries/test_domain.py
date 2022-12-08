import numpy as np
import pytest

from common.timeseries.domain import Bounds, Timestamps, TimeseriesData, UnknownTimestampError, BoundTimeseries, \
    ConstantTimeseriesData
from datetime import datetime, timedelta


def test_timestamps():
    timestamp = [(datetime(2022, 10, 1) + timedelta(minutes=i)).timestamp()
                 for i in range(0, 10)]
    timestamps = Timestamps(timestamp)
    for i, t in enumerate(timestamps):
        assert t == timestamp[i]

    with pytest.raises(UnknownTimestampError):
        timestamp = [(datetime(2022, 10, 1) + timedelta(minutes=i)).timestamp()
                     for i in range(0, 10)]
        timestamps = Timestamps(timestamp)
        timestamps.get_timestamp_index(100)

    with pytest.raises(AssertionError):
        timestamp = [(datetime(2022, 10, 1) - timedelta(minutes=i)).timestamp()
                 for i in range(0, 3)]
        Timestamps(timestamp)


def test_timeseries():
    timestamp = [(datetime(2022, 10, 1) + timedelta(minutes=i)).timestamp()
                 for i in range(0, 10)]
    timestamps = Timestamps(timestamp)
    values = np.arange(0, 10)
    data = TimeseriesData(timestamps, values=values)

    for v, t in zip(values, timestamps):
        assert data.get_value(t) == v

    with pytest.raises(UnknownTimestampError):
        data.get_value(100)

    constant_data = ConstantTimeseriesData(timestamps, value=10)
    for t in timestamps:
        assert constant_data.get_value(t) == v

    with pytest.raises(UnknownTimestampError):
        constant_data.get_value(100)



def test_bounds():
    bound = Bounds(0, 10)
    assert bound.min == 0
    assert bound.max == 10
    with pytest.raises(ValueError):
        Bounds(10, 0)

    t = [(datetime(2022, 10, 1) + timedelta(minutes=i)).timestamp()
                 for i in range(0, 3)]
    timestamps = Timestamps(t)

    time_series_bounds = BoundTimeseries(
        min=ConstantTimeseriesData(timestamps, 0),
        max=ConstantTimeseriesData(timestamps, 10))

    for t in timestamps:
        assert time_series_bounds.get_value(t)[0] == 0
        assert time_series_bounds.get_value(t)[1] == 10

    min_value = [0, 0, 0]
    max_value = [1, 2, 3]
    time_series_bounds = BoundTimeseries(
        min=TimeseriesData(timestamps, min_value),
        max=TimeseriesData(timestamps, max_value)
    )

    for i, t in enumerate(timestamps):
        assert time_series_bounds.get_value(t)[0] == min_value[i]
        assert time_series_bounds.get_value(t)[1] == max_value[i]