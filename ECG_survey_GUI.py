import tkinter as tk
from tkinter import messagebox as mb
from PIL import ImageTk, Image
import os
import numpy as np
import pandas as pd

#class to define the components of the GUI
class Survey:
    def __init__(self, cwd, ecg_details):

        # Create a GUI Window
        self.gui = tk.Tk()
        # set the size of the GUI Window
        self.gui.geometry("1920x1080")
        # set the title of the Window
        self.gui.title("ECG Survey")
        #Get the width and height
        self.gui_width = self.gui.winfo_screenwidth()
        self.gui_height = self.gui.winfo_screenheight()

        # set question number to -1 (starts at welcome page)
        self.q_no=-1

        # opt_selected holds an integer value which is used for
        # selected option in a question.
        #Make one for every radio button set (i.e. 6)
        self.opt_selected=[tk.IntVar(value=1) for ii in range(6)]

        #Make dictionary to store the results for each page
        self.results = {}

        #Make options for the selection
        self.quality_options = np.array(['Q1', 'Q2', 'Q3'])

        #Set an tracking object for valid answers
        self.invalid_answers_found = False

        #Sets the list of ECG plot locations
        self.ecg_plots = []
        for ii, plot_name in enumerate(ecg_details['plot_dirs']):
            self.ecg_plots.append(os.path.join(cwd, plot_name))
        
        #Display welcome screen
        self.display_title()
        self.welcome_screen()
        self.buttons()

    def GetAnswers(self):
        """
        Get the answers from the pages after the next button has been selected
        """
        page_answers = []
        for answer in self.opt_selected:
            page_answers.append(self.quality_options[answer.get()-1])
        
        self.results[self.image_name] = page_answers

    def CheckAnswers(self):
        """
        Check the answers to make sure every radio button set has been filled
        """
        for answer in self.opt_selected:
            if answer.get() == 0:
                return False
            
        return True

    def ResetAnswers(self):
        """
        Reset all the readio button options to zero before the next page
        """

        try:
            #Get the answers from the previous entry - if there are any
            page_answers = self.results[self.ecg_plots[self.q_no]]

            #Set the radio buttons to those answers
            for ii, option in enumerate(self.opt_selected):
                answer = np.where(self.quality_options==page_answers[ii])[0][0] + 1
                self.opt_selected[ii].set(answer)
        except:
            for ii, option in enumerate(self.opt_selected):
                self.opt_selected[ii].set(0)

    def BackStep(self):
        """
        Loads the answers from the previous step
        """

        #Get the answers from the previous page
        page_answers = self.results[self.ecg_plots[self.q_no]]

        #Set the radio buttons to those answers
        for ii, option in enumerate(self.opt_selected):
            answer = np.where(self.quality_options==page_answers[ii])[0][0] + 1
            self.opt_selected[ii].set(answer)

    def previous_btn(self):
        """
        What to do if the previous button is selected
        """

        #Check to make sure the warning page is past and at least 2 pages in
        if self.q_no > 0:
            self.q_no -= 1
            self.display_plot()
            self.buttons()
            self.QualityBlurb()
            self.BackStep()
            self.opts=self.radio_buttons()
            self.display_title()

    def next_btn(self):
        """
        What to do when the next button is selected
        """

        valid_answers = self.CheckAnswers()

        #Only continue if the answers were valid (no blank answers)
        if valid_answers:

            if self.q_no < 0:
                self.welcome_msg.destroy()
            else:
                #Get answers
                self.GetAnswers()

            #Don't want to destroy the warning after the initial page
            if self.invalid_answers_found:
                self.warning_blurb.destroy()
                self.invalid_answers_found = False

            # Moves to next Question by incrementing the q_no counter
            self.q_no += 1
            
            # checks if the q_no size is equal to the data size
            if self.q_no==len(self.ecg_plots):
                
                # destroys the GUI if through all of the signals
                self.gui.destroy()

                #Saves once destroyed

            else:
                # shows the next question
                self.display_plot()
                self.buttons()
                self.QualityBlurb()
                self.ResetAnswers()
                self.opts=self.radio_buttons()
                self.display_title()
        else:
            self.display_warning()
            self.invalid_answers_found = True

    def buttons(self):
        """
        Makes the buttons on the page for next and previous function
        """
         
        next_button = tk.Button(self.gui, text="Next",command=self.next_btn,width=10,bg="blue",fg="white",font=("ariel",16,"bold"))
        next_button.place(relx=0.95,rely=0.9, anchor='center')

        prev_button = tk.Button(self.gui, text="Previous",command=self.previous_btn,width=10,bg="blue",fg="white",font=("ariel",16,"bold"))
        prev_button.place(relx=0.85,rely=0.9, anchor='center')

    def QualityBlurb(self):
        """
        Adds a blurb to each page about the quality

        Also adds the page count at the bottom
        """
        
        quality_txt = "Select a quality for each signal\nQ1 = Best Quality | Q2 = Moderate Quality | Q3 = Poor Quality"
        quality_blurb = tk.Label(self.gui, text=quality_txt, fg="black", font=("ariel", 20, "bold"))
        quality_blurb.place(relx=0.5, rely=0.2, anchor="center")

        page_number_txt = "Page {}/{}".format(self.q_no+1, len(self.ecg_plots))
        page_number = tk.Label(self.gui, text=page_number_txt, fg="black", font=("ariel", 12, "bold"))
        page_number.place(relx=0.5, rely=0.95, anchor="center")

    def display_warning(self):
        warning_txt = "Assign a quality to every signal before clicking Next"
        self.warning_blurb = tk.Label(self.gui, text=warning_txt, fg="black", font=("ariel", 20, "bold"))
        
        # place of the title
        self.warning_blurb.place(relx=0.5, rely=0.9, anchor="center")

    def display_plot(self):
        """
        Make a label for the plot
        """
        self.image_name = self.ecg_plots[self.q_no]
        img = ImageTk.PhotoImage(Image.open(self.ecg_plots[self.q_no]))
        ecg_plot = tk.Label(self.gui, image = img)
        ecg_plot.image=img
        ecg_plot.place(relx=0.95,rely=0.5,anchor='e')


    def welcome_screen(self):
        """
        Shown a welcome screen
        """
        self.welcome_msg = tk.Label(self.gui, text="Click next to start the survey",fg="black", font=("ariel", 20, "bold"))
        self.welcome_msg.place(relx=0.5, rely=0.5, anchor='center')


    # This method is used to Display Title
    def display_title(self):
        
        # The title to be shown
        title = tk.Label(self.gui, text="ECG Survey",
        width=100, bg="green",fg="white", font=("ariel", 20, "bold"))
        
        # place of the title
        title.place(relx=0.5, rely=0.05, anchor="center")


    def radio_buttons(self):
        
        # initialize the list with an empty list of options
        q_list = []
        
        # position of the first option
        y_pos = 0.32 #Tune
        x_pos = 0.05
        
        # adding the options to the list
        for ii in range(len(self.opt_selected)):
            
            # setting the radio button properties
            radio_Q1 = tk.Radiobutton(self.gui,text="Q1",variable=self.opt_selected[ii],
            value = 1,font = ("ariel",14))
            radio_Q2 = tk.Radiobutton(self.gui,text="Q2",variable=self.opt_selected[ii],
            value = 2,font = ("ariel",14))
            radio_Q3 = tk.Radiobutton(self.gui,text="Q3",variable=self.opt_selected[ii],
            value = 3,font = ("ariel",14))
            
            # adding the button to the list
            q_list.append([radio_Q1, radio_Q2, radio_Q3])
            
            # placing the buttons
            radio_Q1.place(relx=x_pos, rely=y_pos, anchor='center')
            radio_Q2.place(relx=x_pos+0.05, rely=y_pos, anchor='center')
            radio_Q3.place(relx=x_pos+0.1, rely=y_pos, anchor='center')
            
            # incrementing the y-axis position for each signal
            y_pos += 0.072 #Tune
        
        # return the radio buttons
        return q_list

    def SaveResults(self):
        formatted_results = {}

        for plot in self.results.keys():
            formatted_key = os.path.split(plot)[-1]
            formatted_results[formatted_key] = self.results[plot]

        pd.DataFrame(formatted_results).transpose().to_csv('Results.csv')


if __name__ == '__main__':
    
    #Load in the ECG plots (would need to pass these in a folder with the .exe)
    cwd = os.getcwd().split('\\ECG_Plotting')[0]
    plot_details = pd.read_csv(os.path.join(cwd, 'Signal Details', 'plot_details_a.csv'))

    # create an object of the Quiz Class.
    quiz = Survey(cwd, plot_details)

    # Start the GUI
    quiz.gui.mainloop()

    quiz.SaveResults()

    #Use below to make the .exe (need the onefile argument)
    #pyinstaller --onefile program.py 
    #Open terminal in that dir
    #pyinstaller --onefile "ECG_survey_GUI.py"

    #Then move the Plots and Signal Details folders in the dist dir with the .exe (just need these two folders and .exe)
