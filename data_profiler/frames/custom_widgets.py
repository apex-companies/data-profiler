'''
Jack Miller
Apex Companies
Oct 2024

Custom ctk frames for DataProfiler
'''

from customtkinter import CTkToplevel, CTkLabel

# Data Profiler
from ..helpers.models.ProjectInfo import BaseProjectInfo

# Apex GUI
from apex_gui.frames.custom_widgets import EntryWithLabel, TextboxWithLabel, CheckbuttonWithLabel, DropdownWithLabel
from apex_gui.frames.styled_widgets import SectionWithScrollbar, Frame, PositiveButton
from apex_gui.helpers.constants import EntryType
from apex_gui.styles.colors import *
from apex_gui.styles.fonts import SectionSubheaderFont

class ProjectInfoFrame(SectionWithScrollbar):
    '''
    Displays basic project info and allows user to edit said info.

    Get current inputs with `get_project_info_inputs()`  
    Set project info with `set_project_info()`
    '''
    
    def __init__(self, master, show_project_number: str = False):
        super().__init__(master, width=500, height=600)    

        ''' Create '''

        self.project_number = EntryWithLabel(self, label_text='Project Number', default_val='', entry_type=EntryType.String, entry_width=240)
        self.project_name = EntryWithLabel(self, label_text='Project Name', default_val='', entry_type=EntryType.String, entry_width=240)
        self.company = EntryWithLabel(self, label_text='Company', default_val='', entry_type=EntryType.String, entry_width=240)
        self.company_location = EntryWithLabel(self, label_text='Location', default_val='', entry_type=EntryType.String, entry_width=240)
        self.salesperson = EntryWithLabel(self, label_text='Salesperson', default_val='', entry_type=EntryType.String, entry_width=240)
        self.email = EntryWithLabel(self, label_text='Email', default_val='', entry_type=EntryType.String, entry_width=240)
        self.start_date = EntryWithLabel(self, label_text='Start Date (yyyy-mm-dd)', default_val='', entry_type=EntryType.Date, entry_width=240)
        self.notes = TextboxWithLabel(self, label_text='Notes', default_val='', alignment='vertical', textbox_height=28*4)
        
        ''' Grid '''
        
        self.grid_columnconfigure(0, weight=1)
       
        if show_project_number:
            self.project_number.grid(row=0, column=0, sticky='ew', padx=20, pady=(5, 0))
            self.project_name.grid(row=1, column=0, sticky='ew', padx=20, pady=(20, 0))
        else:
            self.project_name.grid(row=1, column=0, sticky='ew', padx=20, pady=(5, 0))

        self.company.grid(row=2, column=0, sticky='ew', padx=20, pady=(20, 0))
        self.company_location.grid(row=3, column=0, sticky='ew', padx=20, pady=(20, 0))
        self.salesperson.grid(row=4, column=0, sticky='ew', padx=20, pady=(20, 0))
        self.email.grid(row=5, column=0, sticky='ew', padx=20, pady=(20, 0))
        self.start_date.grid(row=6, column=0, sticky='ew', padx=20, pady=(20, 0))
        self.notes.grid(row=7, column=0, sticky='ew', padx=20, pady=(20,5))

    def validate_inputs(self) -> list[str]:
        errors_lst = []

        # Validate project number
        if (not self.project_number.has_valid_input()) or (self.project_number.get_variable_value() == ''):
            errors_lst.append('Please enter a valid project number.')
        
        # Only other error is with start date
        if not self.start_date.has_valid_input():
            errors_lst.append(f'Invalid date format for Start Date ({self.start_date.get_variable_value()}). Date format should be "yyyy-mm-dd"')

        return errors_lst

    def get_project_info_inputs(self) -> BaseProjectInfo:
        # pn = self.project_number.get_variable_value() if self.project_number_input else project_number
        project_info = BaseProjectInfo(
            project_number=self.project_number.get_variable_value(),
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
        self.project_number.set_variable_value(project_info.project_number)
        self.project_name.set_variable_value(project_info.project_name)
        self.company.set_variable_value(project_info.company_name)
        self.company_location.set_variable_value(project_info.company_location)
        self.email.set_variable_value(project_info.email)
        self.salesperson.set_variable_value(project_info.salesperson)
        self.start_date.set_variable_value(project_info.start_date)
        self.notes.set_text(project_info.notes)

    def clear_frame(self):
        self.project_number.clear_input()
        self.project_name.clear_input()
        self.company.clear_input()
        self.company_location.clear_input()
        self.email.clear_input()
        self.salesperson.clear_input()
        self.start_date.clear_input()
        self.notes.clear_input()


class DataDirectoryFileSelectory(CTkToplevel):
    '''
    Poo
    '''

    def __init__(self, master, files: list[str]):
        super().__init__(master, fg_color=APEX_LIGHT_GRAY)

        self.geometry('800x500')
        self.title('Data Profiler')
        
        self.saved = False

        ''' Widgets '''

        # Parent = self
        self.header_label = CTkLabel(self, text='Data Directory: Select Files', font=SectionSubheaderFont())        
        self.body = SectionWithScrollbar(self)
        self.footer = Frame(self)
        
        # Parent = body        
        self.checkbuttons: dict[str, CheckbuttonWithLabel] = {}
        for file in files:
            label = CheckbuttonWithLabel(self.body, label_text=file, default_val=True)
            self.checkbuttons[file] = label

        # Parent = footer
        self.action_btns_frame = Frame(self.footer)

        # Parent = btns_frame
        self.save_btn = PositiveButton(self.action_btns_frame, text='Save', command=self.save_btn_action)

        ''' Grid '''

        # Parent = self
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1)

        self.header_label.grid(row=0, column=0)
        self.body.grid(row=1, column=0, sticky='nsew', padx=20, pady=(0,20))
        self.footer.grid(row=2, column=0)

        # Parent = body
        self.body.grid_columnconfigure(0, weight=1)

        row = 1
        for checkbutton in self.checkbuttons.values():
            checkbutton.grid(row=row, column=0, pady=10)
            row += 1

        # Parent = footer
        self.footer.grid_rowconfigure(0, weight=1)
        self.footer.grid_columnconfigure(0, weight=1)

        self.action_btns_frame.grid(row=0, column=0, pady=5)

        # Parent = btns_frame
        self.save_btn.grid(row=0, column=0)

    def get_selected_files(self):
        selected_files = []
        for file, label in self.checkbuttons.items():
            if label.get_value():
                selected_files.append(file)

        return selected_files
    
    def validate_inputs(self) -> tuple[bool, str]:
        selected_files = self.get_selected_files()

        if len(selected_files) == 0:
            return False, 'Select at least one file!'

        return True, ''

    def save_btn_action(self):
        self.set_saved(True)
        self.destroy()

    def get_saved(self):
        return self.saved
    
    def set_saved(self, saved: bool):
        self.saved = saved


class DataDescriberColumnSelector(CTkToplevel):
    '''
    Poo
    '''

    def __init__(self, master, columns: list[str]):
        super().__init__(master, fg_color=APEX_LIGHT_GRAY)

        self.geometry('800x500')
        self.title('Data Profiler')
        
        self.saved = False

        ''' Widgets '''

        # Parent = self
        self.header_label = CTkLabel(self, text='Data Describer: Select Columns', font=SectionSubheaderFont())        
        self.grouping_col_dropdown = DropdownWithLabel(self, 
                                                        label_text='Select a column for grouping', 
                                                        dropdown_values=['None'] + columns,
                                                        default_val='None')
        self.body = SectionWithScrollbar(self)
        self.footer = Frame(self)
        
        # Parent = body        
        self.checkbuttons: dict[str, CheckbuttonWithLabel] = {}
        for column in columns:
            label = CheckbuttonWithLabel(self.body, label_text=column, default_val=True)
            self.checkbuttons[column] = label

        # Parent = footer
        self.action_btns_frame = Frame(self.footer)

        # Parent = btns_frame
        self.save_btn = PositiveButton(self.action_btns_frame, text='Save', command=self.save_btn_action)

        ''' Grid '''

        # Parent = self
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1)

        self.header_label.grid(row=0, column=0)
        self.grouping_col_dropdown.grid(row=1, column=0, pady=10)
        self.body.grid(row=2, column=0, sticky='nsew', padx=20, pady=(0,20))
        self.footer.grid(row=3, column=0)

        # Parent = body
        self.body.grid_columnconfigure(0, weight=1)

        row = 1
        for checkbutton in self.checkbuttons.values():
            checkbutton.grid(row=row, column=0, pady=10)
            row += 1

        # Parent = footer
        self.footer.grid_rowconfigure(0, weight=1)
        self.footer.grid_columnconfigure(0, weight=1)

        self.action_btns_frame.grid(row=0, column=0, pady=5)

        # Parent = btns_frame
        self.save_btn.grid(row=0, column=0)

    def get_grouping_col(self):
        col = self.grouping_col_dropdown.get_variable_value()
        return None if col == 'None' else col

    def get_selected_columns(self):
        selected_columns = []
        for column, label in self.checkbuttons.items():
            if label.get_value():
                selected_columns.append(column)

        return selected_columns
    
    def validate_inputs(self) -> tuple[bool, str]:
        grouping_col = self.get_grouping_col()
        selected_cols = self.get_selected_columns()

        if len(selected_cols) == 0:
            return False, 'Select at least one column to describe!'

        if grouping_col != None and grouping_col not in selected_cols:
            return False, f'Grouping column not in selected columns!'

        return True, ''

    def save_btn_action(self):
        self.set_saved(True)
        self.destroy()

    def get_saved(self):
        return self.saved
    
    def set_saved(self, saved: bool):
        self.saved = saved