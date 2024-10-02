'''
Jack Miller
Apex Companies
August 2024
'''

from typing import Literal, Callable
from customtkinter import CTkFrame, CTkEntry, CTkLabel, CTkCheckBox, CTkSwitch, filedialog, StringVar, DoubleVar, BooleanVar

from apex_gui.frames.custom_widgets import Frame

class StaticValueWithLabel(Frame):

    def __init__(self, master, value: str, label_text: str) -> None:
        super().__init__(master=master)

        self.label = CTkLabel(self, text=f'{label_text}:')  
        self.entry = CTkLabel(self, text=value)

        self.label.grid(row=0,column=0, sticky='w')
        self.entry.grid(row=0,column=1, sticky='e', padx=(5,0))