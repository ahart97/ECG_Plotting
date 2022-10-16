import os
import numpy as np
import pandas as pd
import os
import numpy as np
import pandas as pd
import nwdata.NWData
import random
from ecg_report import create_chart_plots
import pickle


def validate_our_Data(annotate_path: str, output_path: str):

    os.makedirs(output_path, exist_ok=True)

    manual_data = pd.read_csv(annotate_path)
    manual_data_array = manual_data.to_numpy()
    columns = list(manual_data.columns)

    #Get data for each catagory that is longer than 15 seconds
    Q3_data = []
    Q2_data = []
    Q1_data = []

    for annotation in manual_data_array:
        if annotation[-1] < 15:
            continue

        category = annotation[5]
        #Q1
        if 'Super' in category:
            annotation[5] = 'Q1'
            Q1_data.append(annotation)
        #Q2
        elif 'Somewhat' in category or 'Quite' in category:
            annotation[5] = 'Q2'
            Q2_data.append(annotation)
        #Q3
        elif 'Crap' in category:
            annotation[5] = 'Q3'
            Q3_data.append(annotation)

    #Format the data into 15 seconds
    Q1_data_fromatted = FormatAnnotations(Q1_data, bout_size=15, fs=250)
    Q2_data_fromatted = FormatAnnotations(Q2_data, bout_size=15, fs=250)
    Q3_data_fromatted = FormatAnnotations(Q3_data, bout_size=15, fs=250)

    #Select some random trials
    Q1_random = pd.DataFrame(random.choices(Q1_data_fromatted,k=2), columns=['Path', 'start_idx', 'end_idx', 'quality'])
    Q2_random = pd.DataFrame(random.choices(Q2_data_fromatted,k=2), columns=['Path', 'start_idx', 'end_idx', 'quality'])
    Q3_random = pd.DataFrame(random.choices(Q3_data_fromatted,k=2), columns=['Path', 'start_idx', 'end_idx', 'quality'])

    #Would pass the signals like this, would also export the quality, indecies and file path in a csv for each random choice
    PlotRandom(Q1_random, Q2_random, Q3_random, output_path, 'v1')

#Have hear just for debugging

def PickleDump(obj, filepath):
    """
    Pickles and object at a given filepath
    """
    with open(filepath, 'wb') as f:
        pickle.dump(obj, f)

def FormatAnnotations(data: np.array, bout_size: float, fs:float):
    """
    Formats the annotations into specified second bouts

    Will cut off the remaining bit of each signal section if it will not go into the time specified seconds
    """

    data_format = []

    for annotation in data:
        num_bouts = int(annotation[-1]/bout_size)

        for ii in range(num_bouts):
            new_annotation = np.array([annotation[0], int(annotation[2]+fs*ii*bout_size), int(annotation[2]+fs*(ii+1)*bout_size), annotation[5]], dtype='O')
            data_format.append(new_annotation)

    return data_format


def PlotRandom(Q1: pd.DataFrame, Q2: pd.DataFrame, Q3: pd.DataFrame, save_dir:str, random_split_name: str='no_label'):
    '''
    if len(data.shape) > 1:
        for annotation in data:
            signal, fs = Load_Raw_ECG(annotation[0], (annotation[1], annotation[2]))
            title = annotation[0].split('cropped/')[-1]
            title = title.split('.EDF')[0]
            t = np.linspace(annotation[1]/fs, annotation[2]/fs, 15, dtype=int)

            create_chart_plots(ecg=signal, fs=fs, save_path=save_dir, title=title, chart_width=375)'''

    #Append all the data togther
    data = pd.concat([Q1, Q2, Q3], ignore_index=True)

    #Shuffle the dataframe
    data = data.sample(frac=1).reset_index(drop=True)

    #Save the details for the shuffled dataframe
    data.to_csv(os.path.join(save_dir, random_split_name + '_data_details.csv'))
    
    #Combine the signals into one
    signal = np.array([])
    start_idxs = data['start_idx'].values
    end_idxs = data['end_idx'].values
    for ii, path in enumerate(data['Path'].values):
        signal_ii, fs = Load_Raw_ECG(path, (start_idxs[ii], end_idxs[ii]))
        signal = np.append(signal, signal_ii)
    PickleDump(np.array(signal), os.path.join(save_dir, 'test_signal.pickle'))
    PickleDump(fs, os.path.join(save_dir, 'test_fs.pickle'))
    title = random_split_name + '_random_ECG'

    #create_chart_plots(ecg=signal, fs=fs, save_path=save_dir, title=title, chart_width=375)


def Load_Raw_ECG(source: str, index: tuple):
    '''
    Load in the raw data associated with the manually annotated HANDDS dataset
    
    source = path to edf file
    index = tuple of start and stop index
    '''

    raw_HANDDS_location = "Y://NiMBaLWEAR"
    source = os.path.join(raw_HANDDS_location, source.split('/NiMBaLWEAR/')[-1])

    data = nwdata.NWData()
    data.import_edf(file_path=source)

    #Read the ECG
    ecg_signal = np.array(data.signals[0])
    ecg_details = data.signal_headers[0]
    ecg_sample_rate = ecg_details['sample_rate']

    return ecg_signal[index[0]:index[1]], ecg_sample_rate


if __name__ == '__main__':
    HANDDS_annots = os.path.dirname(os.path.realpath(__file__))
    HANDDS_annots = os.path.join(HANDDS_annots, 'SignalQualityAnnotation_Reference.csv')
    HANDDS_output = os.path.dirname(os.path.realpath(__file__))

    validate_our_Data(HANDDS_annots, HANDDS_output)