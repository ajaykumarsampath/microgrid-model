from enum import Enum
from typing import Union, Any, List

from common.timeseries.domain import Timestamps, Timestamp

class VariableType(Enum):
    Binary = 'binary'
    Continuous = 'continuous'

class OptimisationVaraibleType(Enum):
    variable = 'variable'
    parameter = 'parameter'


class IOptimisationVariable:
    @property
    def value(self):
        raise NotImplementedError

    def evaluate(self):
        raise NotImplementedError

    @property
    def type(self):
        raise NotImplementedError


class IOptimisationIndexVariable:
    def _at_index(self, index: int):
        raise NotImplementedError

    @property
    def value(self):
        raise NotImplementedError

    def __getitem__(self, index: int):
        return self._at_index(index)

    def evaluate(self):
        raise NotImplementedError


class OptimisationExpression:
    def __init__(self, value: Any):
        self._value = value

    @property
    def value(self):
        return self._value

    def __getitem__(self, item):
        return self._value[item]


class IBaseVariable:
    @property
    def value(self) -> Union[IOptimisationVariable, float]:
        raise NotImplementedError

    @property
    def name(self) -> str:
        raise NotImplementedError

    @value.setter
    def value(self, var: Union[IOptimisationVariable, float]):
        raise NotImplementedError

    def __repr__(self):
        return f'Control variable {self.name}'

    def __add__(self, other):
        return SumExpression(self, other)

    def __radd__(self, other):
        return SumExpression(self, other)

    def __sub__(self, other):
        return SubtractExpression(self, other)

    def __rsub__(self, other):
        return SubtractExpression(self, other)

    def __mul__(self, other):
        return MultiplicationExpression(self, other)

    def __rmul__(self, other):
        return MultiplicationExpression(self, other)

    def __truediv__(self, other):
        return DivisionExpression(self, other)

    def __rtruediv__(self, other):
        return DivisionExpression(self, other)

    def __ge__(self, other):
        return GreaterEqualExpression(self, other)

    def __le__(self, other):
        return LesserEqualExpression(self, other)

    def __gt__(self, other):
        return GreaterExpression(self, other)

    def __lt__(self, other):
        return LesserExpression(self, other)

    def __eq__(self, other):
        return EqualExpression(self, other)

    def __neg__(self):
        return MultiplicationExpression(self, -1)


BaseVariable = Union[IBaseVariable, float, int, OptimisationExpression]


class IExpression(IBaseVariable):
    def __init__(self, variable_1: BaseVariable, variable_2: BaseVariable):
        self.variable_1 = variable_1
        self.variable_2 = variable_2

    def _get_value(self, variable):
        while isinstance(variable, OptimisationExpression) or isinstance(variable, IBaseVariable) or \
                isinstance(variable, IOptimisationVariable):
            variable = variable.value

        return variable

    @property
    def name(self):
        return 'Expression'

    def _get_variable_values(self):
        try:
            value_1 = self._get_value(self.variable_1)
            value_2 = self._get_value(self.variable_2)
            return value_1, value_2
        except NotImplementedError as e:
            raise UndefinedValueError('cannot get values to evaluate the expression: '
                                      f'{e}')

    @property
    def value(self) -> OptimisationExpression:
        raise NotImplementedError

    def evaluate(self):
        return self.value.value


class SumExpression(IExpression):
    @property
    def value(self):
        value_1, value_2 = self._get_variable_values()
        return OptimisationExpression(value_1 + value_2)

    def evaluate(self):
        return self.value.value

    def __repr__(self):
        return f'{self.variable_1} + {self.variable_2}'


class SubtractExpression(IExpression):
    @property
    def value(self):
        value_1, value_2 = self._get_variable_values()
        return OptimisationExpression(value_1 - value_2)

    def __repr__(self):
        return f'{self.variable_1} - {self.variable_2}'


class MultiplicationExpression(IExpression):
    @property
    def value(self):
        value_1, value_2 = self._get_variable_values()
        return OptimisationExpression(value_1 * value_2)

    def __repr__(self):
        return f'{self.variable_1} * {self.variable_2}'


class DivisionExpression(IExpression):
    @property
    def value(self):
        value_1, value_2 = self._get_variable_values()
        return OptimisationExpression(value_1 / value_2)

    def __repr__(self):
        return f'{self.variable_1} / {self.variable_2}'


class EqualExpression(IExpression):
    @property
    def value(self):
        value_1, value_2 = self._get_variable_values()
        return OptimisationExpression(value_1 == value_2)

    def __repr__(self):
        return f'{self.variable_1} == {self.variable_2}'


class GreaterExpression(IExpression):
    @property
    def value(self):
        value_1, value_2 = self._get_variable_values()
        return OptimisationExpression(value_1 > value_2)

    def __repr__(self):
        return f'{self.variable_1} > {self.variable_2}'


class LesserExpression(IExpression):
    @property
    def value(self):
        value_1, value_2 = self._get_variable_values()
        return OptimisationExpression(value_1 < value_2)

    def __repr__(self):
        return f'{self.variable_1} < {self.variable_2}'


class GreaterEqualExpression(IExpression):
    @property
    def value(self):
        value_1, value_2 = self._get_variable_values()
        return OptimisationExpression(value_1 >= value_2)

    def __repr__(self):
        return f'{self.variable_1} >= {self.variable_2}'


class LesserEqualExpression(IExpression):
    @property
    def value(self):
        value_1, value_2 = self._get_variable_values()
        return OptimisationExpression(value_1 <= value_2)

    def __repr__(self):
        return f'{self.variable_1} <= {self.variable_2}'


ConstraintType = Union[EqualExpression, GreaterExpression, GreaterEqualExpression,
                       LesserEqualExpression, LesserExpression]
ObjectiveType = Union[SumExpression, SubtractExpression, MultiplicationExpression,
                      DivisionExpression]


class ITimeIndexBaseModel:
    @property
    def value(self) -> List[IBaseVariable]:
        raise NotImplementedError

    @property
    def optimisation_value(self) -> IOptimisationIndexVariable:
        raise NotImplementedError

    @optimisation_value.setter
    def optimisation_value(self, value: IOptimisationIndexVariable):
        raise NotImplementedError

    @property
    def name(self) -> str:
        raise NotImplementedError

    @property
    def timestamps(self) -> Timestamps:
        raise NotImplementedError

    def _get_value_timestamp(self, timestamp: Timestamp):
        try:
            return self.value[self.timestamps.values.index(timestamp)]
        except (IndexError, ValueError):
            raise UnknownTimestampError(f'timestamp {timestamp} is not part of the timestamps defined')

    def _get_value_index(self, index: int):
        try:
            return self.value[index]
        except (IndexError, ValueError):
            raise UnknownTimestampError(f'index {index} is not part of the timestamps defined')

    def get_value_timestamp(self, timestamp: Timestamp):
        raise NotImplementedError

    def __repr__(self):
        return f'Control variable {self.name}'

    def __getitem__(self, index):
        return self.value[index]

    def __len__(self):
        return len(self.value)

    def __add__(self, other):
        return SumTimeIndexExpression(self.timestamps, self, other)

    def __radd__(self, other):
        return SumTimeIndexExpression(self.timestamps, self, other)

    def __sub__(self, other):
        return SubtractTimeIndexExpression(self.timestamps, self, other)

    def __rsub__(self, other):
        return SubtractTimeIndexExpression(self.timestamps, self, other)

    def __mul__(self, other):
        return MultiplicationTimeIndexExpression(self.timestamps, self, other)

    def __rmul__(self, other):
        return MultiplicationTimeIndexExpression(self.timestamps, self, other)

    def __truediv__(self, other):
        return DivisionTimeIndexExpression(self.timestamps, self, other)

    def __rtruediv__(self, other):
        return DivisionTimeIndexExpression(self.timestamps, self, other)

    def __ge__(self, other):
        return GreaterEqualTimeIndexExpression(self.timestamps, self, other)

    def __le__(self, other):
        return LesserEqualTimeIndexExpression(self.timestamps, self, other)

    def __gt__(self, other):
        return GreaterTimeIndexExpression(self.timestamps, self, other)

    def __lt__(self, other):
        return LesserTimeIndexExpression(self.timestamps, self, other)

    def __eq__(self, other):
        return EqualTimeIndexExpression(self.timestamps, self, other)

    def __neg__(self):
        return MultiplicationTimeIndexExpression(self.timestamps, self, -1)


BaseTimeIndexModel = Union[ITimeIndexBaseModel, float, int, OptimisationExpression]


class ITimeIndexExpression(ITimeIndexBaseModel):
    def __init__(self, timestamps: Timestamps, variable_1: BaseTimeIndexModel,
                 variable_2: BaseTimeIndexModel):
        self._variable_1 = variable_1
        self._variable_2 = variable_2
        self._timestamps = timestamps

    @property
    def timestamps(self) -> Timestamps:
        return self._timestamps

    @property
    def name(self):
        return 'TimeIndexExpression'

    def _get_value(self, variable):
        while isinstance(variable, ITimeIndexBaseModel) or \
                isinstance(variable, OptimisationExpression):
            variable = variable.value

        try:
            if len(variable) == len(self.timestamps):
                # print([v.value for v in variable])
                v_ = []
                for v in variable:
                    if isinstance(v, IBaseVariable):
                        v_.append(v.value.value)
                    elif isinstance(v, OptimisationExpression):
                        v_.append(v.value)
                    else:
                        v_.append(v)

                """
                [v.value
                        if isinstance(v, IBaseVariable) or isinstance(v, OptimisationExpression)
                        else v for v in variable
                        ]
                """

                return v_
        except TypeError:
            return [variable] * len(self.timestamps)
        except AssertionError as e:
            raise UnequalTimeIndexExpression(
                f'Variable {variable.name} timestamps is unequal to '
                f'expression timestamps : {e}')

    def get_value_timestamp(self, timestamp: Timestamp):
        return self._get_value_timestamp(timestamp)

    def _get_index_variable(self, variable):
        if isinstance(variable, int) or isinstance(variable, float):
            return [variable for _ in self.timestamps]
        else:
            return variable

    def _get_indexed_variables(self):
        var_1 = self._get_index_variable(self._variable_1)
        var_2 = self._get_index_variable(self._variable_2)

        return var_1, var_2

    @property
    def value(self) -> OptimisationExpression:
        raise NotImplementedError

    def evaluate(self):
        return self.value.value


class SumTimeIndexExpression(ITimeIndexExpression):
    @property
    def value(self) -> OptimisationExpression:
        value_1 = self._get_value(self._variable_1)
        value_2 = self._get_value(self._variable_2)
        return OptimisationExpression([v_1 + v_2 for v_1, v_2 in zip(value_1, value_2)])

    def get_expression(self):
        var_1, var_2 = self._get_indexed_variables()

        return [SumExpression(v_1, v_2) for v_1, v_2 in zip(var_1, var_2)]

    def __repr__(self):
        return f'{self._variable_1} + {self._variable_2}'


class SubtractTimeIndexExpression(ITimeIndexExpression):
    @property
    def value(self) -> OptimisationExpression:
        value_1 = self._get_value(self._variable_1)
        value_2 = self._get_value(self._variable_2)

        return OptimisationExpression([v_1 - v_2 for v_1, v_2 in zip(value_1, value_2)])

    def get_expression(self):

        var_1, var_2 = self._get_indexed_variables()
        return [SubtractExpression(v_1, v_2) for v_1, v_2 in zip(var_1, var_2)]

    def __repr__(self):
        return f'{self._variable_1.name} - {self._variable_1.name}'


class MultiplicationTimeIndexExpression(ITimeIndexExpression):
    @property
    def value(self) -> OptimisationExpression:
        value_1 = self._get_value(self._variable_1)
        value_2 = self._get_value(self._variable_2)

        return OptimisationExpression([v_1 * v_2 for v_1, v_2 in zip(value_1, value_2)])

    def get_expression(self):
        var_1, var_2 = self._get_indexed_variables()
        return [MultiplicationExpression(v_1, v_2) for v_1, v_2 in zip(var_1, var_2)]

    def __repr__(self):
        return f'{self._variable_1.name} * {self._variable_1.name}'


class DivisionTimeIndexExpression(ITimeIndexExpression):
    @property
    def value(self) -> OptimisationExpression:
        value_1 = self._get_value(self._variable_1)
        value_2 = self._get_value(self._variable_2)

        return OptimisationExpression([v_1/v_2 for v_1, v_2 in zip(value_1, value_2)])

    def get_expression(self):
        var_1, var_2 = self._get_indexed_variables()
        return [DivisionExpression(v_1, v_2) for v_1, v_2 in zip(var_1, var_2)]

    def __repr__(self):
        return f'{self._variable_1.name} / {self._variable_1.name}'


class EqualTimeIndexExpression(ITimeIndexExpression):
    @property
    def value(self) -> OptimisationExpression:
        value_1 = self._get_value(self._variable_1)
        value_2 = self._get_value(self._variable_2)

        return OptimisationExpression([v_1 == v_2 for v_1, v_2 in zip(value_1, value_2)])

    def get_expression(self):
        var_1, var_2 = self._get_indexed_variables()
        return [EqualExpression(v_1, v_2) for v_1, v_2 in zip(var_1, var_2)]

    def __repr__(self):
        return f'{self._variable_1.name} == {self._variable_1.name}'


class GreaterTimeIndexExpression(ITimeIndexExpression):
    @property
    def value(self) -> OptimisationExpression:
        value_1 = self._get_value(self._variable_1)
        value_2 = self._get_value(self._variable_2)

        return OptimisationExpression([v_1 > v_2 for v_1, v_2 in zip(value_1, value_2)])

    def get_expression(self):
        var_1, var_2 = self._get_indexed_variables()
        return [GreaterExpression(v_1, v_2) for v_1, v_2 in zip(var_1, var_2)]

    def __repr__(self):
        return f'{self._variable_1.name} > {self._variable_1.name}'


class LesserTimeIndexExpression(ITimeIndexExpression):
    @property
    def value(self) -> OptimisationExpression:
        value_1 = self._get_value(self._variable_1)
        value_2 = self._get_value(self._variable_2)
        return OptimisationExpression([v_1 < v_2 for v_1, v_2 in zip(value_1, value_2)])

    def get_expression(self):
        var_1, var_2 = self._get_indexed_variables()
        return [LesserExpression(v_1, v_2) for v_1, v_2 in zip(var_1, var_2)]

    def __repr__(self):
        return f'{self._variable_1.name} < {self._variable_1.name}'


class GreaterEqualTimeIndexExpression(ITimeIndexExpression):
    @property
    def value(self) -> OptimisationExpression:
        value_1 = self._get_value(self._variable_1)
        value_2 = self._get_value(self._variable_2)

        return OptimisationExpression([v_1 >= v_2 for v_1, v_2 in zip(value_1, value_2)])

    def get_expression(self):
        var_1, var_2 = self._get_indexed_variables()
        return [GreaterEqualExpression(v_1, v_2) for v_1, v_2 in zip(var_1, var_2)]

    def __repr__(self):
        return f'{self._variable_1.name} >= {self._variable_1.name}'


class LesserEqualTimeIndexExpression(ITimeIndexExpression):
    @property
    def value(self) -> OptimisationExpression:
        value_1 = self._get_value(self._variable_1)
        value_2 = self._get_value(self._variable_2)

        return OptimisationExpression([v_1 <= v_2 for v_1, v_2 in zip(value_1, value_2)])

    def _get_index_variable(self, variable):
        if isinstance(variable, int) or isinstance(variable, float):
            return [variable for _ in self.timestamps]
        else:
            return variable

    def get_expression(self):
        var_1, var_2 = self._get_indexed_variables()
        return [LesserEqualExpression(v_1, v_2) for v_1, v_2 in zip(var_1, var_2)]

    def __repr__(self):
        return f'{self._variable_1.name} <= {self._variable_1.name}'


TimeIndexConstraintType = Union[EqualTimeIndexExpression, GreaterTimeIndexExpression,
                                GreaterEqualTimeIndexExpression, LesserEqualTimeIndexExpression,
                                LesserTimeIndexExpression]
TimeIndexObjectiveType = Union[SumTimeIndexExpression, SubtractTimeIndexExpression,
                               MultiplicationTimeIndexExpression, DivisionTimeIndexExpression]


class UnknownTimestampError(Exception):
    pass


class UndefinedValueError(Exception):
    pass


class UnequalTimeIndexExpression(Exception):
    pass
