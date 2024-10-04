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

from .models.ProjectInfo import BaseProjectInfo, ExistingProjectProjectInfo
from .models.TransformOptions import DateForAnalysis, WeekendDateRules, TransformOptions
from .helpers.constants import RESOURCES_DIR, RESOURCES_DIR_DEV
from .frames.custom_widgets import StaticValueWithLabel, ConfirmDeleteDialog, DropdownWithLabel

from .data_profiler import DataProfiler

from apex_gui.apex_app import ApexApp
from apex_gui.frames.notification_dialogs import NotificationDialog
from apex_gui.frames.styled_widgets import Page, PageContainer, Section, Frame, SectionHeaderLabel, PositiveButton, NeutralButton, NegativeButton, IconButton
from apex_gui.frames.custom_widgets import EntryWithLabel, FileBrowser, CheckbuttonWithLabel
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

        ''' Icons '''
        back_icon_path = f'{RESOURCES_DIR_DEV if self.dev else RESOURCES_DIR}/back-icon-win-10.png'
        self.back_icon = CTkImage(light_image=Image.open(back_icon_path), size=(26, 26))

        ''' Create self '''

        # https://stackoverflow.com/questions/34276663/tkinter-gui-layout-using-frames-and-grid
        # self._create_self()
        self._create_start_frame()
        self._create_new_project_frame()
        self._create_loading_frame()
        self._create_upload_data_frame()
        # self._create_home_frame()
        # # self._create_project_number_frame()
        # self._create_switches_frame()
        # self._create_glossary_frame()
        # self._create_loading_frame()

        ''' Grid self '''
        # self._grid_start_frame()
        # self._grid_loading_frame()
        # self._grid_home_frame()

        ''' Toggle grids '''
        # Ungrid everything but start
        self._toggle_frame_grid(frame=self.loading_frame, grid=False)
        self._toggle_frame_grid(frame=self.upload_frame, grid=False)
        self._toggle_frame_grid(frame=self.new_project_frame, grid=False)
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

        # Grid
        self._grid_start_frame()

    def _create_new_project_frame(self):
        self.new_project_frame = Page(self)

        self.new_project_frame_header_frame = CTkFrame(self.new_project_frame, fg_color=APEX_LIGHT_GRAY, corner_radius=0)
        self.new_project_frame_title = CTkLabel(self.new_project_frame_header_frame, text='Start New Project', font=AppSubtitleFont())
        self.new_project_frame_logout_btn = IconButton(self.new_project_frame_header_frame, image=self.back_icon, command=self.logout_action)

        self.new_project_frame_content_frame = Frame(self.new_project_frame)

        self.new_project_frame_project_info_frame = Section(self.new_project_frame_content_frame)
        
        # self.new_project_frame_project_number = StaticValueWithLabel(self.new_project_frame_project_info_frame, value=self._get_project_number(), label_text='Project Number')
        self.new_project_frame_project_name = EntryWithLabel(self.new_project_frame_project_info_frame, label_text='Project Name', default_val='', entry_type=EntryType.String)
        self.new_project_frame_company = EntryWithLabel(self.new_project_frame_project_info_frame, label_text='Company', default_val='', entry_type=EntryType.String)
        self.new_project_frame_company_location = EntryWithLabel(self.new_project_frame_project_info_frame, label_text='Location', default_val='', entry_type=EntryType.String)
        self.new_project_frame_salesperson = EntryWithLabel(self.new_project_frame_project_info_frame, label_text='Salesperson', default_val='', entry_type=EntryType.String)
        self.new_project_frame_email = EntryWithLabel(self.new_project_frame_project_info_frame, label_text='Email', default_val='', entry_type=EntryType.String)
        self.new_project_frame_start_date = EntryWithLabel(self.new_project_frame_project_info_frame, label_text='Start Date (yyyy-mm-dd)', default_val='', entry_type=EntryType.Date)
        self.new_project_frame_notes = EntryWithLabel(self.new_project_frame_project_info_frame, label_text='Notes', default_val='', entry_type=EntryType.String)
        
        self.new_project_frame_submit_project_info_btn = PositiveButton(self.new_project_frame_project_info_frame, text='Create Project', command=self.create_project_action)

        # Grid
        self._grid_new_project_frame()

    def _create_home_frame(self):
        self.home_frame = Page(self)

        self.home_frame_header_frame = CTkFrame(self.home_frame, fg_color=APEX_LIGHT_GRAY, corner_radius=0)
        self.home_frame_title = CTkLabel(self.home_frame_header_frame, text='Data Profile Dashboard', font=AppSubtitleFont())
        
        self.home_frame_logout_btn = IconButton(self.home_frame_header_frame, image=self.back_icon, command=self.logout_action)

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
        self.home_frame_start_date = EntryWithLabel(self.home_frame_project_info_frame, label_text='Start Date (yyyy-mm-dd)', default_val=self.project_info.start_date, entry_type=EntryType.String)
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

        self.delete_project_data_button = NeutralButton(self.home_frame_data_info_frame, text='Delete Project Data', command=self.delete_project_data_action)
        self.home_frame_upload_data_button = PositiveButton(self.home_frame_data_info_frame, text='Upload Data', command=self.show_upload_data_frame_action)

        # Grid
        self._grid_home_frame()


    def _create_upload_data_frame(self):
        self.upload_frame = Page(self)

        self.upload_frame_header_frame = CTkFrame(self.upload_frame, fg_color=APEX_LIGHT_GRAY, corner_radius=0)
        
        self.upload_frame_title = CTkLabel(self.upload_frame_header_frame, text='Upload Project Data', font=AppSubtitleFont())
        self.upload_frame_back_to_home_btn = IconButton(self.upload_frame_header_frame, image=self.back_icon, command=self.upload_frame_back_to_home_action)

        self.upload_frame_content_frame = Frame(self.upload_frame)

        self.upload_frame_upload_section = Section(self.upload_frame_content_frame)

        # self.upload_frame_title = CTkLabel(self.upload_frame_content_frame, text='Upload Project Data', font=SectionHeaderFont())

        self.upload_frame_data_directory_browse = FileBrowser(self.upload_frame_upload_section, label_text='Select a data directory', path_type='folder', label_font=SectionSubheaderFont())

        self.upload_frame_date_for_analysis = DropdownWithLabel(self.upload_frame_upload_section, label_text='Date for Analysis', default_val=DateForAnalysis.PICK_DATE.value,
                                                                dropdown_values=[DateForAnalysis.RECEIVED_DATE.value, DateForAnalysis.PICK_DATE.value, DateForAnalysis.SHIP_DATE.value])
        self.upload_frame_weekend_date_rule = DropdownWithLabel(self.upload_frame_upload_section, label_text='Weekend Date Rule', default_val=WeekendDateRules.AS_IS.value,
                                                                dropdown_values=[WeekendDateRules.NEAREST_WEEKDAY.value, WeekendDateRules.ALL_TO_FRIDAY.value, WeekendDateRules.ALL_TO_MONDAY.value, WeekendDateRules.AS_IS.value])

        self.upload_frame_process_inbound_data = CheckbuttonWithLabel(self.upload_frame_upload_section, label_text='Process Inbound Data', default_val=True)
        self.upload_frame_process_inventory_data = CheckbuttonWithLabel(self.upload_frame_upload_section, label_text='Process Inventory Data', default_val=True)
        self.upload_frame_process_outbound_data = CheckbuttonWithLabel(self.upload_frame_upload_section, label_text='Process Outbound Data', default_val=True)

        self.upload_frame_submit_btn = PositiveButton(self.upload_frame_upload_section, text='Submit', command=self.upload_data_action)

        # Grid
        self._grid_upload_frame()


    def _create_loading_frame(self):
        self.loading_frame = Page(self)

        self.loading_frame_content_frame = Section(self.loading_frame)

        self.loading_frame_text_var = StringVar(self.loading_frame_content_frame, 'Loading...')
        self.loading_frame_label = CTkLabel(self.loading_frame_content_frame, textvariable=self.loading_frame_text_var, wraplength=450)

        # Grid
        self._grid_loading_frame()


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

    def _grid_new_project_frame(self):
        # Parent = self
        self.grid_page(self.new_project_frame)

        self.new_project_frame.grid_columnconfigure(0, weight=1)
        self.new_project_frame.grid_rowconfigure(1, weight=1)

        # Parent = new_project_frame
        self.new_project_frame_header_frame.grid(row=0, column=0, sticky='ew')
        self.new_project_frame_content_frame.grid(row=1, column=0, sticky='nsew')
        
        # Parent = new_project_frame_header_frame
        self.new_project_frame_header_frame.grid_columnconfigure(0, weight=1)

        self.new_project_frame_title.grid(row=0, column=0, sticky='ew', pady=5)
        self.new_project_frame_logout_btn.grid(row=0, column=0, sticky='w', padx=(19,0), pady=5)

        # Parent = new_project_frame_content_frame
        self.new_project_frame_content_frame.grid_rowconfigure(0, weight=1)
        self.new_project_frame_content_frame.grid_columnconfigure(0, weight=1)

        self.new_project_frame_project_info_frame.grid(row=0, column=0)

        # Parent = home_frame_project_info_frame
        self.new_project_frame_project_info_frame.grid_columnconfigure(0, weight=1)

        # self.new_project_frame_project_number.grid(row=0, column=0, sticky='ew', padx=50, pady=(20, 0))
        self.new_project_frame_project_name.grid(row=1, column=0, sticky='ew', padx=50, pady=(20, 0))
        self.new_project_frame_company.grid(row=2, column=0, sticky='ew', padx=50, pady=(20, 0))
        self.new_project_frame_company_location.grid(row=3, column=0, sticky='ew', padx=50, pady=(20, 0))
        self.new_project_frame_salesperson.grid(row=4, column=0, sticky='ew', padx=50, pady=(20, 0))
        self.new_project_frame_email.grid(row=5, column=0, sticky='ew', padx=50, pady=(20, 0))
        self.new_project_frame_start_date.grid(row=6, column=0, sticky='ew', padx=50, pady=(20, 0))
        self.new_project_frame_notes.grid(row=7, column=0, sticky='ew', padx=50, pady=20)
        
        self.new_project_frame_submit_project_info_btn.grid(row=8, column=0, padx=50, pady=20)


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
        self.home_frame_logout_btn.grid(row=0, column=0, sticky='w', padx=(19,0), pady=5)

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

        if self.project_info.data_uploaded:
            self.delete_project_data_button.grid(row=10, column=0, padx=50, pady=(20, 20))
        else:
            self.home_frame_upload_data_button.grid(row=10, column=0, padx=50, pady=(20, 20))

    def _grid_upload_frame(self):
        # Parent = self
        self.grid_page(self.upload_frame)

        # Parent = upload_frame
        self.upload_frame.grid_columnconfigure(0, weight=1)
        self.upload_frame.grid_rowconfigure(1, weight=1)

        self.upload_frame_header_frame.grid(row=0, column=0, sticky='ew')
        self.upload_frame_content_frame.grid(row=1, column=0, sticky='nsew')
        
        # Parent = home_frame_header_frame
        self.upload_frame_header_frame.grid_columnconfigure(0, weight=1)

        self.upload_frame_title.grid(row=0, column=0, sticky='ew', pady=5)
        self.upload_frame_back_to_home_btn.grid(row=0, column=0, sticky='w', padx=(19,0), pady=5)
        
        # Parent = upload_frame_content_frame
        self.upload_frame_content_frame.grid_columnconfigure(0, weight=1)
        self.upload_frame_content_frame.grid_rowconfigure(0, weight=1)

        self.upload_frame_upload_section.grid(row=0, column=0)

        # Parent = upload_frame_upload_section
        self.upload_frame_data_directory_browse.grid(row=1, column=0, sticky='ew', padx=50, pady=(50, 0))
        self.upload_frame_date_for_analysis.grid(row=2, column=0, padx=50, sticky='ew', pady=(20, 0))
        self.upload_frame_weekend_date_rule.grid(row=3, column=0, sticky='ew', padx=50, pady=(20, 0))
        self.upload_frame_process_inbound_data.grid(row=4, column=0, sticky='ew', padx=50, pady=(20, 0))
        self.upload_frame_process_inventory_data.grid(row=5, column=0, sticky='ew', padx=50, pady=(20, 0))
        self.upload_frame_process_outbound_data.grid(row=6, column=0, sticky='ew', padx=50, pady=(20, 50))

        self.upload_frame_submit_btn.grid(row=7, column=0, sticky='ew', padx=50, pady=20)


    def _grid_loading_frame(self):
        # Parent = self
        # self.loading_frame.grid(row=1,column=0, sticky='nsew')
        self.grid_page(self.loading_frame)

        # Parent = loading_frame
        self.loading_frame.grid_columnconfigure(0, weight=1)
        self.loading_frame.grid_rowconfigure(0, weight=1)

        self.loading_frame_content_frame.grid(row=0, column=0)

        # Parent = loading_frame_content_frame
        self.loading_frame_content_frame.grid_columnconfigure(0, weight=1)
        self.loading_frame_content_frame.grid_rowconfigure(0, weight=1)

        self.loading_frame_label.grid(row=0, column=0, padx=50, pady=50)

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
        # Show loading frame while executing
        self._set_loading_frame_text('Loading...')
        self._toggle_frame_grid(frame=self.start_frame, grid=False)
        self._toggle_frame_grid(frame=self.loading_frame, grid=True)
        self.update()

        # Initialize a DataProfiler instance
        self._init_data_profiler()

        # Does the project number exist?
        if self.DataProfiler.get_project_exists():
            # Create home frame with project info
            self._create_home_frame() #project_info=self.DataProfiler.get_project_info())

            self._toggle_frame_grid(frame=self.loading_frame, grid=False)
            self._toggle_frame_grid(frame=self.home_frame, grid=True)

            self._toggle_project_number_frame_grid(grid=True)

        else:
            confirm_dialog = ConfirmDeleteDialog(self, title='Data Profiler', 
                                             text=f'A data project for "{self._get_project_number()}" does not yet exist. Would you like to start one?',
                                             positive_action=self.show_new_project_frame,
                                             negative_action=self.logout_action)
        
            confirm_dialog.attributes('-topmost', True)
            confirm_dialog.mainloop()

            # return
            # self._toggle_frame_grid(frame=self.loading_frame, grid=False)
            # self._toggle_frame_grid(frame=self.start_frame, grid=True)

        self.update()

    def show_new_project_frame(self):
        self._toggle_frame_grid(self.loading_frame, False)
        self._toggle_frame_grid(self.start_frame, False)
        self._toggle_frame_grid(self.new_project_frame, True)
        self._toggle_project_number_frame_grid(grid=True)

        self.update()


    def create_project_action(self):

        # Validate inputs
        if not self.new_project_frame_start_date.has_valid_input():
            # Display notification of results
            message = f'Invalid date format for Start Date:\n{self.new_project_frame_start_date.get_variable_value()}\n\nDate format should be "yyyy-mm-dd"'
            notification_dialog = NotificationDialog(self, title='Error', text=message)
            notification_dialog.attributes('-topmost', True)
            notification_dialog.mainloop()
            return
        
        # Show loading frame while executing
        self._set_loading_frame_text('Creating new project...')
        self._toggle_frame_grid(frame=self.new_project_frame, grid=False)
        self._toggle_frame_grid(frame=self.loading_frame, grid=True)
        self.update()

        # Create obj
        new_project_info = BaseProjectInfo(
            project_number=self._get_project_number(),
            project_name=self.new_project_frame_project_name.get_variable_value(),
            company_name=self.new_project_frame_company.get_variable_value(),
            company_location=self.new_project_frame_company_location.get_variable_value(),
            email=self.new_project_frame_email.get_variable_value(),
            salesperson=self.new_project_frame_salesperson.get_variable_value(),
            start_date=self.new_project_frame_start_date.get_variable_value(),
            notes=self.new_project_frame_notes.get_variable_value()
        )

        success = self.DataProfiler.create_new_project(project_info=new_project_info)

        if success:
            self._refresh_project_info()
            self._create_home_frame()

            # Clear new project form
            self.new_project_frame_project_name.clear_input(),
            self.new_project_frame_company.clear_input(),
            self.new_project_frame_company_location.clear_input(),
            self.new_project_frame_email.clear_input(),
            self.new_project_frame_salesperson.clear_input(),
            self.new_project_frame_start_date.clear_input(),
            self.new_project_frame_notes.clear_input()

            self._toggle_frame_grid(frame=self.loading_frame, grid=False)
            self._toggle_frame_grid(frame=self.home_frame, grid=True)
            self.update()

            # Display notification of results
            notification_dialog = NotificationDialog(self, title='Success!', text=f'Created new data project for {self._get_project_number()}')
            notification_dialog.attributes('-topmost', True)
            notification_dialog.mainloop()
        
        else:
            self._toggle_frame_grid(frame=self.loading_frame, grid=False)
            self._toggle_frame_grid(frame=self.new_project_frame, grid=True)
            self.update()

            # Display notification of results
            notification_dialog = NotificationDialog(self, title='Error', text=f'Something went wrong when creating new project for {self._get_project_number()}')
            notification_dialog.attributes('-topmost', True)
            notification_dialog.mainloop()


    def logout_action(self):
        # Destroy our data profiler instance
        self._destroy_data_profiler()

        # Grid only start frame
        if hasattr(self, 'home_frame'):
            self._toggle_frame_grid(frame=self.home_frame, grid=False)

        self._toggle_frame_grid(frame=self.upload_frame, grid=False)
        self._toggle_frame_grid(frame=self.new_project_frame, grid=False)
        self._toggle_frame_grid(frame=self.loading_frame, grid=False)

        self._toggle_project_number_frame_grid(grid=False)
        self._toggle_frame_grid(frame=self.start_frame, grid=True)
        self.update()

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
            confirm_dialog = ConfirmDeleteDialog(self, title='Confirm Save', 
                                                text=f'Are you sure you would like to save project info changes for {self._get_project_number()}?',
                                                positive_action=self.save_project_info_changes,
                                                negative_action=self.void)
            
            confirm_dialog.attributes('-topmost', True)
            confirm_dialog.mainloop()

        return
    
    def void(self):
        return

    def save_project_info_changes(self):
        # Show loading frame while executing
        self._set_loading_frame_text('Saving changes...')
        self._toggle_frame_grid(frame=self.home_frame, grid=False)
        self._toggle_frame_grid(frame=self.loading_frame, grid=True)
        self.update()

        # Create new project info object using inputs
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
        
        # Submit changes to DB
        print(f'--------------------- OLD ---------------------------')
        print(current_project_info.model_dump())
        print(f'--------------------- NEW ---------------------------')
        pprint(new_project_info.model_dump())
        print(f'SUBMITTING TO DB')
        self.DataProfiler.update_project_info(new_project_info=new_project_info)
        self._refresh_project_info()
        print(f'DONE')

        # Show self again
        self._toggle_frame_grid(frame=self.loading_frame, grid=False)
        self._toggle_frame_grid(frame=self.home_frame, grid=True)
        self.update()

        notification_dialog = NotificationDialog(self, title='Success!', text='Saved project info changes to database.')

        # Display notification of results
        notification_dialog.attributes('-topmost', True)
        notification_dialog.mainloop()


    def validate_data_directory(self):
        pass

    def upload_frame_back_to_home_action(self):
        # Show self again
        self._toggle_frame_grid(frame=self.upload_frame, grid=False)
        self._toggle_frame_grid(frame=self.home_frame, grid=True)
        self.update()

    def upload_data_action(self):
        data_dir = self.upload_frame_data_directory_browse.get_path()

        transform_options = TransformOptions(
            date_for_analysis=DateForAnalysis(self.upload_frame_date_for_analysis.get_variable_value()),
            weekend_date_rule=WeekendDateRules(self.upload_frame_weekend_date_rule.get_variable_value()),
            process_inbound_data=self.upload_frame_process_inbound_data.get_value(),
            process_inventory_data=self.upload_frame_process_inventory_data.get_value(),
            process_outbound_data=self.upload_frame_process_outbound_data.get_value(),
        )

        data_directory_validation = self.DataProfiler.validate_data_directory(data_directory=data_dir, transform_options=transform_options)
        if not data_directory_validation.is_valid:
            errors_str = '\n'.join(data_directory_validation.errors_list)
            # Display error
            notification_dialog = NotificationDialog(self, title='Error', text=f'Data directory is not valid:\n{errors_str}')
            notification_dialog.attributes('-topmost', True)
            notification_dialog.mainloop()

            print(f'DATA DIR NOT VALID')
            return
        
        # Show loading frame while executing
        self._set_loading_frame_text('Transforming and uploading data...')
        self._toggle_frame_grid(frame=self.upload_frame, grid=False)
        self._toggle_frame_grid(frame=self.loading_frame, grid=True)
        self.update()

        results = self.DataProfiler.transform_and_upload_data(data_directory=data_dir, transform_options=transform_options)

        self._toggle_frame_grid(frame=self.loading_frame, grid=False)
        if not results.success:
            self._toggle_frame_grid(frame=self.upload_frame, grid=True)

            # Display notification of results
            notification_dialog = NotificationDialog(self, title='Error', text=f'Trouble with the upload:\n{results.message}')
            notification_dialog.attributes('-topmost', True)
            notification_dialog.mainloop()

        else:
            self._refresh_project_info()
            self._create_home_frame()

            # Back to home
            self._toggle_frame_grid(frame=self.home_frame, grid=True)

            # Display notification of results
            notification_dialog = NotificationDialog(self, title='Success!', text=f'Successful transformation and data upload:\n{results.rows_inserted.model_dump()}')
            notification_dialog.attributes('-topmost', True)
            notification_dialog.mainloop()


    def show_upload_data_frame_action(self):
        self._toggle_frame_grid(self.home_frame, grid=False)
        self._toggle_frame_grid(self.upload_frame, grid=True)


    def delete_project_data_action(self):
        confirm_dialog = ConfirmDeleteDialog(self, title='Confirm Deletion', 
                                             text=f'Are you sure you would like to delete project data for {self._get_project_number()}?',
                                             positive_action=self.delete_project_data,
                                             negative_action=self.void)
        
        confirm_dialog.attributes('-topmost', True)
        confirm_dialog.mainloop()

        return
    
    def delete_project_data(self):
        # Show loading frame while executing
        self._set_loading_frame_text('Deleting project data...')
        self._toggle_frame_grid(frame=self.home_frame, grid=False)
        self._toggle_frame_grid(frame=self.loading_frame, grid=True)
        self.update()

        if not self._get_project_info().data_uploaded:
            print(f'NOTHING TO DELETE')
        else:
            print(f'DELETING PROJECT DATA')
            self.DataProfiler.delete_project_data()
            self._refresh_project_info()
            print(f'DONE')
        
        self._create_home_frame()

        # Show self again
        self._toggle_frame_grid(frame=self.loading_frame, grid=False)
        self._toggle_frame_grid(frame=self.home_frame, grid=True)
        self.update()

        notification_dialog = NotificationDialog(self, title='Success!', text='Deleted project data successfully.')

        # Display notification of results
        notification_dialog.attributes('-topmost', True)
        notification_dialog.mainloop()


    ''' Critical functions '''

    def _init_data_profiler(self):
        self.DataProfiler = DataProfiler(project_number=self._get_project_number(), dev=self.dev)
        self._refresh_project_info()

    def _destroy_data_profiler(self):
        self.DataProfiler = None
        self.project_info = None

    ''' Getters/Setters '''

    def _get_project_number(self):
        return self.project_number_var.get()
    
    def _set_project_number(self, pn: str):
        self.project_number_var.set(pn)  

    def _get_project_info(self) -> ExistingProjectProjectInfo:
        return self.project_info
    
    def _refresh_project_info(self):
        self.project_info = self.DataProfiler.get_project_info()

    def _set_loading_frame_text(self, text: str):
        self.loading_frame_text_var.set(text)