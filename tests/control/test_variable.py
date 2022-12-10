from typing import List, Union

from control.optimisation_engine.domain import IBaseVariable, IExpression, BaseVariable, ITimeIndexBaseModel, \
    UnknownTimestampError, ConstraintType
from control.optimisation_engine.variable import TimeIndexConstraint
from microgrid.shared.timeseries import Timestamp
from common.timeseries.domain import Timestamps
import pytest


class MockBaseVariable(IBaseVariable):
    def __init__(self, value: float):
        self._value = value

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

    def get_value_timestamp(self, timestamp: Timestamp) -> Union[BaseVariable, IExpression]:
        return self._get_value_timestamp(timestamp)


class MockTimeseriesParameter(ITimeIndexBaseModel):
    def __init__(self, timestamps: Timestamps, value: List[float]):
        self._timestamps = timestamps
        self._value = value
        self._name = 'mock_parameter'

    @property
    def name(self) -> str:
        return self._name

    @property
    def timestamps(self) -> Timestamps:
        return self._timestamps

    @property
    def value(self) -> List[float]:
        return self._value


class MockTimeseriesConstraint(TimeIndexConstraint):
    def __init__(self, name: str, timestamps: Timestamps,
                 constraint_expression: List[ConstraintType]):
        super().__init__(name, timestamps, constraint_expression)
        self._value = constraint_expression

    @property
    def timestamps(self) -> Timestamps:
        return self._timestamps

    @property
    def value(self) -> List[IExpression]:
        return self._value


class TestTimeseriesData:
    def test_get_value_timestamp(self):
        timestamps = Timestamps([1, 2, 3, 4])
        variable_1 = [MockBaseVariable(i) for i in range(0, len(timestamps.values))]
        timeseries_variable_1 = MockTimeseriesData(timestamps, variable_1)
        values = [i for i in range(0, len(timestamps.values))]
        timeseries_parameter_1 = MockTimeseriesParameter(timestamps, values)

        constraint_1 = [vb + va <= 0 for vb, va in zip(variable_1, values)]
        timeseries_constraint_1 = MockTimeseriesConstraint(
            'constraint', timestamps, constraint_1)

        for i, t in enumerate(timestamps.values):
            v = timeseries_variable_1.get_value_timestamp(t)
            assert timeseries_parameter_1.value[i] == values[i]
            assert v.value == variable_1[i].value
            assert timeseries_constraint_1.get_value_timestamp(t) is constraint_1[i]

    def test_unknown_timestamp(self):
        timestamps = Timestamps([1, 2, 3, 4])
        variable_1 = [MockBaseVariable(i) for i in range(0, len(timestamps.values))]
        timeseries_variable_1 = MockTimeseriesData(timestamps, variable_1)
        with pytest.raises(UnknownTimestampError):
            timeseries_variable_1.get_value_timestamp(10)
