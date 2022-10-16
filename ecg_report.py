import os
import numpy as np
from matplotlib import pyplot as plt
from matplotlib.ticker import AutoMinorLocator
import pickle

#Have hear just for debugging
def PickleLoad(filepath):
    """
    Loads an object from a pickle filepath 
    """
    with open(filepath, 'rb') as f:
        obj = pickle.load(f)
    return obj

def create_chart_plots(ecg: np.ndarray, fs: float, save_path: str, title: str, chart_width=250, chart_height=150,
                       ecg_amp=1, line_w=0.5, timetick=0.2):

    '''
    ecg: Nx15second array where N are the number of signals, will iterate through all the signals to display
    :param study_dir:
    :param subject_id:
    :param coll_id:
    :param device_location:
    :param report_dir:
    :param chart_width: mm
    :param chart_height: mm
    :param ecg_amp: +/- mV shown on each chart row
    :param line_w: 0.5
    :param timetick: 0.2
    :return:
    '''

    # STRIP CHART PLOT SETTINGS ############################

    XSCALE = 25  # 25 mm per second
    YSCALE = 10  # 10 mm per mV

    row_height = ecg_amp * 2 * YSCALE
    row_seconds = chart_width / XSCALE
    chart_mv = chart_height / YSCALE
    chart_rows = int(chart_height / row_height)

    row_offsets = np.arange(chart_rows, 0, -1) * ecg_amp * 2 - ecg_amp

    #############################################################

    period = 1 / fs
    ecg = ecg / 1000

    row_samples = int(row_seconds * fs)
    strip_rows = len(ecg)/row_samples
    pad_width = (strip_rows * row_samples) - len(ecg)
    ecg_strip = np.pad(ecg, (0, int(pad_width)), mode='constant', constant_values=None)
    ecg_strip = np.reshape(ecg_strip, (-1, row_samples)).T
    ecg_strip_means = np.nanmean(ecg_strip, 0)
    ecg_strip = ecg_strip - ecg_strip_means

    #TODO: Need to find a way to iterate through these

    ecg_strip_chart = ecg_strip

    ecg_offsets = row_offsets[:ecg_strip_chart.shape[-1]]
    ecg_strip_chart = ecg_strip_chart + ecg_offsets

    time = np.arange(0, ecg_strip_chart.shape[0] * period, period)
    time = np.vstack((time,) * ecg_strip_chart.shape[1]).T

    fig_bottom_mm = 5
    fig_top_mm = 5
    fig_left_mm = 1
    fig_right_mm = 1

    fig_height = chart_height + fig_top_mm + fig_bottom_mm
    fig_width = chart_width + fig_left_mm + fig_right_mm
    chart_bottom = fig_bottom_mm / fig_height
    chart_top = 1 - (fig_top_mm / fig_height)
    chart_left = fig_left_mm / fig_width
    chart_right = 1 - (fig_right_mm / fig_width)

    fig_size = (chart_width / 25.4, fig_height / 25.4)  # convert to inches
    fig = plt.figure(figsize=fig_size)
    plt.subplots_adjust(left=chart_left, right=chart_right, bottom=chart_bottom, top=chart_top, hspace=0, wspace=0)
    ax = plt.subplot(1, 1, 1)

    # PLOT A SINGLE AX
    ax.set_xticks(np.arange(0, row_seconds, timetick))
    ax.set_yticks(np.arange(0, chart_mv, 0.5))

    # ax.set_yticklabels([])
    # ax.set_xticklabels([])

    ax.minorticks_on()

    ax.xaxis.set_minor_locator(AutoMinorLocator(5))

    #ax.title.set_text(f"{arr} detected at: {r['start_time']}")

    ax.set_xlim(0, row_seconds)
    ax.set_ylim(0, chart_mv)

    ax.grid(which='major', linestyle='-', linewidth='0.5', color='red')
    ax.grid(which='minor', linestyle='-', linewidth='0.5', color=(1, 0.7, 0.7))

    ax.plot(time, ecg_strip_chart, linewidth=line_w, color='black')

    ax.spines['bottom'].set_color('red')
    ax.spines['top'].set_color('red')
    ax.spines['left'].set_color('red')
    ax.spines['right'].set_color('red')
    [t.set_visible(False) for t in ax.get_xticklines(minor=True)]
    [t.set_visible(False) for t in ax.get_yticklines(minor=True)]
    [t.set_visible(False) for t in ax.get_xticklines(minor=False)]
    [t.set_visible(False) for t in ax.get_yticklines(minor=False)]
    [l.set_visible(False) for l in ax.get_xticklabels()]
    [l.set_visible(False) for l in ax.get_yticklabels()]

    settings_msg = f"{XSCALE} mm/s  {YSCALE} mm/mV  {int(fs)} Hz"
    plt.figtext(chart_left, 0.01, settings_msg, fontname='serif', fontsize=10)

    # TODO: add to image indication, time, context, etc.
    # TODO: pad i and j so filename is sortable

    plt.savefig(os.path.join(save_path, title + '.png'))
    plt.close()

    return


if __name__ == '__main__':

    save_dir = os.path.dirname(os.path.realpath(__file__))
    signal = PickleLoad(os.path.join(save_dir, 'test_signal.pickle'))
    fs = PickleLoad(os.path.join(save_dir, 'test_fs.pickle'))

    create_chart_plots(signal, fs, save_dir, 'test', chart_width=375, chart_height=int(20*len(signal)/(15*fs)))