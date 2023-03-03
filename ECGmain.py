import pandas as pd
import numpy as np
import os
from nwecg.ecg_quality import annotate_ecg_quality, preprocess
import nimbalwear
import random
from ecg_strip_charts import create_chart_plots

class ECGDictionary():
    def __init__(self, random_state):

        #Dictionary for all of the data
        self.ECG_dictionary = {'bout_code': [], 'signal_dirs': [], 'fs': [], 'start_idx': [], 'end_idx': [], 'SNR_avg': [], 'SNR_min': [], 'SNR_max': [], 'Amp_max': []}
        self.plot_dictionary = {'plot_dirs': [], 'S1_code': [], 'S2_code': [], 'S3_code': [], 'S4_code': [], 'S5_code': [], 'S6_code': []}

        #Sets the random state
        self.random_state = random_state

        #Define number of slides - number of plots will be that times 6
        self.bout_time = 10 #seconds
        self.num_slides = 50
        self.plots_per_slide = 6
        self.num_plots = self.num_slides*self.plots_per_slide

        #Smital cutoffs are 5 and 18 dB
        #15 to 18 is really that interesting range
        #1 to 22 ish, unifrom bins and the uniform distribution 
        self.SNR_ranges = []
        for ii in range(22):
            self.SNR_ranges.append((ii+1,ii+3))

        self.evenBinCounts = 8
        self.numBins = len(self.SNR_ranges)
        self.overlapPlots = int(self.evenBinCounts*self.numBins)
        self.nonOverlapPlots = self.num_plots-self.overlapPlots

    def LoadSignal(self, ecg_signal_dir: str):
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

        x, _, SNR, _, _ = annotate_ecg_quality(ecg_signal=ecg, ecg_sample_rate=fs)


        start_idx = int(fs*self.bout_time)
        bout_count = 0

        #Loop through 10 second bouts of the signal - skip the first and last 10 seconds
        for ii in range(int(fs*self.bout_time)*2, len(SNR), int(fs*self.bout_time)):

            stop_idx = ii
            bout_code = 'P' + str(participant_num) + '_B' + str(bout_count)

            #Find the data based on the start and stop indices
            SNR_avg = np.nanmean(SNR[start_idx:stop_idx])
            SNR_min = np.nanmin(SNR[start_idx:stop_idx])
            SNR_max = np.nanmax(SNR[start_idx:stop_idx])
            amp_max = np.nanmax(np.abs(x[start_idx:stop_idx]))

            #Append everthing to the main dictionary
            self.ECG_dictionary['bout_code'].append(bout_code)
            self.ECG_dictionary['signal_dirs'].append(ecg_signal_dir)
            self.ECG_dictionary['fs'].append(fs)
            self.ECG_dictionary['start_idx'].append(start_idx)
            self.ECG_dictionary['end_idx'].append(stop_idx)
            self.ECG_dictionary['SNR_avg'].append(SNR_avg)
            self.ECG_dictionary['SNR_min'].append(SNR_min)
            self.ECG_dictionary['SNR_max'].append(SNR_max)
            self.ECG_dictionary['Amp_max'].append(amp_max)

            start_idx = stop_idx+1
            bout_count+=1

        #Going with preprocessed signals

    def SampleDistribution(self):
        """
        Pulls a subset from the ECG dictionary based on the distribution specified (this should be random so can just run multiple times for new surveys)

        Shuffles the signals at the end 
        """

        self.ECG_sample_dictionary = {'bout_code': [], 'signal_dirs': [], 'fs': [], 'start_idx': [], 'end_idx': [], 'SNR_avg': [], 'SNR_min': [], 'SNR_max': []}

        for ii in range(self.nonOverlapPlots):
            #Find the SNR range for this iteration
            #Weighting everything evenly
            SNR_index = np.random.choice(len(self.SNR_ranges),1)[0]
            SNR_range = self.SNR_ranges[SNR_index]

            #Find the indicies that are good based on the SNR range
            SNR_eligibility = self._FindSNREligible(np.array(list(self.ECG_dictionary['SNR_avg'].values())), np.array(list(self.ECG_dictionary['SNR_min'].values())), np.array(list(self.ECG_dictionary['SNR_max'].values())), np.array(list(self.ECG_dictionary['Amp_max'].values())), SNR_range)

            eligible_idxs = np.where(SNR_eligibility)[0]

            #Sample from the bouts within the bin
            selected_bout = self._RandomSelect(eligible_idxs)

            #Keep sampling until a bout is found that is not in the ECG_sample_directory already
            while selected_bout['bout_code'] in self.ECG_sample_dictionary['bout_code'] or selected_bout['bout_code'] in self.ECG_core_dictionary['bout_code']:
                selected_bout = self._RandomSelect(eligible_idxs)

            #Add the selected bout to the sample_dictionary
            self.ECG_sample_dictionary = self.mergeDictionary(self.ECG_sample_dictionary, selected_bout)


    def _FindSNREligible(self, SNR_avg: list, SNR_min: list, SNR_max: list, amp_max: list, SNR_range: tuple):
        avg_check = np.logical_and(SNR_avg > SNR_range[0], SNR_avg < SNR_range[1])
        min_check = np.logical_and(SNR_min >= SNR_range[0], SNR_min < SNR_range[1])
        max_check = np.logical_and(SNR_max > SNR_range[0], SNR_max <= SNR_range[1])

        amp_check = amp_max < 1850 #Found from probing one of the signals

        eligible = np.logical_and(np.logical_and(np.logical_and(avg_check, min_check), max_check), amp_check)
        return eligible


    def _RandomSelect(self, eligible_idxs):
        #Randomly sample the good indices
        idx = np.random.choice(eligible_idxs)

        selected_bout = {}
        for key in self.ECG_dictionary.keys():
            selected_bout[key] = self.ECG_dictionary[key][idx]
        return selected_bout


    def PullSiganl(self, signal_code):

        index = np.where(np.array(list(self.ECG_dictionary['bout_code'].values())) == signal_code)[0][0]

        signal, _ = self.LoadSignal(self.ECG_dictionary['signal_dirs'][index])

        print(np.max(np.abs(signal[self.ECG_dictionary['start_idx'][index]:self.ECG_dictionary['end_idx'][index]])))

        a= 1


    def SampleCoreSignals(self):
        """
        Pulls 84 signals, 4 from each bin, that will be used as an overlap between all raters

        This set is appended on the other sampled set
        """

        self.ECG_core_dictionary = {'bout_code': [], 'signal_dirs': [], 'fs': [], 'start_idx': [], 'end_idx': [], 'SNR_avg': [], 'SNR_min': [], 'SNR_max': []}

        for ii in range(self.overlapPlots):
            #Need to find four signals for each bin
            SNR_index = int(ii/(self.overlapPlots/len(self.SNR_ranges)))
            SNR_range = self.SNR_ranges[SNR_index]

            #Find the indicies that are good based on the SNR range
            SNR_eligibility = self._FindSNREligible(np.array(list(self.ECG_dictionary['SNR_avg'].values())), np.array(list(self.ECG_dictionary['SNR_min'].values())), np.array(list(self.ECG_dictionary['SNR_max'].values())), np.array(list(self.ECG_dictionary['Amp_max'].values())), SNR_range)

            eligible_idxs = np.where(SNR_eligibility)[0]

            if len(eligible_idxs) < self.evenBinCounts:
                print('Not enough eligible bouts')
                exit()

            #Sample from the bouts within the bin
            selected_bout = self._RandomSelect(eligible_idxs)

            #Keep sampling until a bout is found that is not in the ECG_sample_directory already
            while selected_bout['bout_code'] in self.ECG_core_dictionary['bout_code']:
                selected_bout = self._RandomSelect(eligible_idxs)

            #Add the selected bout to the sample_dictionary
            self.ECG_core_dictionary = self.mergeDictionary(self.ECG_core_dictionary, selected_bout)


    def mergeDictionary(self, dict_1, dict_2):
        """
        Merge two dictionaries based on their keys
        """
        dict_3 = {**dict_2}
        for key, value in dict_3.items():
            if key in dict_1 and key in dict_2:
                try:
                    a_list = list(dict_1[key].values())
                    b_list = list(value.values())
                    combined_value = np.array([a_list, b_list], dtype=object)
                except:
                    combined_value = np.array([dict_1[key], value], dtype=object)
                dict_3[key] = np.hstack(combined_value)
        
        return dict_3


    def ProcessSignalPlotting(self, signal_idx, signal_row):

        #Load the proper signal
        signal, fs = self.LoadSignal(self.ECG_sample_random['signal_dirs'][signal_idx])

        #Preprocess the signal - like in the Smital
        x = preprocess(signal, fs)

        #Record what signal was picked
        self.plot_dictionary['S'+str(signal_row+1)+'_code'].append(self.ECG_sample_random['bout_code'][signal_idx])

        trimmed_x = x[int(self.ECG_sample_random['start_idx'][signal_idx]):int(self.ECG_sample_random['end_idx'][signal_idx]+1)]

        return trimmed_x


    def GroupDistribution(self, save_dir, test_code):
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
            for jj in range(self.plots_per_slide):
                plotting_signal = np.append(plotting_signal, self.ProcessSignalPlotting(ii+jj, jj))

            #Reshape the plotting signal
            plotting_signal = np.reshape(plotting_signal, (int(self.ECG_sample_random['fs'][ii]*self.bout_time),self.plots_per_slide))

            create_chart_plots(plotting_signal, self.ECG_sample_random['fs'][ii], os.path.join(save_dir, 'Plots'), test_code + str(plot_count))

            #Save plot details
            self.plot_dictionary['plot_dirs'].append(os.path.join('Plots', test_code + str(plot_count) + '.png'))

            plot_count+=1


if __name__ == '__main__':

    #Set the random seed (can have multiple variations)
    random_state = 1
    test_code = chr(random_state+96)
    random.seed(random_state)

    ECGFinder = ECGDictionary(random_state=random_state)

    signals_dir = r'Y:\NiMBaLWEAR\OND09\wearables\device_edf_cropped'
    current_dir = os.getcwd().split('\\ECG_Plotting')[0]

    #Not sure what SBH and TWH are???
    try:
        ECGFinder.ECG_dictionary = pd.read_csv(os.path.join(current_dir, 'Signal Details', 'ecg_details.csv')).to_dict()
    except:
        ecg_signal_paths = []
        for file in os.listdir(signals_dir):
            if 'Chest.edf' in file and 'SBH' not in file and 'TWH' not in file and 'OND09_0003_01' not in file:
                ecg_signal_paths.append(os.path.join(signals_dir, file))

        for ii, signal in enumerate(ecg_signal_paths):
            ECGFinder.SampleSignal(participant_num=ii, ecg_signal_dir=signal)

        #Save signal details here since that should not change
        pd.DataFrame(ECGFinder.ECG_dictionary).to_csv(os.path.join(current_dir, 'Signal Details', 'ecg_details.csv'), index=False)

    #ECGFinder.PullSiganl('P26_B34978')

    #Find the core sample
    try:
        ECGFinder.ECG_core_dictionary = pd.read_csv(os.path.join(current_dir, 'Signal Details', 'ecg_sampled_core.csv')).to_dict()
    except:
        ECGFinder.SampleCoreSignals()
        pd.DataFrame(ECGFinder.ECG_core_dictionary).to_csv(os.path.join(current_dir, 'Signal Details', 'ecg_sampled_core.csv'), index=False)

    #Sample the ecg bouts
    try:
        ECGFinder.ECG_sample_dictionary = pd.read_csv(os.path.join(current_dir, 'Signal Details', 'ecg_sampled_random.csv')).to_dict()
    except:
        ECGFinder.SampleDistribution()
        pd.DataFrame(ECGFinder.ECG_sample_dictionary).to_csv(os.path.join(current_dir, 'Signal Details', 'ecg_sampled_random.csv'), index=False)

    #Group bouts and throw them in plots
    try:
        ECGFinder.plot_dictionary = pd.read_csv(os.path.join(current_dir, 'Signal Details', 'plot_details_' + test_code + '.csv')).to_dict()
    except:
        #MODIFY THE NUMBER OF OVERLAP PLOTS TO REMOVE THIS FEATURE
        #Merge the core and sample dictionaries prior to the plotting, this means we save them seperate
        ECGFinder.ECG_sample_dictionary = ECGFinder.mergeDictionary(ECGFinder.ECG_sample_dictionary, ECGFinder.ECG_core_dictionary)

        ECGFinder.GroupDistribution(current_dir, test_code)
        pd.DataFrame(ECGFinder.plot_dictionary).to_csv(os.path.join(current_dir, 'Signal Details', 'plot_details_' + test_code + '.csv'), index=False)