'''
Jack Miller
Apex Companies
August 2024
'''

from typing import Literal, Callable
from customtkinter import CTkFrame, CTkButton, CTkLabel, CTkOptionMenu, CTkSwitch, filedialog, StringVar, DoubleVar, BooleanVar

from apex_gui.frames.custom_widgets import Frame
from apex_gui.frames.notification_dialogs import NotificationDialog
from apex_gui.frames.styled_widgets import PositiveButton, NegativeButton
from apex_gui.styles.colors import *
from apex_gui.styles.fonts import AppFont

class StaticValueWithLabel(Frame):

    def __init__(self, master, value: str, label_text: str) -> None:
        super().__init__(master=master)

        self.label = CTkLabel(self, text=f'{label_text}:')  
        self.entry = CTkLabel(self, text=value)

        self.label.grid(row=0,column=0, sticky='w')
        self.entry.grid(row=0,column=1, sticky='e', padx=(5,0))

class DropdownWithLabel(Frame):

    def __init__(self, master, label_text: str, default_val: str, dropdown_values: list, label_font: AppFont | None = None, **kwargs):
        super().__init__(master=master, **kwargs)

        self.dropdown_values = dropdown_values
        self.variable = StringVar(self, default_val)

        if label_font == None:
            label_font = AppFont(size=14)

        self.label = CTkLabel(self, text=label_text, font=label_font)
        self.dropdown = CTkOptionMenu(self, variable=self.variable, values=dropdown_values)

        # Grid
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure([0,1], weight=1)

        self.label.grid(row=0, column=0, sticky='ew')
        self.dropdown.grid(row=1, column=0, sticky='ew')

    def get_variable_value(self) -> str:
        return self.variable.get()


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
        self.destroy()
        self.positive_action_func()
    
    def negative_action(self):
        self.destroy()
        self.negative_action_func()