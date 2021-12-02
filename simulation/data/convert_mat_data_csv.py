from scipy.io import loadmat
import pandas as pd
import os
import matplotlib.pyplot as plt

def convert_microgrid_mat_csv(mat_data_relate_path: str, csv_relative_path:str):
    try:
        matlab_mg_model_data_path = os.path.join(mat_data_relate_path, 'jupiterModelTimeseries.mat')
        jupiter_csv_data_path = os.path.join(mat_data_relate_path, 'jupiter_model.csv')


        jupiter_data = loadmat(matlab_mg_model_data_path)
        num_data_point = len(jupiter_data['jupiterModelTs'][0][0][0][0][0])

        jupiter_pd_data = pd.DataFrame(
            index=jupiter_data['jupiterModelTs'][0][0][2][0][0].reshape((num_data_point,))
        )
        jupiter_pd_data['timestamp'] = jupiter_data['jupiterModelTs'][0][0][0][0][0].reshape(
            (num_data_point,))
        for i in range(0, 4):
            jupiter_pd_data[f'mg_{i}_renewable'] = jupiter_data['jupiterModelTs'][0][0][0][0][i].reshape(
                (num_data_point,))
            jupiter_pd_data[f'mg_{i}_load'] = jupiter_data['jupiterModelTs'][0][0][1][0][i].reshape(
                (num_data_point,))

        jupiter_pd_data.to_csv(jupiter_csv_data_path)
    except (FileNotFoundError, ValueError):
        raise ValueError("conversion of microgrid data  is not possible")

"""
    fig, ax = plt.subplots(4, 1)
    ax[0].plot(jupiter_data['jupiterModelTs'][0][0][1][0][0])
    ax[1].plot(jupiter_data['jupiterModelTs'][0][0][1][0][1])
    ax[2].plot(jupiter_data['jupiterModelTs'][0][0][1][0][2])
    ax[3].plot(jupiter_data['jupiterModelTs'][0][0][1][0][3])
    plt.show()
"""