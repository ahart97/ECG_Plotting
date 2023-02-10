# Project Title: ECG Bout Sampling and Annotation GUI

## Description
This repository contains a Python implementation for loading ECG data, generating 10-second bouts from the data, and sampling the bouts based on the estimated signal to noise ratio generated from a stationary wavelet signal quality algorithm. The resulting sampled bouts are organized in a graphical user interface (GUI) built with tkinter, which can be used for comparing the algorithm's signal quality annotations to clinician annotations.

## Installation
To use this repository, you will need to have the following packages installed:

- Python 3
- NumPy
- Matplotlib
- Tkinter
- PIL
- nwecg (from the [NiMBaL](https://github.com/nimbal) group)
- nimbalwear (from the [NiMBaL](https://github.com/nimbal) group)
- numpy
- pandas

You can install these packages using pip or another package manager.

## Usage
The repository contains the following files:

- ECG_survey_GUI.py - Script for generating a Tkinter survey based generated ECG images
- ECGmain.py - Loops through the available ECG data from the [NiMBaL](https://github.com/nimbal) group, and samples 10 second bouts based on the predicted signal to noise ratio
- ecg_strip_charts.py - Produces ECG strip chart plots that mimic the format used in clinic (not available in public repo due to privacy issues)

## Contributing
If you would like to contribute to this repository, please fork the repository and make the necessary changes. Then, submit a pull request for review.

