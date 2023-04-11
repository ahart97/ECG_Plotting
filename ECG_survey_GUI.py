import tkinter as tk
from tkinter import ttk
from tkinter.messagebox import showwarning
from PIL import ImageTk, Image
import os
import numpy as np
import pandas as pd
from Tabs.QualityDef import QualityDef
from Tabs.Annotation import Annotation
from tkinter.messagebox import askokcancel, showwarning

#class to define the components of the GUI
class Survey:
    def __init__(self, cwd, ecg_details, rater_code):

        # Create a GUI Window
        self.gui = tk.Tk()

        #Set the closing protocol
        self.gui.protocol("WM_DELETE_WINDOW", self.close_window)

        # set the size of the GUI Window
        self.gui.geometry("1920x1080")
        # set the title of the Window
        self.rater_code = rater_code
        self.gui.title("ECG Survey (Rater: {})".format(self.rater_code))
        #Get the width and height
        self.gui_width = self.gui.winfo_screenwidth()
        self.gui_height = self.gui.winfo_screenheight()

        #Limit the sizes to keep things consitent
        self.gui.minsize(1920, 1080)
        self.gui.maxsize(1920,1080)

        self.display_title()

        # Create a Notebook widget
        self.notebook = ttk.Notebook(self.gui)

        # Create two tabs
        self.annotationTab = Annotation(self.notebook, cwd, ecg_details, self.gui)
        self.detailTab = QualityDef(self.notebook)

        # Add the tabs to the notebook
        self.notebook.add(self.annotationTab, text="Annotations")
        self.notebook.add(self.detailTab, text="Quality Definitions")

        # Pack the notebook widget
        self.notebook.pack(expand=True, fill="both")

    def close_window(self):
        finished_ans = askokcancel(
                    title='Confirmation',
                    message='Exiting annotations, results will save on exit.'
                    )
                
        if finished_ans:
            # destroys the GUI if through all of the signals
            self.gui.destroy()

    # This method is used to Display Title
    def display_title(self):
        
        # The title to be shown
        title = tk.Label(self.gui, text="ECG Survey",
        width=100, bg="green",fg="white", font=("ariel", 20, "bold"))
        
        # place of the title
        title.pack(side=tk.TOP, padx=10, pady=10)


    def SaveResults(self):
        formatted_results = {}

        for plot in self.annotationTab.results.keys():
            formatted_key = os.path.split(plot)[-1]
            formatted_results[formatted_key] = self.annotationTab.results[plot]

        pd.DataFrame(formatted_results).transpose().to_csv('Results_{}.csv'.format(self.rater_code))


if __name__ == '__main__':
    
    rater_code = 'a'

    nre_dir = r'Z:\ONDRI\ECG Quality Survey'
    plot_details = pd.read_csv(os.path.join(nre_dir, 'Signal Details', 'plot_details_{}_short.csv'.format(rater_code)))

    #Load in the ECG plots (would need to pass these in a folder with the .exe)
    #cwd = os.getcwd().split('\\ECG_Plotting')[0]
    #plot_details = pd.read_csv(os.path.join(cwd, 'Signal Details', 'plot_details_a.csv'))

    # create an object of the Quiz Class.
    quiz = Survey(nre_dir, plot_details, rater_code)

    # Start the GUI
    quiz.gui.mainloop()

    quiz.SaveResults()

    #Use below to make the .exe (need the onefile argument)
    #pyinstaller --onefile program.py 
    #Open terminal in that dir
    #pyinstaller --onefile "ECG_survey_GUI.py"

    #Then move the Plots and Signal Details (just plot details) folders in the dist dir with the .exe (just need these two folders and .exe, basically the dir folder here)
