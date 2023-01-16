import pandas as pd
import numpy as np
import os
from nwecg.ecg_quality import annotate_ecg_quality
import nimbalwear
import random
from ecg_strip_charts import create_chart_plots

class ECGDictionary():
    def __init__(self, random_state):

        #Dictionary for all of the data
        self.ECG_dictionary = {'bout_code': [], 'signal_dirs': [], 'fs': [], 'start_idx': [], 'end_idx': [], 'SNR_avg': [], 'SNR_min': [], 'SNR_max': []}
        self.plot_dictionary = {'plot_dirs': [], 'S1_code': [], 'S2_code': [], 'S3_code': [], 'S4_code': [], 'S5_code': [], 'S6_code': []}

        #Sets the random state
        self.random_state = random_state

    def LoadSignal(ecg_signal_dir: str):
        data = nimbalwear.Device()
        data.import_edf(file_path=ecg_signal_dir)

        #Load ECG
        ecg_details = data.signal_headers[0]
        ecg_signal = np.array(data.signals[0])
        ecg_fs = ecg_details['sample_rate']

        return ecg_signal, ecg_fs


    def SampleSignal(self, participant_num: int, ecg_signal_dir: str):
        """
        Takes the raw signal and the SNR to record the potential 10 second bouts
        """

        ecg, fs = self.LoadSignal(ecg_signal_dir)

        _, _, SNR, _, _ = annotate_ecg_quality(ecg_signal=ecg, ecg_sample_rate=fs)

        start_idx = 0
        #Loop through 10 second bouts of the signal
        for ii in range(int(fs*10), len(SNR), int(fs*10)):
            stop_idx = ii
            bout_code = chr(participant_num) + str(ii)

            #Find the data based on the start and stop indices
            SNR_avg = np.nanmean(SNR[start_idx:stop_idx])
            SNR_min = np.nanmin(SNR[start_idx:stop_idx])
            SNR_max = np.nanmax(SNR[start_idx:stop_idx])

            #Append everthing to the main dictionary
            self.ECG_dictionary['bout_code'].append(bout_code)
            self.ECG_dictionary['signal_dirs'].append(ecg_signal_dir)
            self.ECG_dictionary['fs'].append(fs)
            self.ECG_dictionary['start_idx'].append(start_idx)
            self.ECG_dictionary['end_idx'].append(stop_idx)
            self.ECG_dictionary['SNR_avg'].append(SNR_avg)
            self.ECG_dictionary['SNR_min'].append(SNR_min)
            self.ECG_dictionary['SNR_max'].append(SNR_max)

            start_idx = stop_idx+1

        #TODO: Do we want pre-processed or raw ECG

    def SampleDistribution(self):
        """
        Pulls a subset from the ECG dictionary based on the distribution specified (this should be random so can just run multiple times for new surveys)

        Shuffles the signals at the end 
        """

        def FindSNREligible(SNR_avg: list, SNR_min: list, SNR_max: list, SNR_range: tuple):
            avg_check = SNR_avg > SNR_range[0] and SNR_avg < SNR_range[1]
            min_check = SNR_min >= SNR_range[0] and SNR_min < SNR_range[1]
            max_check = SNR_max > SNR_range[0] and SNR_max <= SNR_range[1]

            eligible = avg_check and min_check and max_check

        self.ECG_sample_dictionary = {'bout_code': [], 'signal_dirs': [], 'fs': [], 'start_idx': [], 'end_idx': [], 'SNR_avg': [], 'SNR_min': [], 'SNR_max': []}

        #Define number of slides - number of plots will be that times 6
        num_slides = 50
        num_plots = num_slides*6

        SNR_ranges = [(-5,10), (10,15), (15,20), (20,30), (30,100)]

        for ii in range(num_plots):
            #Find the SNR range for this iteration
            #TODO: Define the p for the distribution
            SNR_range = np.random.choice(SNR_ranges, p =[1,1,1,1,1])

            #Find the indicies that are good based on the SNR range
            SNR_eligibility = FindSNREligible(self.ECG_dictionary['SNR_avg'], self.ECG_dictionary['SNR_min'], self.ECG_dictionary['SNR_max'], SNR_range)

            eligible_values = np.array(list(self.ECG_dictionary.values()))[SNR_eligibility]

            #Randomly sample the good indices
            selected_bout = pd.DataFrame(eligible_values, columns=list(self.ECG_dictionary.keys())).sample(random_state=self.random_state)

            #Add the selected bout to the sample_dictionary
            self.mergeDictionary(selected_bout.to_dict())


    def mergeDictionary(self, dict_2):
        """
        Merge two dictionaries based on their keys
        """
        dict_3 = {**dict_2}
        for key, value in dict_3.items():
            if key in self.ECG_sample_dictionary and key in dict_2:
                combined_value = np.array([self.ECG_sample_dictionary[key], value])
                dict_3[key] = np.hstack(combined_value)
        
        self.ECG_sample_dictionary = dict_3


    def ProcessSignalPlotting(self, signal_idx, signal_row):

        #Load the proper signal
        signal, fs = self.LoadSignal(self.ECG_sample_random['signal_dirs'][signal_idx])

        #Record what signal was picked
        self.plot_dictionary['S'+str(signal_row+1)+'_code'].append(self.ECG_sample_random['bout_code'][signal_idx])

        return signal[self.ECG_sample_random['start_idx'][ii]:self.ECG_sample_random['stop_idx'][ii]]


    def GroupDistribution(self, test_code):
        """
        Groups the signals in the sample distribution for plotting

        Each group will have an identifier which will be the name of the plot
        """

        #Randomize the order of the sampled dictionary (need to convert to df to do this and then back)
        self.ECG_sample_random = pd.DataFrame(self.ECG_sample_dictionary).sample(frac=1, random_state=self.random_state).to_dict()

        plot_count = 1

        for ii in range(0, len(self.ECG_sample_random['bout_code']), 6):
            #Loop through the signals 6 at a time

            plotting_signal = np.array([])

            #Populate the plotting signal with the next 6 signals
            for jj in range(6):
                plotting_signal = np.append(plotting_signal, self.ProcessSignalPlotting(ii+jj, jj))

            #Reshape the plotting signal
            plotting_signal = np.reshape(plotting_signal, (int(self.ECG_sample_random['fs'][ii]*10),6))

            create_chart_plots(plotting_signal, self.ECG_sample_random['fs'][ii], 'Plots', test_code + str(plot_count))

            #Save plot details
            self.plot_dictionary['plot_dirs'].append(os.path.join('Plots', test_code + str(plot_count) + '.png'))

            plot_count+=1


if __name__ == '__main__':

    #TODO: Run through everything

    #Set the random seed (can have multiple variations)
    random_state = 1
    test_code = chr(random_state)
    random.seed(random_state)

    ECGFinder = ECGDictionary(random_state=random_state)

    signals_dir = r'Y:\NiMBaLWEAR\OND09\wearables\device_edf_cropped'

    ecg_signal_paths = []
    for file in os.listdir(signals_dir):
        if 'Chest.edf' in file:
            ecg_signal_paths.append(os.path.join(signals_dir, file))

    for ii, signal in enumerate(ecg_signal_paths):
        ECGFinder.SampleSignal(ii, signal)

    ECGFinder.SampleDistribution()
    ECGFinder.GroupDistribution(test_code)

    #save both of the dictionarys
    pd.DataFrame(ECGFinder.ECG_dictionary).to_csv(os.path.join('ECG_Plotting', 'Signal Details', 'ecg_details.csv'), index=False)
    pd.DataFrame(ECGFinder.plot_dictionary).to_csv(os.path.join('ECG_Plotting', 'Signal Details', 'plot_details.csv'), index=False)