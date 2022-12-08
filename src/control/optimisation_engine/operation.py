from typing import List, Union

from control.optimisation_engine.domain import IBaseVariable

from enum import Enum

class ArrayShapeType(Enum):
    row = 'row'
    colum = 'colum'


class VariableArray:
    def __init__(self, var: Union[List[IBaseVariable], List[float]],
                 shape_type: ArrayShapeType= ArrayShapeType.row):
        self._var = var
        self._shape_type = shape_type

    @property
    def value(self):
        return self._var

    @property
    def T(self):
        if self._shape_type is ArrayShapeType.row:
            return VariableArray(self._var, ArrayShapeType.colum)
        else:
            return VariableArray(self._var, ArrayShapeType.row)

    def __getitem__(self, item) -> IBaseVariable:
        return self._var[item]

    def shape(self):
        if self._shape_type is ArrayShapeType.row:
            return (len(self._var), 1)
        else:
            return (1, len(self._var))


    def __add__(self, other):
        try:
            return VariableArray([e + other[i] for i, e in enumerate(self)])
        except Exception as e:
            self._expectation(e)

    def __radd__(self, other):
        try:
            return VariableArray([other[i] + e for i, e in enumerate(self)])
        except Exception as e:
            self._expectation(e)


    def __sub__(self, other):
        try:
            return VariableArray([e - other[i] for i, e in enumerate(self)])
        except Exception as e:
            self._expectation(e)

    def __rsub__(self, other):
        try:
            return VariableArray([other[i] - e for i, e in enumerate(self)])
        except Exception as e:
            self._expectation(e)

    def __mul__(self, other):
        try:
            if isinstance(other, list):
                value = sum([other[i] * e for i, e in enumerate(self)])
                return VariableArray([value])
            elif isinstance(other, float) or isinstance(other, int):
                return VariableArray([e*other for e in self])
        except Exception as e:
            self._expectation(e)

    def __rmul__(self, other):
        try:
            if isinstance(other, list):
                value = sum([other[i] * e for i, e in enumerate(self)])
                return VariableArray([value])
            elif isinstance(other, float) or isinstance(other, int):
                return VariableArray([e*other for e in self])
        except Exception as e:
            self._expectation(e)


    def _expectation(self, exception: Exception):
        if isinstance(exception, TypeError):
            raise TypeError(exception)
        elif isinstance(exception, IndexError):
            raise IndexError(exception)
        else:
            raise Exception(exception)


class VariableMatrix:
    def __init__(self, var: Union[List[IBaseVariable], List[float]],
                 row_dim: int, col_dim: int):
        self._var = var
        self._row_dim = row_dim
        self._col_dim = col_dim
        assert len(var) == self._col_dim*self._row_dim

    def shape(self):
        return (self._row_dim, self._col_dim)

    @property
    def T(self):
        return VariableMatrix(self._var, self._col_dim, self._row_dim)

    def __getitem__(self, item):
        i = item[0]
        j = item[1]
        return self._var[j*self._row_dim + i]


def matmul(mat_var: VariableMatrix, array_var: VariableArray):
    mat_shape = mat_var.shape()
    vec_shape = array_var.shape()
    assert mat_shape[1] == vec_shape[0]

    result_var = [sum([mat_var[i, j]*array_var[j] for j in range(0, vec_shape[0])])
                  for i in range(0, mat_shape[0])]

    return VariableArray(result_var, ArrayShapeType.row)