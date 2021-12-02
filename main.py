from dataclasses import dataclass

from oct2py import octave
import os
import numpy as np
from scipy.io import loadmat
import pandas as pd
import matplotlib.pyplot as plt

from microgrid.model.grid_model import GridModelData, GridLine
from simulation.data.convert_mat_data_csv import convert_microgrid_mat_csv


def octave_try():
    path_name = '/home/control/Documents/work/project/distributed-EMS-interconnected-mg/simulator'
    octave.addpath(path_name)
    octave.eval('sample_py')


@dataclass
class TempClass:
    var_1: int
    var_2: int

    def validate_date(self):
        try:
            assert type(self.var_2) == int
            return True
        except:
            return False

if __name__ == '__main__':

    t_1 = TempClass(1, 2)
    print(t_1)
    print(t_1.validate_date())

    """
    l = GridLine('1', '2')
    t = np.array([[0, 5, 6],
                  [7, 0, 8],
                  [9, 10, 0]])
    for i in range(0, 3):
        t[i, i] = t[i, :].sum()

    print(t)
    """

    """
    a = [1, 2, 3, 4, 5, 6]
    x = np.array([-9, 8, -9, 10]).T
    num_bus = 4
    mat_a = np.zeros((num_bus, num_bus))
    # mat_a[0][1:3] = np.array([1, 2]

    j = 0
    for i in range(num_bus-1, 0, -1):
        mat_a[num_bus-i-1][num_bus - i:] = a[j:j+i]
        j = j + i

    mat_a_sys = mat_a + mat_a.T
    for i in range(0, num_bus):
        mat_a_sys[i][i] = -mat_a_sys[i].sum()

    print(mat_a_sys)
    # print(mat_a_sys[1:, 1:])
    # print(np.linalg.inv(mat_a_sys[1:, 1:])@x[1:])
    x_dash = np.zeros(4)
    x_dash[1:] = np.linalg.inv(mat_a_sys[1:, 1:])@x[1:]
    print(x_dash)
    # print(x)
    print(mat_a_sys@x_dash)
    """
    cwd = os.getcwd()

    convert_microgrid_mat_csv(mat_data_relate_path='simulation/data', csv_relative_path='simulation/data')

    print('completed')

