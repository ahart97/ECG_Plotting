import tkinter as tk
from tkinter import ttk
from PIL import ImageTk, Image
import os
import numpy as np
import pandas as pd
from tkinter.messagebox import askokcancel, showwarning

class Annotation(ttk.Frame): 
    def __init__(self, notebook, cwd, ecg_details, gui):
        super().__init__(notebook)

        self.annotation_frame = tk.Frame(self)
        self.annotation_frame.place(relx=0.5, rely=0.35, anchor='center')

        # opt_selected holds an integer value which is used for
        # selected option in a question.
        #Make one for every radio button set (i.e. 6)
        self.opt_selected=[tk.IntVar(value=1) for ii in range(6)]

        #Make dictionary to store the results for each page
        self.results = {}

        # set question number to -1 (starts at welcome page)
        self.q_no=-1

        #Make options for the selection
        self.quality_options = np.array(['Q1', 'Q2', 'Q3'])

        #Set an tracking object for valid answers
        self.invalid_answers_found = False

        #Sets the list of ECG plot locations
        self.ecg_plots = []
        for ii, plot_name in enumerate(ecg_details['plot_dirs']):
            self.ecg_plots.append(os.path.join(cwd, plot_name))

        self.gui = gui

        self.welcome_screen()
        self.buttons()


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
                
                finished_ans = askokcancel(
                    title='Confirmation',
                    message='Finished annotations, results will save on exit.'
                    )
                
                if finished_ans:
                    # destroys the GUI if through all of the signals
                    self.gui.destroy()

                else:
                    self.q_no -= 1
                    # shows the next question
                    self.display_plot()
                    self.buttons()
                    self.QualityBlurb()
                    self.ResetAnswers()
                    self.opts=self.radio_buttons()
                #Saves once destroyed

            else:
                # shows the next question
                self.display_plot()
                self.buttons()
                self.QualityBlurb()
                self.ResetAnswers()
                self.opts=self.radio_buttons()
        else:
            self.display_warning()
            self.invalid_answers_found = True

    def GetAnswers(self):
        """
        Get the answers from the pages after the next button has been selected
        """
        page_answers = []
        for answer in self.opt_selected:
            page_answers.append(self.quality_options[answer.get()-1])
        
        self.results[self.image_name] = page_answers

    def buttons(self):
        """
        Makes the buttons on the page for next and previous function
        """
         
        next_button = tk.Button(self, text="Next",command=self.next_btn,width=10,bg="blue",fg="white",font=("ariel",16,"bold"))
        next_button.place(relx=0.95,rely=0.9, anchor='center')

        prev_button = tk.Button(self, text="Previous",command=self.previous_btn,width=10,bg="blue",fg="white",font=("ariel",16,"bold"))
        prev_button.place(relx=0.85,rely=0.9, anchor='center')

    def QualityBlurb(self):
        """
        Adds a blurb to each page about the quality

        Also adds the page count at the bottom
        """
        
        quality_txt = "Select a quality for each signal\nQ1 = Best Quality | Q2 = Moderate Quality | Q3 = Poor Quality"
        quality_blurb = tk.Label(self.annotation_frame, text=quality_txt, fg="black", font=("ariel", 20, "bold"))
        quality_blurb.grid(row=0, column=0, columnspan=4, pady=30)

        page_number_txt = "Page {}/{}".format(self.q_no+1, len(self.ecg_plots))
        page_number = tk.Label(self, text=page_number_txt, fg="black", font=("ariel", 12, "bold"))
        page_number.place(relx=0.5, rely=0.95, anchor="center")

    def display_warning(self):
        warning_txt = "Assign a quality to every signal before clicking Next"
        self.warning_blurb = showwarning(title='Annotations Incomplete', message=warning_txt)

    def display_plot(self):
        """
        Make a label for the plot
        """
        self.image_name = self.ecg_plots[self.q_no]
        img = ImageTk.PhotoImage(Image.open(self.ecg_plots[self.q_no]))
        ecg_plot = tk.Label(self.annotation_frame, image = img)
        ecg_plot.image=img
        ecg_plot.grid(row=1, column=3, rowspan=8, padx=20)


    def welcome_screen(self):
        """
        Shown a welcome screen
        """
        self.welcome_msg = tk.Label(self, text="Click next to start the survey",fg="black", font=("ariel", 20, "bold"))
        self.welcome_msg.place(relx=0.5, rely=0.5, anchor='center')

    def radio_buttons(self):
        
        # initialize the list with an empty list of options
        q_list = []
        
        # position of the first option
        y_pos = 0.32 #Tune
        x_pos = 0.10
        
        # adding the options to the list
        for ii in range(len(self.opt_selected)):
            
            # setting the radio button properties
            radio_Q1 = tk.Radiobutton(self.annotation_frame,text="Q1",variable=self.opt_selected[ii],
            value = 1,font = ("ariel",14))
            radio_Q2 = tk.Radiobutton(self.annotation_frame,text="Q2",variable=self.opt_selected[ii],
            value = 2,font = ("ariel",14))
            radio_Q3 = tk.Radiobutton(self.annotation_frame,text="Q3",variable=self.opt_selected[ii],
            value = 3,font = ("ariel",14))
            
            # adding the button to the list
            q_list.append([radio_Q1, radio_Q2, radio_Q3])
            
            # placing the buttons
            radio_Q1.grid(row=ii+2, column=0, padx=10, pady=5)
            radio_Q2.grid(row=ii+2, column=1, padx=10, pady=5)
            radio_Q3.grid(row=ii+2, column=2, padx=10, pady=5)
        
        # return the radio buttons
        return q_list

