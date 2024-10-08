'''
Jack Miller
Apex Companies
August 2024
'''

from typing import Literal, Callable
from customtkinter import CTkTextbox, CTkEntry, CTkLabel, CTkOptionMenu, CTkScrollableFrame, CTkFrame, StringVar, DoubleVar, BooleanVar

from apex_gui.frames.notification_dialogs import NotificationDialog, ResultsDialog
from apex_gui.frames.custom_widgets import EntryWithLabel
from apex_gui.frames.styled_widgets import Frame, Section, PositiveButton, NegativeButton
from apex_gui.helpers.constants import EntryType
from apex_gui.styles.colors import *
from apex_gui.styles.fonts import AppFont, SectionHeaderFont

from ..models.ProjectInfo import BaseProjectInfo

class StaticValueWithLabel(Frame):

    def __init__(self, master, value: str, label_text: str, alignment: str = 'horizontal') -> None:
        if alignment not in ['horizontal', 'vertical']:
            raise ValueError(f'Argument "alignment" received illegal value: {alignment}')
        
        super().__init__(master=master)

        self.variable = StringVar(self, value)

        self.label = CTkLabel(self, text=f'{label_text}')  
        # self.entry = CTkLabel(self, text=value, wraplength=400)
        self.entry = CTkEntry(self, textvariable=self.variable, state='disabled')

        if alignment == 'horizontal':
            self.grid_rowconfigure(0, weight=1)
            self.grid_columnconfigure([0,1], weight=1)

            self.label.grid(row=0,column=0, sticky='w')
            self.entry.grid(row=0,column=1, sticky='e', padx=(5,0))
        else:
            self.grid_rowconfigure(1, weight=1)
            self.grid_columnconfigure(0, weight=1)

            self.label.grid(row=0,column=0, sticky='w')
            self.entry.grid(row=1, column=0, sticky='ew', pady=(5,0))

        # self.label.grid(row=0,column=0, sticky='w')
        # self.entry.grid(row=0,column=1, sticky='e', padx=(5,0))

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

        self.negative_action_btn = NegativeButton(self.get_action_buttons_frame(), text='No', command=self.negative_action)
        self.negative_action_btn.grid(row=0, column=0)

        self.positive_action_btn = PositiveButton(self.get_action_buttons_frame(), text='Yes', command=self.positive_action)
        self.positive_action_btn.grid(row=0, column=1, padx=(5,0))

    def positive_action(self):
        self.destroy()
        self.positive_action_func()
    
    def negative_action(self):
        self.destroy()
        self.negative_action_func()


class ResultsDialogWithLogFile(ResultsDialog):
    def __init__(self, master, success: bool, text: str, log_file_path: str):
        title = 'Success!' if success else 'Error'
        super().__init__(master, title=title, body_text=text, button_text='Open Log', results_dir=log_file_path)


class TextboxWithLabel(Frame):

    def __init__(self, master, default_val: str, label_text: str, alignment: str = 'vertical', textbox_height: int = 28, textbox_width: int = 140) -> None:
        if alignment not in ['horizontal', 'vertical']:
            raise ValueError(f'Argument "alignment" received illegal value: {alignment}')
        
        super().__init__(master=master)

        self.label = CTkLabel(self, text=label_text)  
        self.textbox = CTkTextbox(master=self, wrap='word', height=textbox_height, width=textbox_width)
        self.set_text(default_val)

        if alignment == 'horizontal':
            self.grid_rowconfigure(0, weight=1)
            self.grid_columnconfigure([0,1], weight=1)

            self.label.grid(row=0,column=0, sticky='w')
            self.textbox.grid(row=0,column=1, sticky='e', padx=(5,0))
        else:
            self.grid_rowconfigure(1, weight=1)
            self.grid_columnconfigure(0, weight=1)

            self.label.grid(row=0,column=0, sticky='w')
            self.textbox.grid(row=1, column=0, sticky='ew', pady=(5,0))

    def get_text(self):
        t = self.textbox.get(0.0, 'end-1c')
        # return sanitize_text(t)
        return t

    def set_text(self, val):
        self.textbox.insert(0.0, val, 'end-1c')

    def clear_input(self):
        self.set_text('')

    # def has_valid_input(self):
    #     return self.entry.has_valid_input()



class ProjectInfoFrame(Frame):

    def __init__(self, master, title: str, submit_btn_text: str, submit_btn_action: Callable):
        super().__init__(master)

        ''' Create '''

        self.title = CTkLabel(self, text=title, font=SectionHeaderFont())

        # self.container = CTkScrollableFrame(self, scrollbar_fg_color=APEX_IVORY_MEDIUM_SHADE, fg_color=WHITE, border_color=APEX_IVORY_MEDIUM_SHADE, border_width=2, corner_radius=15, width=500, height=600)
        self.container = SectionWithScrollbar(self, width=500, height=600)

        self.project_name = EntryWithLabel(self.container, label_text='Project Name', default_val='', entry_type=EntryType.String, entry_width=240)
        self.company = EntryWithLabel(self.container, label_text='Company', default_val='', entry_type=EntryType.String, entry_width=240)
        self.company_location = EntryWithLabel(self.container, label_text='Location', default_val='', entry_type=EntryType.String, entry_width=240)
        self.salesperson = EntryWithLabel(self.container, label_text='Salesperson', default_val='', entry_type=EntryType.String, entry_width=240)
        self.email = EntryWithLabel(self.container, label_text='Email', default_val='', entry_type=EntryType.String, entry_width=240)
        self.start_date = EntryWithLabel(self.container, label_text='Start Date (yyyy-mm-dd)', default_val='', entry_type=EntryType.Date, entry_width=240)
        self.notes = TextboxWithLabel(self.container, label_text='Notes', default_val='', alignment='vertical', textbox_height=28*4)
        
        self.submit_btn = PositiveButton(self, text=submit_btn_text, command=submit_btn_action)


        ''' Grid '''
        
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)
        
        self.title.grid(row=0, column=0, sticky='ew', padx=50, pady=(20, 0))
        self.container.grid(row=1, column=0, sticky='nsew', padx=5, pady=20)
        self.submit_btn.grid(row=2, column=0, padx=50, pady=(0, 20))

        self.container.grid_columnconfigure(0, weight=1)
        # self.container.grid_rowconfigure(0, weight=1)
       
        self.project_name.grid(row=1, column=0, sticky='ew', padx=20, pady=(5, 0))
        self.company.grid(row=2, column=0, sticky='ew', padx=20, pady=(20, 0))
        self.company_location.grid(row=3, column=0, sticky='ew', padx=20, pady=(20, 0))
        self.salesperson.grid(row=4, column=0, sticky='ew', padx=20, pady=(20, 0))
        self.email.grid(row=5, column=0, sticky='ew', padx=20, pady=(20, 0))
        self.start_date.grid(row=6, column=0, sticky='ew', padx=20, pady=(20, 0))
        self.notes.grid(row=7, column=0, sticky='ew', padx=20, pady=(20,5))

        

    def has_valid_inputs(self):
        return self.start_date.has_valid_input()

    def get_project_info_inputs(self, project_number) -> BaseProjectInfo:
        project_info = BaseProjectInfo(
            project_number=project_number,
            project_name=self.project_name.get_variable_value(),
            company_name=self.company.get_variable_value(),
            company_location=self.company_location.get_variable_value(),
            email=self.email.get_variable_value(),
            salesperson=self.salesperson.get_variable_value(),
            start_date=self.start_date.get_variable_value(),
            notes=self.notes.get_text()
        )

        return project_info

    def set_project_info(self, project_info: BaseProjectInfo):
        self.project_name.set_variable_value(project_info.project_name)
        self.company.set_variable_value(project_info.company_name)
        self.company_location.set_variable_value(project_info.company_location)
        self.email.set_variable_value(project_info.email)
        self.salesperson.set_variable_value(project_info.salesperson)
        self.start_date.set_variable_value(project_info.start_date)
        self.notes.set_text(project_info.notes)

    def clear_frame(self):
        self.project_name.clear_input()
        self.company.clear_input()
        self.company_location.clear_input()
        self.email.clear_input()
        self.salesperson.clear_input()
        self.start_date.clear_input()
        self.notes.clear_input()


class SectionWithScrollbar(CTkScrollableFrame):
    def __init__(self, master, width: int = 200, height: int = 200):
        super().__init__(master, fg_color=WHITE, border_color=APEX_IVORY_MEDIUM_SHADE, scrollbar_fg_color=APEX_IVORY_MEDIUM_SHADE, 
                         border_width=2, corner_radius=15, width=width, height=height)