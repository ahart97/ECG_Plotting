import nimbalwear
import random
import numpy as np
import pickle

def LoadSignal(ecg_signal_dir: str, start_idx = 0, stop_idx = -1):
    data = nimbalwear.Device()
    data.import_edf(file_path=ecg_signal_dir)

    #Load ECG
    ecg_details = data.signal_headers[0]
    ecg_signal = np.array(data.signals[0])[int(start_idx):int(stop_idx)]
    ecg_fs = ecg_details['sample_rate']

    return (ecg_signal, ecg_fs)

def _FindSNREligible(SNR_avg: list, SNR_min: list, SNR_max: list, amp_max: list, SNR_range: tuple):
    avg_check = np.logical_and(SNR_avg > SNR_range[0], SNR_avg < SNR_range[1])
    min_check = np.logical_and(SNR_min >= SNR_range[0], SNR_min < SNR_range[1])
    max_check = np.logical_and(SNR_max > SNR_range[0], SNR_max <= SNR_range[1])

    amp_check = True#amp_max < 1850 #Found from probing one of the signals

    eligible = np.logical_and(np.logical_and(np.logical_and(avg_check, min_check), max_check), amp_check)
    return eligible

def PickleDump(obj, filepath):
    """
    Pickles and object at a given filepath
    """
    with open(filepath, 'wb') as f:
        pickle.dump(obj, f)

def PickleLoad(filepath):
    """
    Loads an object from a pickle filepath 
    """
    with open(filepath, 'rb') as f:
        obj = pickle.load(f)
    return obj
