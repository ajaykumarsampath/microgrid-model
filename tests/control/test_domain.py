from typing import List

from common.timeseries.domain import Timestamps, Timestamp
from control.optimisation_engine.domain import IBaseVariable, ITimeIndexBaseModel


class MockBaseVariable(IBaseVariable):
    def __init__(self, value: float):
        self._value = value
        self._name = f'mock_var_{value}'

    @property
    def name(self) -> str:
        return self._name

    @property
    def value(self):
        return self._value


class MockTimeseriesData(ITimeIndexBaseModel):
    def __init__(self, timestamps: Timestamps, value: List[MockBaseVariable]):
        assert len(timestamps.values) == len(value)
        self._timestamps = timestamps
        self._value = value
        self._name = 'mock_timeindex_var'

    @property
    def timestamps(self) -> Timestamps:
        return self._timestamps

    @property
    def value(self):
        return self._value

    @property
    def name(self) -> str:
        return self._name

    def get_value_timestamp(self, timestamp: Timestamp) -> float:
        return self._get_value_timestamp(timestamp)


class TestVariableInterface:
    def test_variable(self):
        a = MockBaseVariable(2)
        b = MockBaseVariable(3)
        print((a < b).value)
        print(a.value)

    def test_sum_expression(self):
        a = MockBaseVariable(2)
        b = MockBaseVariable(3)
        c = a + b
        d = c + 1
        assert c.value == 5
        assert d.value == 6

    def test_subtraction_expression(self):
        a = MockBaseVariable(2)
        b = MockBaseVariable(3)
        c = a - b
        d = c - 1
        assert c.value == -1
        assert d.value == -2

    def test_product_expression(self):
        a = MockBaseVariable(2)
        b = MockBaseVariable(3)
        c = a * b
        d = c * -1
        assert c.value == 6
        assert d.value == -6

    def test_division_expression(self):
        a = MockBaseVariable(2)
        b = MockBaseVariable(3)
        c = a / b
        d = c / -3
        assert c.value == 2 / 3
        assert d.value == -2 / 9

    def test_greater_expression(self):
        a = MockBaseVariable(2)
        b = MockBaseVariable(3)
        c = b > a
        d = a <= 2
        assert c.value
        assert d.value

    def test_lesser_expression(self):
        a = MockBaseVariable(2)
        b = MockBaseVariable(3)
        c = a < b
        d = a >= 2
        assert c.value
        assert d.value

    def test_algorithm_expression_timeindex_model(self):
        timestamps = Timestamps(values=[1, 2, 3, 4])
        value_1 = [10, 20, 30, 40]
        value = [MockBaseVariable(v) for v in value_1]
        a = MockTimeseriesData(timestamps, value)
        b = MockTimeseriesData(timestamps, value)
        c = MockTimeseriesData(timestamps, [MockBaseVariable(0) for _ in value])
        d = a + b + c
        assert all([d[i] == 2 * value_1[i] for i, _ in enumerate(timestamps)])
        d = 0 * d + 1
        assert all([d[i] == 1 for i, _ in enumerate(timestamps)])

    def test_logical_expression_timeindex_model(self):
        timestamps = Timestamps(values=[1, 2, 3, 4])
        value_1 = [10, 20, 30, 40]
        value = [MockBaseVariable(v) for v in value_1]
        a = MockTimeseriesData(timestamps, value)
        b = MockTimeseriesData(timestamps, value)
        d = a == b
        assert all([d[i] for i, t in enumerate(timestamps)])
        d = a <= 1
        assert all([not d[i] for i, t in enumerate(timestamps)])
