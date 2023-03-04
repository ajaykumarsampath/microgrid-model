import numpy as np

from control.optimisation_engine.operation import VariableArray, VariableMatrix, matmul


class TestOperationVariable:
    def test_variable_array(self):
        arr_value = [1, 2]
        mat_value = list(range(0, 6))
        arr_var = VariableArray([1, 2])
        mat_var = VariableMatrix(list(range(6)), 3, 2)

        assert [arr_var[i] for i in range(0, arr_var.shape[0])] == arr_value
        assert [mat_var[i, j] for j in range(0, mat_var.shape[1])
                for i in range(0, mat_var.shape[0])] == mat_value

    def test_matmul(self):
        arr_value = np.array([1, 2])
        mat_value = np.array([
            [0, 3],
            [1, 4],
            [2, 5]
        ])

        arr_var = VariableArray(arr_value)
        mat_var = VariableMatrix([j for i in mat_value.T.tolist() for j in i], 3, 2)

        result = matmul(mat_var, arr_var)
        assert all((result.value == mat_value @ arr_value).flatten())
