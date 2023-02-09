import matplotlib.pyplot as plt
import pandas as pd
import os
import numpy as np

def PlotSNRDist(SNR_vals):
    bins = np.linspace(1,24,21)
    plt.hist(SNR_vals, bins=bins, edgecolor='black', linewidth=1.2)
    plt.xlabel('SNR')
    plt.ylabel('Number of Signals Sampled')
    plt.xticks(bins)

    plt.show()

if __name__ == '__main__':

    random_state = 1
    test_code = chr(random_state+96)

    current_dir = os.getcwd().split('\\ECG_Plotting')[0]
    signal_details = pd.read_csv(os.path.join(current_dir, 'Signal Details', 'ecg_sampled_' + test_code + '.csv')).to_dict()

    PlotSNRDist(np.array(list(signal_details['SNR_avg'].values())))


