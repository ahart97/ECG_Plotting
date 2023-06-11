import pandas as pd
import numpy as np
import os
from nwecg.ecg_quality import annotate_ecg_quality, preprocess
from Utils.ECG_utils import LoadSignal, _FindSNREligible, PickleDump, PickleLoad
from Utils.ecg_strip_charts import create_chart_plots
from alive_progress import alive_bar
from random import randint

class ECGDictionary():
    def __init__(self):

        #Dictionary for all of the data
        self.labels_df = pd.DataFrame()
        self.sample_df = pd.DataFrame({'bout_code': [], 'signal_dirs': [], 'fs': [], 'start_idx': [], 'end_idx': [], 'SNR_avg': [], 'SNR_min': [], 'SNR_max': []})
        self.sample_signals = np.array([])

        #Define number of slides - number of plots will be that times 6
        self.bout_time = 10 #seconds
        self.n_slides = 50
        self.bout_per_slide = 6
        self.n_bouts = self.n_slides*self.bout_per_slide

        #Smital cutoffs are 5 and 18 dB
        #15 to 18 is really that interesting range
        #1 to 22 ish, unifrom bins and the uniform distribution 
        for ii in range(22):
            if ii == 0:
                self.SNR_ranges = np.array([ii+1,ii+3])  
            else:
                self.SNR_ranges = np.vstack((self.SNR_ranges,
                                             [ii+1,ii+3]))  

        self.n_bins = self.SNR_ranges.shape[0]
        self.binCounts = np.floor(self.n_bouts/self.n_bins)

    def LabelSignals(self, participant_num: int, ecg_signal_dir: str):
        """
        Takes the raw signal and the SNR to record the potential 10 second bouts
        """

        ecg, fs = LoadSignal(ecg_signal_dir)

        x, _, SNR, _, _ = annotate_ecg_quality(ecg_signal=ecg, ecg_sample_rate=fs)


        start_idx = int(fs*self.bout_time)
        bout_count = 0

        labels_temp = {'bout_code': [], 'signal_dirs': [], 'fs': [], 'start_idx': [], 
                       'end_idx': [], 'SNR_avg': [], 'SNR_min': [], 'SNR_max': [], 
                       'SNR_bin': [], 'Amp_max': []}

        #Loop through 10 second bouts of the signal - skip the first and last 10 seconds
        for ii in range(int(fs*self.bout_time)*2, len(SNR), int(fs*self.bout_time)):

            stop_idx = ii
            bout_code = 'P' + str(participant_num) + '_B' + str(bout_count)

            #Find the data based on the start and stop indices
            SNR_avg = np.nanmean(SNR[start_idx:stop_idx])
            SNR_min = np.nanmin(SNR[start_idx:stop_idx])
            SNR_max = np.nanmax(SNR[start_idx:stop_idx])
            SNR_bin = np.where(np.logical_and(SNR_min >= self.SNR_ranges[:,0],
                                              SNR_max <= self.SNR_ranges[:,1]),
                                              True, False)
            SNR_bin = np.argmax(SNR_bin)
            amp_max = np.nanmax(np.abs(x[start_idx:stop_idx]))

            #Append everthing to the main dictionary
            labels_temp['bout_code'].append(bout_code)
            labels_temp['signal_dirs'].append(ecg_signal_dir)
            labels_temp['fs'].append(fs)
            labels_temp['start_idx'].append(start_idx)
            labels_temp['end_idx'].append(stop_idx)
            labels_temp['SNR_avg'].append(SNR_avg)
            labels_temp['SNR_min'].append(SNR_min)
            labels_temp['SNR_max'].append(SNR_max)
            labels_temp['SNR_bin'].append(SNR_bin)
            labels_temp['Amp_max'].append(amp_max)

            start_idx = stop_idx+1
            bout_count+=1
        
        self.labels_df = pd.concat([self.labels_df, pd.DataFrame(labels_temp)], ignore_index=True)

    def SampleSignals(self):
        """
        Pull even from each bin, then randomly for the left overs

        This set is appended on the other sampled set
        """

        with alive_bar(self.n_bouts, force_tty=True) as bar:
            for ii in range(self.n_bouts):

                SNR_index = np.floor(ii/(self.binCounts)).astype(int)

                #Need to account for remainder after
                if SNR_index >= self.n_bins:
                    #Select random bin to fill up at the end
                    SNR_index = randint(0, self.n_bins-1)

                #Find the indicies that are good based on the SNR range
                eligible_rows = self.labels_df[self.labels_df['SNR_bin']==SNR_index]

                if eligible_rows.shape[0] < self.binCounts+1:
                    print('Not enough eligible bouts')
                    exit()

                #Sample from the bouts within the bin
                selected_bout = eligible_rows.sample(1)

                #Keep sampling until a bout is found that is not in the ECG_sample_directory already
                while selected_bout['bout_code'].to_numpy() in self.sample_df['bout_code'].to_numpy():
                    selected_bout = eligible_rows.sample(1)

                #Add the selected bout to the sample_dictionary
                self.sample_df = pd.concat([self.sample_df, selected_bout], ignore_index=True)

                bar()

    def SampleLoader(self):
        """SampleLoader Loads the samples saved and saves all the signals in an array
        """

        with alive_bar(self.n_bouts, force_tty=True) as bar:
            for ii, bout_code in enumerate(self.sample_df['bout_code']):

                bout_df = self.sample_df[self.sample_df['bout_code'] == bout_code]

                ecg, fs = LoadSignal(bout_df['signal_dirs'].to_numpy()[0], bout_df['start_idx'], bout_df['end_idx']+1)

                if ii == 0:
                    self.sample_signals = ecg
                else:
                    self.sample_signals = np.vstack((self.sample_signals, ecg))

                bar()




if __name__ == '__main__':


    ECGFinder = ECGDictionary()

    signals_dir = r'Y:\NiMBaLWEAR\OND09\wearables\device_edf_cropped'
    save_dir = r'Z:\ONDRI\ECG Quality Survey'

    #Not sure what SBH and TWH are???
    try:
        ECGFinder.labels_df = pd.read_csv(os.path.join(save_dir, 'Signal Details', 'ECG_labels.csv'))
    except:
        ecg_signal_paths = []
        for file in os.listdir(signals_dir):
            if 'Chest.edf' in file and 'SBH' not in file and 'TWH' not in file and 'OND09_0003_01' not in file:
                ecg_signal_paths.append(os.path.join(signals_dir, file))

        with alive_bar(len(ecg_signal_paths), force_tty=True) as bar:
            for ii, signal_dir in enumerate(ecg_signal_paths):
                ECGFinder.LabelSignals(participant_num=ii, ecg_signal_dir=signal_dir)
                bar()

        #Save signal details here since that should not change
        ECGFinder.labels_df.to_csv(os.path.join(save_dir, 'Signal Details', 'ECG_labels.csv'), index=False)

    #Sample the signals
    try:
        ECGFinder.sample_df = pd.read_csv(os.path.join(save_dir, 'Signal Details', 'ECG_samples.csv'))
    except FileNotFoundError:
        ECGFinder.SampleSignals()
        ECGFinder.sample_df.to_csv(os.path.join(save_dir, 'Signal Details', 'ECG_samples.csv'), index=False)

    #Load samples data
    try:
        ECGFinder.sample_signals = PickleLoad(os.path.join(save_dir, 'Signal Details', 'sample_signals.pkl'))
    except FileNotFoundError:
        ECGFinder.SampleLoader()
        PickleDump(ECGFinder.sample_signals, os.path.join(save_dir, 'Signal Details', 'sample_signals.pkl'))

