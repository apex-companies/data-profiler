'''
Jack Miller
Apex Companies
Oct 2024

GUI for data profiler app. Creates an instance of DataProfiler as backend logic and to interact with database
'''

from pprint import pprint

import customtkinter
from customtkinter import CTkScrollableFrame, CTkLabel, StringVar, CTkEntry, CTkFrame,\
      CTkTextbox, CTkImage, CTkOptionMenu
from PIL import Image

from .models.ProjectInfo import ExistingProjectProjectInfo
from .helpers.constants import RESOURCES_DIR, RESOURCES_DIR_DEV
from .frames.custom_widgets import StaticValueWithLabel, ConfirmDeleteDialog

from .data_profiler import DataProfiler

from apex_gui.apex_app import ApexApp
from apex_gui.frames.styled_widgets import Page, PageContainer, Section, Frame, SectionHeaderLabel, PositiveButton, NeutralButton, NegativeButton, IconButton
from apex_gui.frames.custom_widgets import EntryWithLabel
from apex_gui.styles.fonts import AppSubtitleFont, SectionHeaderFont, SectionSubheaderFont
from apex_gui.styles.colors import *
from apex_gui.helpers.constants import EntryType

class DataProfilerGUI(ApexApp):

    PROJECT_NUMBERS = ['TESTNATIVE', 'AAS24-010101', 'AAS23-016549']

    def __init__(self, dev: bool = False):
        """
        Constructs an instance of the DataProfiler app. Use dev=True if running locally in a python environment.
        """

        theme_path = f'{RESOURCES_DIR_DEV if dev else RESOURCES_DIR}/apex-theme.json'
        customtkinter.set_default_color_theme(theme_path)

        icon_path = f'{RESOURCES_DIR_DEV if dev else RESOURCES_DIR}/apex-a.ico'
        logo_url = f'{RESOURCES_DIR_DEV if dev else RESOURCES_DIR}/apex-a.png'
        logo = Image.open(logo_url)

        super().__init__(title='Data Profiler', icon_path=icon_path, logo=logo, dev=dev)

        self.dev = dev

        ''' Variables '''

        self.project_number_var = StringVar(self)
        self.DataProfiler: DataProfiler = None
        self.project_info: ExistingProjectProjectInfo = None

        ''' Create self '''

        # https://stackoverflow.com/questions/34276663/tkinter-gui-layout-using-frames-and-grid
        # self._create_self()
        self._create_start_frame()
        # self._create_home_frame()
        # # self._create_project_number_frame()
        # self._create_switches_frame()
        # self._create_glossary_frame()
        # self._create_loading_frame()

        ''' Grid self '''
        self._grid_start_frame()
        # self._grid_home_frame()

        ''' Toggle grids '''
        # Ungrid everything but start
        # self._toggle_frame_grid(frame=self.home_frame, grid=False)
        self._toggle_project_number_frame_grid(grid=False)

        self._toggle_frame_grid(frame=self.start_frame, grid=True)
        # self._toggle_frame_grid(frame=self.home_frame, grid=True)

        # if dev:
        #     self._dev_startup()


    ''' Create frames '''

    def _create_start_frame(self):
        self.start_frame = Page(self)

        self.start_frame_content_frame = Section(self.start_frame)

        self.start_frame_title = CTkLabel(self.start_frame_content_frame, text='Welcome to Data Profiler', font=SectionHeaderFont())

        self.select_project_number_label = CTkLabel(self.start_frame_content_frame, text='Select a project number', font=SectionSubheaderFont())
        self.select_project_number_dropdown = CTkOptionMenu(self.start_frame_content_frame, variable=self.project_number_var, values=self.PROJECT_NUMBERS)

        # Submit
        self.start_frame_submit = PositiveButton(self.start_frame_content_frame, text="Submit", command=self._start_frame_submit_action)

    def _create_home_frame(self): #, project_info: ExistingProjectProjectInfo):
        self.home_frame = Page(self)

        self.home_frame_header_frame = CTkFrame(self.home_frame, fg_color=APEX_LIGHT_GRAY, corner_radius=0)
        self.home_frame_title = CTkLabel(self.home_frame_header_frame, text='Data Profile Dashboard', font=AppSubtitleFont())
        
        self.home_frame_content_container = CTkScrollableFrame(self.home_frame, fg_color='transparent', corner_radius=0)
        
        self.home_frame_project_info_container = Frame(self.home_frame_content_container)
        self.home_frame_data_info_container = Frame(self.home_frame_content_container)

        self.home_frame_project_info_frame = Section(self.home_frame_project_info_container)
        self.home_frame_data_info_frame = Section(self.home_frame_data_info_container)

        self.home_frame_project_name = EntryWithLabel(self.home_frame_project_info_frame, label_text='Project Name', default_val=self.project_info.project_name, entry_type=EntryType.String)
        self.home_frame_company = EntryWithLabel(self.home_frame_project_info_frame, label_text='Company', default_val=self.project_info.company_name, entry_type=EntryType.String)
        self.home_frame_company_location = EntryWithLabel(self.home_frame_project_info_frame, label_text='Location', default_val=self.project_info.company_location, entry_type=EntryType.String)
        self.home_frame_salesperson = EntryWithLabel(self.home_frame_project_info_frame, label_text='Salesperson', default_val=self.project_info.salesperson, entry_type=EntryType.String)
        self.home_frame_email = EntryWithLabel(self.home_frame_project_info_frame, label_text='Email', default_val=self.project_info.email, entry_type=EntryType.String)
        self.home_frame_start_date = EntryWithLabel(self.home_frame_project_info_frame, label_text='Start Date', default_val=self.project_info.start_date, entry_type=EntryType.String)
        self.home_frame_notes = EntryWithLabel(self.home_frame_project_info_frame, label_text='Notes', default_val=self.project_info.notes, entry_type=EntryType.String)
        
        self.save_project_info_changes_button = PositiveButton(self.home_frame_project_info_frame, text='Save Changes', command=self.save_project_info_changes_action)

        date_for_analysis = self.project_info.transform_options.date_for_analysis.value if self.project_info.transform_options.date_for_analysis else ''
        weekend_date_rule = self.project_info.transform_options.weekend_date_rule.value if self.project_info.transform_options.weekend_date_rule else ''

        self.home_frame_data_uploaded = StaticValueWithLabel(self.home_frame_data_info_frame, label_text='Data Uploaded', value=str(self.project_info.data_uploaded))
        self.home_frame_upload_date = StaticValueWithLabel(self.home_frame_data_info_frame, label_text='Upload Date', value=str(self.project_info.upload_date))
        self.home_frame_date_for_analysis = StaticValueWithLabel(self.home_frame_data_info_frame, label_text='Date for Analysis', value=date_for_analysis)
        self.home_frame_weekend_date_rule = StaticValueWithLabel(self.home_frame_data_info_frame, label_text='Weekend Date Rule', value=weekend_date_rule)
        self.home_frame_item_master_file = StaticValueWithLabel(self.home_frame_data_info_frame, label_text='Item Master File', value=str(self.project_info.uploaded_file_paths.item_master))
        self.home_frame_inbound_header_file = StaticValueWithLabel(self.home_frame_data_info_frame, label_text='Inbound Header File', value=str(self.project_info.uploaded_file_paths.inbound_header))
        self.home_frame_inbound_details_file = StaticValueWithLabel(self.home_frame_data_info_frame, label_text='Inbound Details File', value=str(self.project_info.uploaded_file_paths.inbound_details))
        self.home_frame_inventory_file = StaticValueWithLabel(self.home_frame_data_info_frame, label_text='Inventory File', value=str(self.project_info.uploaded_file_paths.inventory))
        self.home_frame_order_header_file = StaticValueWithLabel(self.home_frame_data_info_frame, label_text='Order Header File', value=str(self.project_info.uploaded_file_paths.order_header))
        self.home_frame_order_details_file = StaticValueWithLabel(self.home_frame_data_info_frame, label_text='Order Details File', value=str(self.project_info.uploaded_file_paths.order_details))

        self.delete_project_data_button = NeutralButton(self.home_frame_data_info_frame, text='Delete Project Data', command=self.delete_project_data_action,
                                                        state='disabled' if not self.project_info.data_uploaded else 'normal')


        self._grid_home_frame()


    ''' Grid frames '''

    def _grid_start_frame(self):
        # Parent = self
        self.grid_page(self.start_frame)

        self.start_frame.grid_columnconfigure(0, weight=1)
        self.start_frame.grid_rowconfigure(0, weight=1)

        # Parent = start_frame
        self.start_frame_content_frame.grid(row=0, column=0)

        # Parent = start_frame_content_frame
        self.start_frame_title.grid(row=0, column=0, sticky='ew', padx=50, pady=(20,0))
        self.select_project_number_label.grid(row=1, column=0, sticky='ew', padx=50, pady=(50, 0))
        self.select_project_number_dropdown.grid(row=2, column=0, padx=50, sticky='ew', pady=(10, 50))
        self.start_frame_submit.grid(row=3, column=0, sticky='ew', padx=50, pady=20)


    def _grid_home_frame(self):
        # Parent = self
        self.grid_page(self.home_frame)

        self.home_frame.grid_columnconfigure(0, weight=1)
        self.home_frame.grid_rowconfigure(1, weight=1)

        # Parent = home_frame
        self.home_frame_header_frame.grid(row=0, column=0, sticky='ew')
        self.home_frame_content_container.grid(row=1, column=0, sticky='nsew')
        
        # Parent = home_frame_header_frame
        self.home_frame_header_frame.grid_columnconfigure(0, weight=1)

        self.home_frame_title.grid(row=0, column=0, sticky='ew', pady=5)

        # Parent = home_frame_container
        self.home_frame_content_container.grid_rowconfigure(0, weight=1)
        self.home_frame_content_container.grid_columnconfigure([0,1], weight=1)

        self.home_frame_project_info_container.grid(row=0, column=0, sticky='nsew')
        self.home_frame_data_info_container.grid(row=0, column=1, sticky='nsew')

        # Parent = home_frame_project_info_container
        self.home_frame_project_info_container.grid_rowconfigure(0, weight=1)
        self.home_frame_project_info_container.grid_columnconfigure(0, weight=1)

        self.home_frame_project_info_frame.grid(row=0, column=0)

        # Parent = home_frame_data_info_container
        self.home_frame_data_info_container.grid_rowconfigure(0, weight=1)
        self.home_frame_data_info_container.grid_columnconfigure(0, weight=1)

        self.home_frame_data_info_frame.grid(row=0, column=0)
        
        # Parent = home_frame_project_info_frame
        self.home_frame_project_info_frame.grid_columnconfigure(0, weight=1)

        self.home_frame_project_name.grid(row=0, column=0, sticky='ew', padx=50, pady=(20, 0))
        self.home_frame_company.grid(row=1, column=0, sticky='ew', padx=50, pady=(20, 0))
        self.home_frame_company_location.grid(row=2, column=0, sticky='ew', padx=50, pady=(20, 0))
        self.home_frame_salesperson.grid(row=3, column=0, sticky='ew', padx=50, pady=(20, 0))
        self.home_frame_email.grid(row=4, column=0, sticky='ew', padx=50, pady=(20, 0))
        self.home_frame_start_date.grid(row=5, column=0, sticky='ew', padx=50, pady=(20, 0))
        self.home_frame_notes.grid(row=6, column=0, sticky='ew', padx=50, pady=20)
        
        self.save_project_info_changes_button.grid(row=7, column=0, padx=50, pady=20)

        # Parent = home_frame_data_info_frame
        self.home_frame_data_info_frame.grid_columnconfigure(0, weight=1)
        
        self.home_frame_data_uploaded.grid(row=0, column=0, sticky='ew', padx=50, pady=(20, 0))
        self.home_frame_upload_date.grid(row=1, column=0, sticky='ew', padx=50, pady=(20, 0))
        self.home_frame_date_for_analysis.grid(row=2, column=0, sticky='ew', padx=50, pady=(20, 0))
        self.home_frame_weekend_date_rule.grid(row=3, column=0, sticky='ew', padx=50, pady=(20, 0))
        self.home_frame_item_master_file.grid(row=4, column=0, sticky='ew', padx=50, pady=(20, 0))
        self.home_frame_inbound_header_file.grid(row=5, column=0, sticky='ew', padx=50, pady=(20, 0))
        self.home_frame_inbound_details_file.grid(row=6, column=0, sticky='ew', padx=50, pady=(20, 0))
        self.home_frame_inventory_file.grid(row=7, column=0, sticky='ew', padx=50, pady=(20, 0))
        self.home_frame_order_header_file.grid(row=8, column=0, sticky='ew', padx=50, pady=(20, 0))
        self.home_frame_order_details_file.grid(row=9, column=0, sticky='ew', padx=50, pady=(20, 20))

        self.delete_project_data_button.grid(row=10, column=0, padx=50, pady=(20, 20))


    ''' Toggle grid '''

    def _toggle_frame_grid(self, frame: CTkFrame, grid: bool):
        if grid:
            # self._grid_start_frame()
            frame.grid()
            # self._toggle_project_number_frame_grid(grid=False)
        else:
            frame.grid_remove()

    # def _toggle_start_frame_grid(self, grid: bool):
    #     if grid:
    #         self._grid_start_frame()
    #         self._toggle_project_number_frame_grid(grid=False)
    #     else:
    #         self.start_frame.grid_remove()

    def _toggle_project_number_frame_grid(self, grid: bool):
        if grid:
            self.get_title_frame().set_project_number(self._get_project_number())
            self.get_title_frame().grid_project_number_frame()
        else:
            self.get_title_frame().ungrid_project_number_frame()


    ''' Button actions '''

    def _start_frame_submit_action(self):
        # Initialize a DataProfiler instance
        self._init_data_profiler()

        # Does the project number exist?
        if self.DataProfiler.get_project_exists():
            # Create home frame with project info
            self._create_home_frame()#project_info=self.DataProfiler.get_project_info())

            self._toggle_frame_grid(frame=self.start_frame, grid=False)
            self._toggle_frame_grid(frame=self.home_frame, grid=True)

            self._toggle_project_number_frame_grid(grid=True)

    def save_project_info_changes_action(self):
        current_project_info = self._get_project_info()

        new_project_info = ExistingProjectProjectInfo(
            project_number=self._get_project_number(),
            project_name=self.home_frame_project_name.get_variable_value(),
            company_name=self.home_frame_company.get_variable_value(),
            company_location=self.home_frame_company_location.get_variable_value(),
            salesperson=self.home_frame_salesperson.get_variable_value(),
            email=self.home_frame_email.get_variable_value(),
            start_date=self.home_frame_start_date.get_variable_value(),
            notes=self.home_frame_notes.get_variable_value(),
            data_uploaded=current_project_info.data_uploaded,
            upload_date=current_project_info.upload_date,
            transform_options=current_project_info.transform_options,
            uploaded_file_paths=current_project_info.uploaded_file_paths
        )

        if new_project_info == current_project_info:
            print('INFO IS THE SAME. DONT DO ANYTHING')
        
        else:
            print(f'--------------------- OLD ---------------------------')
            print(current_project_info.model_dump())
            print(f'--------------------- NEW ---------------------------')
            pprint(new_project_info.model_dump())
            print(f'SUBMITTING TO DB')
            self.DataProfiler.update_project_info(new_project_info=new_project_info)
            self._refresh_project_info()
            print(f'DONE')

    def delete_project_data_action(self):
        confirm_dialog = ConfirmDeleteDialog(self, title='Confirm Deletion', 
                                             text=f'Are you sure you would like to delete project data for {self._get_project_number()}?',
                                             positive_action=self.delete_project_data,
                                             negative_action=None)
        
        confirm_dialog.attributes('-topmost', True)
        confirm_dialog.mainloop()

        return
    
    def delete_project_data(self):
        if not self._get_project_info().data_uploaded:
            print(f'NOTHING TO DELETE')
        else:
            print(f'DELETING PROJECT DATA')
            self.DataProfiler.delete_project_data()
            self._refresh_project_info()
            print(f'DONE')

    ''' Critical functions '''

    def _init_data_profiler(self):
        self.DataProfiler = DataProfiler(project_number=self._get_project_number(), dev=self.dev)
        self._refresh_project_info()

    ''' Getters/Setters '''

    def _get_project_number(self):
        return self.project_number_var.get()
    
    def _set_project_number(self, pn: str):
        self.project_number_var.set(pn)  

    def _get_project_info(self) -> ExistingProjectProjectInfo:
        return self.project_info
    
    def _refresh_project_info(self):
        self.project_info = self.DataProfiler.get_project_info()
