'''
Jack Miller
Apex Companies
August 2024
'''

from typing import Literal, Callable
from customtkinter import CTkFrame, CTkButton, CTkLabel, CTkCheckBox, CTkSwitch, filedialog, StringVar, DoubleVar, BooleanVar

from apex_gui.frames.custom_widgets import Frame
from apex_gui.frames.notification_dialogs import NotificationDialog
from apex_gui.frames.styled_widgets import PositiveButton, NegativeButton
from apex_gui.styles.colors import *

class StaticValueWithLabel(Frame):

    def __init__(self, master, value: str, label_text: str) -> None:
        super().__init__(master=master)

        self.label = CTkLabel(self, text=f'{label_text}:')  
        self.entry = CTkLabel(self, text=value)

        self.label.grid(row=0,column=0, sticky='w')
        self.entry.grid(row=0,column=1, sticky='e', padx=(5,0))


class ConfirmDeleteDialog(NotificationDialog):

    def __init__(self, master, title: str, text: str, positive_action: Callable, negative_action: Callable):
        super().__init__(master, title=title, text=text)

        self.positive_action_func: Callable = positive_action
        self.negative_action_func: Callable = negative_action

        self.negative_action_btn = PositiveButton(self.get_action_buttons_frame(), text='No', command=self.negative_action)
        self.negative_action_btn.grid(row=0, column=0)

        self.positive_action_btn = PositiveButton(self.get_action_buttons_frame(), text='Yes', command=self.positive_action)
        self.positive_action_btn.grid(row=0, column=1, padx=(5,0))

    def positive_action(self):
        self.positive_action_func()
        self.destroy()
    
    def negative_action(self):
        self.negative_action_func()
        self.destroy()