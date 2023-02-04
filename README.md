# ECG_Plotting

Codebase for GUI that can be used for displaying 10 second bouts of ECG signals which can then be easily classified into 3 signal quality categories.

This code was designed with the intention of annotating data provided by the [NiMBaL](https://github.com/nimbal) group

## File Breakdown

### ECG_survey_GUI.py

Script for generating a Tkinter survey based generated ECG images

### ECGmain.py

Loops through the available ECG data from the [NiMBaL](https://github.com/nimbal) group, and samples 10 second bouts based on the predicted signal to noise ratio

### ecg_strip_charts.py

Produces ECG strip chart plots that mimic the format used in clinic
