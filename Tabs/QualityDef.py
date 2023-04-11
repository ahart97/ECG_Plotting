import tkinter as tk
from tkinter import ttk
from PIL import ImageTk, Image
import os
import numpy as np
import pandas as pd

class QualityDef(ttk.Frame): 
    def __init__(self, notebook):
        super().__init__(notebook)

        self.defineQualityLabels()
        self.defineLayout()


    def defineQualityLabels(self):
        self.Q1_detials = 'Q1 Signals: Suitable for full ECG wave analysis, it is possible to reliably detect the QRS complex and five other significant points in the ECG curve (P onset, P offset, QRS onset, QRS offset, T offset).'
        self.Q2_detials = 'Q2 Signals: Must be possible to reliably detect the QRS complexes.'
        self.Q3_detials = 'Q3 Signals: Detection of QRS complexes is not guaranteed.'

    def defineLayout(self):
        bold_font = ("TkDefaultFont", 20, "bold")

        self.q1_label = tk.Label(self, text=self.Q1_detials, font=bold_font, wraplength=1800)
        self.q1_label.pack(side="top", pady=50, padx=50)
        self.q2_label = tk.Label(self, text=self.Q2_detials, font=bold_font)
        self.q2_label.pack(side="top", pady=50, padx=50)
        self.q3_label = tk.Label(self, text=self.Q3_detials, font=bold_font)
        self.q3_label.pack(side="top", pady=50, padx=50)

