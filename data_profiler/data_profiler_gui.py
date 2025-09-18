'''
Jack Miller
Apex Companies
Oct 2024

GUI for data profiler app. Creates an instance of DataProfiler as backend logic and to interact with database
'''

# Python
from pprint import pprint
import customtkinter
from customtkinter import CTkLabel, StringVar, CTkFrame, CTkImage
from PIL import Image
import pandas as pd

# DataProfiler
from .helpers.models.ProjectInfo import BaseProjectInfo, ExistingProjectProjectInfo
from .helpers.models.TransformOptions import DateForAnalysis, WeekendDateRules, TransformOptions
from .helpers.models.Responses import TransformRowsInserted
from .helpers.models.GeneralModels import DownloadDataOptions
from .helpers.models.DataFiles import DataDirectoryType
from .helpers.constants.app_constants import RESOURCES_DIR, RESOURCES_DIR_DEV
from .frames.custom_widgets import ProjectInfoFrame, DataDescriberColumnSelector

from .services.output_tables_service import OutputTablesService
from .data_profiler import DataProfiler

# Apex GUI
from apex_gui.apex_app import ApexApp
from apex_gui.frames.notification_dialogs import NotificationDialog, ResultsDialog, ResultsDialogWithLogFile, ConfirmDeleteDialog
from apex_gui.frames.styled_widgets import Page, Section, SectionWithScrollbar, Frame, NeutralButton, TransparentIconButton, PositiveIconButton, NeutralIconButton, DangerIconButton
from apex_gui.frames.custom_widgets import Toggle, StaticValueWithLabel, DropdownWithLabel, CheckbuttonWithLabel, FileBrowser
from apex_gui.styles.fonts import AppSubtitleFont, SectionHeaderFont, SectionSubheaderFont
from apex_gui.styles.colors import *


class DataProfilerGUI(ApexApp):

    PROJECT_NUMBERS = []

    def __init__(self, dev: bool = False):
        """
        Constructs an instance of the DataProfiler app. Use dev=True if running locally in a python environment.
        """

        self.resources_dir = f'{RESOURCES_DIR_DEV if dev else RESOURCES_DIR}'

        theme_path = f'{self.resources_dir}/apex-theme.json'
        customtkinter.set_default_color_theme(theme_path)

        # Set variables for constructor
        icon_path = f'{self.resources_dir}/apex-a.ico'
        logo_url = f'{self.resources_dir}/apex-a.png'
        logo = Image.open(logo_url)
        title = '(DEV) Data Profiler' if dev else 'Data Profiler'

        # Create window
        super().__init__(title=title, icon_path=icon_path, logo=logo, dev=dev)
        self.geometry('1100x700')

        ''' Variables '''

        self.dev = dev
        self.project_number = None
        self.DataProfiler: DataProfiler = None
        self.project_info: ExistingProjectProjectInfo = None

        ''' Icons '''
        self.back_icon = CTkImage(light_image=Image.open(f'{self.resources_dir}/back-icon-win-10.png'), size=(26, 26))
        self.trash_icon = CTkImage(light_image=Image.open(f'{self.resources_dir}/trash-icon-win-10.png'), size=(26, 26))
        self.save_icon = CTkImage(light_image=Image.open(f'{self.resources_dir}/save-icon-win-10.png'), size=(26, 26))
        self.check_icon = CTkImage(light_image=Image.open(f'{self.resources_dir}/check-icon-win-10.png'), size=(26, 26))
        self.upload_icon = CTkImage(light_image=Image.open(f'{self.resources_dir}/upload-icon-win-10.png'), size=(26, 26))
        self.add_new_icon = CTkImage(light_image=Image.open(f'{self.resources_dir}/add-new-icon-win-10.png'), size=(26, 26))

        ''' Create self '''

        # https://stackoverflow.com/questions/34276663/tkinter-gui-layout-using-frames-and-grid
        self._create_start_frame()
        self._create_new_project_frame()
        self._create_loading_frame()
        self._create_upload_data_frame()
        self._create_more_actions_frame()

        ''' Startup '''

        # Use logout, because it ungrids every other frame, fetches project #s, and navigates to start
        self.logout_action()
        

    ''' Create frames '''

    def _create_start_frame(self):
        self.start_frame = Page(self)

        # TOPLEVEL - start_frame
        self.start_frame_container = Frame(self.start_frame)

        # LEVEL 1 - start_frame_container
        self.start_frame_title = CTkLabel(self.start_frame_container, text='Welcome to Data Profiler', font=SectionHeaderFont())
        self.start_frame_content_frame = Section(self.start_frame_container)

        # LEVEL 2 - start_frame_content_frame
        self.select_project_number_dropdown = DropdownWithLabel(self.start_frame_content_frame, 
                                                                label_text='Select a project number', 
                                                                label_font=SectionSubheaderFont(),
                                                                dropdown_values=self.PROJECT_NUMBERS,
                                                                default_val='')
        self.start_frame_submit = NeutralIconButton(self.start_frame_content_frame, image=self.check_icon, command=self._start_frame_submit_action)

        self.or_label = CTkLabel(self.start_frame_content_frame, text='OR', font=SectionHeaderFont())
        
        self.create_label = CTkLabel(self.start_frame_content_frame, text='Create new', font=SectionSubheaderFont())
        self.start_frame_new_project_btn = PositiveIconButton(self.start_frame_content_frame, image=self.add_new_icon, command=self.navigate_to_new_project_frame_action)

        # Grid
        self._grid_start_frame()

    def _create_new_project_frame(self):
        self.new_project_frame = Page(self)

        # TOPLEVEL - new_project_frame
        self.new_project_frame_header_frame = CTkFrame(self.new_project_frame, fg_color=APEX_LIGHT_GRAY, corner_radius=0)
        self.new_project_frame_content_frame = Frame(self.new_project_frame)

        # LEVEL 1 - new_project_frame_header_frame
        self.new_project_frame_title = CTkLabel(self.new_project_frame_header_frame, text='Start New Project', font=AppSubtitleFont())
        self.new_project_frame_logout_btn = TransparentIconButton(self.new_project_frame_header_frame, image=self.back_icon, command=self.logout_action)

        # LEVEL 1 - new_project_frame_content_frame
        self.new_project_frame_content_title = CTkLabel(self.new_project_frame_content_frame, text='Enter Project Info', font=SectionHeaderFont())
        self.new_project_frame_project_info_section = ProjectInfoFrame(self.new_project_frame_content_frame, show_project_number=True)
        self.new_project_frame_submit_btn = PositiveIconButton(self.new_project_frame_content_frame, image=self.check_icon, command=self.create_project_action)

        # Grid
        self._grid_new_project_frame()

    def _create_home_frame(self):
        self.home_frame = Page(self)

        # TOPLEVEL - Parent = home_frame
        self.home_frame_header_frame = CTkFrame(self.home_frame, fg_color=APEX_LIGHT_GRAY, corner_radius=0)
        self.home_frame_content_container = Frame(self.home_frame)
        
        # LEVEL 1 - Parent = home_frame_header_frame
        self.home_frame_title = CTkLabel(self.home_frame_header_frame, text='Data Profile Dashboard', font=AppSubtitleFont())        
        self.home_frame_logout_btn = TransparentIconButton(self.home_frame_header_frame, image=self.back_icon, command=self.logout_action)
        self.home_frame_task_bar_frame = Frame(self.home_frame_header_frame)

        # LEVEL 1 - Parent = home_frame_content_container
        self.home_frame_project_info_frame = Frame(self.home_frame_content_container)
        self.home_frame_data_info_frame = Frame(self.home_frame_content_container)

        # LEVEL 2 - Parent = home_frame_task_bar_frame
        self.home_frame_more_actions_btn = NeutralButton(self.home_frame_task_bar_frame, text='More Actions', command=self.navigate_to_more_actions_action)
        self.home_frame_delete_project_frame = TransparentIconButton(self.home_frame_task_bar_frame, image=self.trash_icon, command=self._delete_project_action)

        # LEVEL 2 - home_frame_project_info_frame
        self.home_frame_project_info_title = CTkLabel(self.home_frame_project_info_frame, text='Project Info', font=SectionHeaderFont())
        self.home_frame_project_info_section = ProjectInfoFrame(self.home_frame_project_info_frame)
        self.home_frame_save_changes_button = NeutralIconButton(self.home_frame_project_info_frame, image=self.save_icon, command=self._save_project_info_changes_action)

        # LEVEL 3 - home_frame_data_info_section
        # Within ProjectInfoFrame
        self.home_frame_project_info_section.set_project_info(self._get_project_info())

        # LEVEL 2 - Parent = home_frame_data_info_frame
        self.home_frame_data_info_title = CTkLabel(self.home_frame_data_info_frame, text='Project Data Info', font=SectionHeaderFont())
        self.home_frame_data_info_section = SectionWithScrollbar(self.home_frame_data_info_frame, width=350, height=250)
        self.delete_project_data_button = DangerIconButton(self.home_frame_data_info_frame, image=self.trash_icon, command=self._delete_project_data_action)
        self.home_frame_upload_data_button = PositiveIconButton(self.home_frame_data_info_frame, image=self.upload_icon, command=self.navigate_to_upload_data_frame_action)

        # LEVEL 3 - Parent = home_frame_data_info_section
        date_for_analysis = self.project_info.transform_options.date_for_analysis.value if self.project_info.transform_options.date_for_analysis else ''
        weekend_date_rule = self.project_info.transform_options.weekend_date_rule.value if self.project_info.transform_options.weekend_date_rule else ''

        self.home_frame_data_uploaded = StaticValueWithLabel(self.home_frame_data_info_section, label_text='Data Uploaded', value=str(self.project_info.data_uploaded))#, alignment='vertical')
        self.home_frame_upload_date = StaticValueWithLabel(self.home_frame_data_info_section, label_text='Upload Date', value=str(self.project_info.upload_date))#, alignment='vertical')
        self.home_frame_date_for_analysis = StaticValueWithLabel(self.home_frame_data_info_section, label_text='Date for Analysis', value=date_for_analysis)#, alignment='vertical')
        self.home_frame_weekend_date_rule = StaticValueWithLabel(self.home_frame_data_info_section, label_text='Weekend Date Rule', value=weekend_date_rule)#, alignment='vertical')
        self.home_frame_inbound_processed = StaticValueWithLabel(self.home_frame_data_info_section, label_text='Inbound Processed', value=self.project_info.transform_options.process_inbound_data)#, alignment='vertical')
        self.home_frame_inventory_processed = StaticValueWithLabel(self.home_frame_data_info_section, label_text='Inventory Processed', value=self.project_info.transform_options.process_inventory_data)#, alignment='vertical')
        self.home_frame_outbound_processed = StaticValueWithLabel(self.home_frame_data_info_section, label_text='Outbound Processed', value=self.project_info.transform_options.process_outbound_data)#, alignment='vertical')

        # Grid
        self._grid_home_frame()

    def _create_upload_data_frame(self):
        self.upload_frame = Page(self)

        # TOP LEVEL - upload_frame
        self.upload_frame_header_frame = CTkFrame(self.upload_frame, fg_color=APEX_LIGHT_GRAY, corner_radius=0)
        self.upload_frame_content_frame = Frame(self.upload_frame)

        # LEVEL 1 - upload_frame_header_frame
        self.upload_frame_title = CTkLabel(self.upload_frame_header_frame, text='Upload Project Data', font=AppSubtitleFont())
        self.upload_frame_back_to_home_btn = TransparentIconButton(self.upload_frame_header_frame, image=self.back_icon, command=self.navigate_to_home_action)

        # LEVEL 1 - upload_frame_content_frame
        self.upload_frame_upload_section = SectionWithScrollbar(self.upload_frame_content_frame, width=375, height=420)
        self.upload_frame_submit_btn = PositiveIconButton(self.upload_frame_content_frame, image=self.check_icon, command=self.upload_data_action)#, state='disabled')

        # LEVEL 2 - upload_frame_upload_section
        self.upload_frame_data_directory_browse = FileBrowser(self.upload_frame_upload_section, label_text='Select a data directory', path_type='folder')
        self.upload_frame_data_upload_type = Toggle(self.upload_frame_upload_section, on_value_text=DataDirectoryType.HEADERS.value, off_value_text=DataDirectoryType.REGULAR.value, default='off')

        self.upload_frame_process_inbound_data = CheckbuttonWithLabel(self.upload_frame_upload_section, label_text='Process Inbound Data', default_val=True)
        self.upload_frame_process_inventory_data = CheckbuttonWithLabel(self.upload_frame_upload_section, label_text='Process Inventory Data', default_val=True)
        self.upload_frame_process_outbound_data = CheckbuttonWithLabel(self.upload_frame_upload_section, label_text='Process Outbound Data', default_val=True)

        self.upload_frame_date_for_analysis = DropdownWithLabel(self.upload_frame_upload_section, label_text='Date for Analysis', default_val=DateForAnalysis.PICK_DATE.value,
                                                                dropdown_values=[DateForAnalysis.RECEIVED_DATE.value, DateForAnalysis.PICK_DATE.value, DateForAnalysis.SHIP_DATE.value],
                                                                dropdown_sticky='')
        self.upload_frame_weekend_date_rule = DropdownWithLabel(self.upload_frame_upload_section, label_text='Weekend Date Rule', default_val=WeekendDateRules.AS_IS.value,
                                                                dropdown_values=[WeekendDateRules.NEAREST_WEEKDAY.value, WeekendDateRules.ALL_TO_FRIDAY.value, WeekendDateRules.ALL_TO_MONDAY.value, WeekendDateRules.AS_IS.value],
                                                                dropdown_sticky='')
        
        # Grid
        self._grid_upload_frame()

    def _create_more_actions_frame(self):
        self.more_actions_frame = Page(self)

        # TOPLEVEL - Parent = more_actions_frame
        self.more_actions_frame_header_frame = CTkFrame(self.more_actions_frame, fg_color=APEX_LIGHT_GRAY, corner_radius=0)
        self.more_actions_frame_content_container = Frame(self.more_actions_frame)
        
        # LEVEL 1 - Parent = more_actions_frame_header_frame
        self.more_actions_frame_title = CTkLabel(self.more_actions_frame_header_frame, text='More Data Actions', font=AppSubtitleFont())        
        self.more_actions_frame_logout_btn = TransparentIconButton(self.more_actions_frame_header_frame, image=self.back_icon, command=self.navigate_to_home_action)
        self.more_actions_frame_task_bar_frame = Frame(self.more_actions_frame_header_frame)

        # LEVEL 1 - Parent = more_actions_frame_content_container
        self.more_actions_frame_update_item_master_section = Section(self.more_actions_frame_content_container)
        self.more_actions_frame_download_data_section = Section(self.more_actions_frame_content_container)
        self.more_actions_data_describer_section = Section(self.more_actions_frame_content_container)
        self.more_actions_subframe_4 = Frame(self.more_actions_frame_content_container)

        # LEVEL 2 - Parent = more_actions_frame_task_bar_frame
        self.more_actions_frame_home_btn = NeutralButton(self.more_actions_frame_task_bar_frame, text='Home', command=self.navigate_to_home_action)
        self.more_actions_frame_delete_project_frame = TransparentIconButton(self.more_actions_frame_task_bar_frame, image=self.trash_icon, command=self._delete_project_action)

        # LEVEL 2 - Parent = more_actions_frame_update_item_master_section
        self.more_actions_frame_update_item_master_title = CTkLabel(self.more_actions_frame_update_item_master_section, text='Update Item Master', font=SectionHeaderFont())
        self.more_actions_frame_update_item_master_browse = FileBrowser(self.more_actions_frame_update_item_master_section, label_text='Select a file', path_type='CSV')
        self.more_actions_frame_update_item_master_submit_btn = PositiveIconButton(self.more_actions_frame_update_item_master_section, image=self.check_icon, command=self.update_item_master)

        # LEVEL 2 - Parent = more_actions_frame_download_data_section
        self.more_actions_frame_download_data_title = CTkLabel(self.more_actions_frame_download_data_section, text='Download Data', font=SectionHeaderFont())
        self.more_actions_frame_download_data_options_dropdown = DropdownWithLabel(self.more_actions_frame_download_data_section, 
                                                                label_text='Select a download option',
                                                                dropdown_values=[option.value for option in DownloadDataOptions],
                                                                default_val='')
        self.more_actions_frame_download_data_folder_browse = FileBrowser(self.more_actions_frame_download_data_section, label_text='Select a download folder', path_type='folder')
        self.more_actions_frame_download_data_submit_btn = PositiveIconButton(self.more_actions_frame_download_data_section, image=self.check_icon, command=self._download_data_submit_action)

        # LEVEL 2 - Parent = more_actions_data_describer_section
        self.more_actions_data_describer_title = CTkLabel(self.more_actions_data_describer_section, text='Describe a dataset', font=SectionHeaderFont())
        self.more_actions_data_describer_browse = FileBrowser(self.more_actions_data_describer_section, label_text='Select a file', path_type='TABLE', btn_action=self._data_describer_set_sheet_names)
        self.more_actions_data_describer_sheet_name = DropdownWithLabel(self.more_actions_data_describer_section, label_text='Sheet Name', default_val=None, dropdown_values=[], dropdown_sticky='')
        self.more_actions_data_describer_submit_btn = PositiveIconButton(self.more_actions_data_describer_section, image=self.check_icon, command=self._data_describer_submit_action)

        # Grid
        self._grid_more_actions_frame()


    def _create_loading_frame(self):
        self.loading_frame = Page(self)

        # TOPLEVEL - loading_frame
        self.loading_frame_content_frame = Section(self.loading_frame)

        # LEVEL 1 - loading_frame_content_frame
        self.loading_frame_text_var = StringVar(self.loading_frame_content_frame, 'Loading...')
        self.loading_frame_label = CTkLabel(self.loading_frame_content_frame, textvariable=self.loading_frame_text_var, wraplength=450)

        # Grid
        self._grid_loading_frame()


    ''' Grid frames '''

    def _grid_start_frame(self):
        # Parent = self
        self.grid_page(self.start_frame)

        # TOPLEVEL - start_frame
        self.start_frame.grid_columnconfigure(0, weight=1)
        self.start_frame.grid_rowconfigure(0, weight=1)
        
        self.start_frame_container.grid(row=0, column=0)

        # LEVEL 1 - start_frame_container
        self.start_frame_container.grid_columnconfigure(0, weight=1)
        self.start_frame_container.grid_rowconfigure(1, weight=1)

        self.start_frame_title.grid(row=0, column=0, sticky='ew', pady=20)
        self.start_frame_content_frame.grid(row=1, column=0, sticky='nsew')
        
        # LEVEL 2 - start_frame_content_frame
        self.start_frame_content_frame.grid_columnconfigure(0, weight=1)

        self.select_project_number_dropdown.grid(row=0, column=0, padx=50, sticky='ew', pady=(20, 5))
        self.start_frame_submit.grid(row=1, column=0, sticky='ew', padx=50, pady=(5, 10))

        self.or_label.grid(row=2, column=0, sticky='ew', padx=50, pady=10)
        
        self.create_label.grid(row=3, column=0, sticky='ew', padx=50, pady=(10, 0))
        self.start_frame_new_project_btn.grid(row=4, column=0, sticky='ew', padx=50, pady=(0, 20))

    def _grid_new_project_frame(self):
        # Parent = self
        self.grid_page(self.new_project_frame)

        # TOPLEVEL - new_project_frame
        self.new_project_frame.grid_columnconfigure(0, weight=1)
        self.new_project_frame.grid_rowconfigure(1, weight=1)

        self.new_project_frame_header_frame.grid(row=0, column=0, sticky='ew')
        self.new_project_frame_content_frame.grid(row=1, column=0, sticky='nsew')
        
        # LEVEL 1 - new_project_frame_header_frame
        self.new_project_frame_header_frame.grid_columnconfigure(0, weight=1)
        self.new_project_frame_header_frame.grid_rowconfigure(0, weight=1)

        self.new_project_frame_title.grid(row=0, column=0, sticky='ew', pady=5)
        self.new_project_frame_logout_btn.grid(row=0, column=0, sticky='w', padx=(19,0), pady=5)

        # LEVEL 1 - new_project_frame_content_frame
        self.new_project_frame_content_frame.grid_columnconfigure(0, weight=1)
        self.new_project_frame_content_frame.grid_rowconfigure(1, weight=1)

        self.new_project_frame_content_title.grid(row=0, column=0, sticky='ew', padx=50, pady=(20, 0))
        self.new_project_frame_project_info_section.grid(row=1, column=0, sticky='ns', padx=5, pady=20)
        self.new_project_frame_submit_btn.grid(row=2, column=0, padx=50, pady=(0, 20))

    def _grid_home_frame(self):
        # Parent = self
        self.grid_page(self.home_frame)

        # TOPLEVEL - home_frame
        self.home_frame.grid_columnconfigure(0, weight=1)
        self.home_frame.grid_rowconfigure(1, weight=1)

        self.home_frame_header_frame.grid(row=0, column=0, sticky='ew')
        self.home_frame_content_container.grid(row=1, column=0, sticky='nsew')
        
        # LEVEL 1 - home_frame_header_frame
        self.home_frame_header_frame.grid_columnconfigure(0, weight=1)
        self.home_frame_header_frame.grid_rowconfigure(0, weight=1)

        self.home_frame_title.grid(row=0, column=0, sticky='ew', pady=5)
        self.home_frame_logout_btn.grid(row=0, column=0, sticky='w', padx=(19,0), pady=5)
        self.home_frame_task_bar_frame.grid(row=0, column=0, sticky='e', padx=(0,19), pady=5)
        
        # LEVEL 1 - home_frame_content_container
        self.home_frame_content_container.grid_rowconfigure(0, weight=1)
        self.home_frame_content_container.grid_columnconfigure([0,1], weight=1)

        self.home_frame_project_info_frame.grid(row=0, column=0, padx=(50, 25), sticky='nsew')      # LEVEL 2 and 3 within ProjectInfoFrame class
        self.home_frame_data_info_frame.grid(row=0, column=1, padx=(25, 50), sticky='nsew')

        # LEVEL 2 - home_frame_task_bar_frame
        self.home_frame_task_bar_frame.grid_rowconfigure(0, weight=1)

        self.home_frame_more_actions_btn.grid(row=0, column=0, sticky='ew', padx=(0,5))
        self.home_frame_delete_project_frame.grid(row=0, column=1, sticky='ew', padx=(5,0))

        # LEVEL 2 - home_frame_project_info_frame
        self.home_frame_project_info_frame.grid_columnconfigure(0, weight=1)
        self.home_frame_project_info_frame.grid_rowconfigure(1, weight=1)

        self.home_frame_project_info_title.grid(row=0, column=0, sticky='ew', padx=50, pady=(20, 0))
        self.home_frame_project_info_section.grid(row=1, column=0, sticky='ns', padx=5, pady=20)
        self.home_frame_save_changes_button.grid(row=2, column=0, padx=50, pady=(0, 20))

        # LEVEL 2 - home_frame_data_info_frame
        self.home_frame_data_info_frame.grid_columnconfigure(0, weight=1)
        self.home_frame_data_info_frame.grid_rowconfigure(1, weight=1)

        self.home_frame_data_info_title.grid(row=0, column=0, sticky='ew', padx=50, pady=(20, 0))
        self.home_frame_data_info_section.grid(row=1, column=0, sticky='ns', padx=5, pady=20)
        if self.project_info.data_uploaded:
            self.delete_project_data_button.grid(row=2, column=0, padx=50, pady=(0, 20))
        else:
            self.home_frame_upload_data_button.grid(row=2, column=0, padx=50, pady=(0, 20))

        # LEVEL 3 - home_frame_project_info_section
        # Within ProjectInfoFrame

        # LEVEL 3 - home_frame_data_info_section
        self.home_frame_data_info_section.grid_columnconfigure(0, weight=1)
        
        self.home_frame_data_uploaded.grid(row=0, column=0, sticky='ew', padx=20, pady=(5, 0))
        if self._get_project_info().data_uploaded:
            self.home_frame_upload_date.grid(row=1, column=0, sticky='ew', padx=20, pady=(20, 0))
            self.home_frame_date_for_analysis.grid(row=2, column=0, sticky='ew', padx=20, pady=(20, 0))
            self.home_frame_weekend_date_rule.grid(row=3, column=0, sticky='ew', padx=20, pady=(20, 0))
            self.home_frame_inbound_processed.grid(row=4, column=0, sticky='ew', padx=20, pady=(20, 0))
            self.home_frame_inventory_processed.grid(row=5, column=0, sticky='ew', padx=20, pady=(20, 0))
            self.home_frame_outbound_processed.grid(row=6, column=0, sticky='ew', padx=20, pady=(20, 5))

    def _grid_upload_frame(self):
        # Parent = self
        self.grid_page(self.upload_frame)

        # TOP LEVEL - upload_frame
        self.upload_frame.grid_columnconfigure(0, weight=1)
        self.upload_frame.grid_rowconfigure(1, weight=1)

        self.upload_frame_header_frame.grid(row=0, column=0, sticky='ew')
        self.upload_frame_content_frame.grid(row=1, column=0, sticky='nsew')
        
        # LEVEL 1 - upload_frame_header_frame
        self.upload_frame_header_frame.grid_columnconfigure(0, weight=1)

        self.upload_frame_title.grid(row=0, column=0, sticky='ew', pady=5)
        self.upload_frame_back_to_home_btn.grid(row=0, column=0, sticky='w', padx=(19,0), pady=5)
        
        # LEVEL 1 - upload_frame_content_frame
        self.upload_frame_content_frame.grid_columnconfigure(0, weight=1)
        self.upload_frame_content_frame.grid_rowconfigure(1, weight=1)

        self.upload_frame_upload_section.grid(row=1, column=0, sticky='ns', padx=5, pady=20)
        self.upload_frame_submit_btn.grid(row=2, column=0, padx=50, pady=(0, 20))#, sticky='ew', padx=20, pady=(20, 5))

        # LEVEL 2 - upload_frame_upload_section
        self.upload_frame_upload_section.grid_columnconfigure(0, weight=1)

        self.upload_frame_data_directory_browse.grid(row=0, column=0, sticky='ew', padx=20, pady=(5, 10))
        
        self.upload_frame_data_upload_type.grid(row=1, column=0, padx=20, pady=(20, 0))
        self.upload_frame_process_inbound_data.grid(row=2, column=0, sticky='ew', padx=20, pady=(5, 0))
        self.upload_frame_process_inventory_data.grid(row=3, column=0, sticky='ew', padx=20, pady=(5, 0))
        self.upload_frame_process_outbound_data.grid(row=4, column=0, sticky='ew', padx=20, pady=(5, 10))   

        self.upload_frame_date_for_analysis.grid(row=5, column=0, sticky='ew', padx=20, pady=(10, 0))
        self.upload_frame_weekend_date_rule.grid(row=6, column=0, sticky='ew', padx=20, pady=(10, 5))

             

    def _grid_more_actions_frame(self):
        # Parent = self
        self.grid_page(self.more_actions_frame)

        # TOPLEVEL - more_actions_frame
        self.more_actions_frame.grid_columnconfigure(0, weight=1)
        self.more_actions_frame.grid_rowconfigure(1, weight=1)

        self.more_actions_frame_header_frame.grid(row=0, column=0, sticky='ew')
        self.more_actions_frame_content_container.grid(row=1, column=0, sticky='nsew')
        
        # LEVEL 1 - more_actions_frame_header_frame
        self.more_actions_frame_header_frame.grid_columnconfigure(0, weight=1)
        self.more_actions_frame_header_frame.grid_rowconfigure(0, weight=1)

        self.more_actions_frame_title.grid(row=0, column=0, sticky='ew', pady=5)
        self.more_actions_frame_logout_btn.grid(row=0, column=0, sticky='w', padx=(19,0), pady=5)
        self.more_actions_frame_task_bar_frame.grid(row=0, column=0, sticky='e', padx=(0,19), pady=5)
        
        # LEVEL 1 - more_actions_frame_content_container
        self.more_actions_frame_content_container.grid_rowconfigure([0,1], weight=1)
        self.more_actions_frame_content_container.grid_columnconfigure([0,1], weight=1)

        self.more_actions_frame_update_item_master_section.grid(row=0, column=0, sticky='nsew', padx=20, pady=20)      # LEVEL 2 and 3 within ProjectInfoFrame class
        self.more_actions_frame_download_data_section.grid(row=0, column=1, sticky='nsew', padx=20, pady=20)
        self.more_actions_data_describer_section.grid(row=1, column=0, sticky='nsew', padx=20, pady=(0,20))
        self.more_actions_subframe_4.grid(row=1, column=1, sticky='nsew')

        # LEVEL 2 - more_actions_frame_task_bar_frame
        self.more_actions_frame_task_bar_frame.grid_rowconfigure(0, weight=1)

        self.more_actions_frame_home_btn.grid(row=0, column=0, sticky='ew', padx=(0,5))
        self.more_actions_frame_delete_project_frame.grid(row=0, column=1, sticky='ew', padx=(5,0))

        # LEVEL 2 - more_actions_frame_update_subwhse_frame
        self.more_actions_frame_update_item_master_section.grid_rowconfigure(1, weight=1)
        self.more_actions_frame_update_item_master_section.grid_columnconfigure(0, weight=1)

        self.more_actions_frame_update_item_master_title.grid(row=0, column=0, sticky='ew', padx=10, pady=(10, 0))
        self.more_actions_frame_update_item_master_browse.grid(row=1, column=0, sticky='ew', padx=10, pady=20)
        self.more_actions_frame_update_item_master_submit_btn.grid(row=2, column=0, padx=10, pady=(0, 20))

         # LEVEL 2 - more_actions_frame_download_data_section
        self.more_actions_frame_download_data_section.grid_rowconfigure([1,2], weight=1)
        self.more_actions_frame_download_data_section.grid_columnconfigure(0, weight=1)

        self.more_actions_frame_download_data_title.grid(row=0, column=0, sticky='ew', padx=10, pady=(10, 0))
        self.more_actions_frame_download_data_options_dropdown.grid(row=1, column=0, padx=10, pady=(20, 0))
        self.more_actions_frame_download_data_folder_browse.grid(row=2, column=0, sticky='ew', padx=10, pady=(0,20))
        self.more_actions_frame_download_data_submit_btn.grid(row=3, column=0, padx=10, pady=(0, 20))

        # LEVEL 2 - more_actions_data_describer_section
        self.more_actions_data_describer_section.grid_rowconfigure(1, weight=1)
        self.more_actions_data_describer_section.grid_columnconfigure(0, weight=1)

        self.more_actions_data_describer_title.grid(row=0, column=0, sticky='ew', padx=10, pady=(10, 0))
        self.more_actions_data_describer_browse.grid(row=1, column=0, sticky='ew', padx=10, pady=(15, 0))
        self.more_actions_data_describer_sheet_name.grid(row=2, column=0, padx=10, pady=(0, 20))
        self.more_actions_data_describer_submit_btn.grid(row=3, column=0, padx=10, pady=(0, 20))

    def _grid_loading_frame(self):
        # Parent = self
        self.grid_page(self.loading_frame)

        # TOPLEVEL - loading_frame
        self.loading_frame.grid_columnconfigure(0, weight=1)
        self.loading_frame.grid_rowconfigure(0, weight=1)

        self.loading_frame_content_frame.grid(row=0, column=0)

        # LEVEL 1 - loading_frame_content_frame
        self.loading_frame_content_frame.grid_columnconfigure(0, weight=1)
        self.loading_frame_content_frame.grid_rowconfigure(0, weight=1)

        self.loading_frame_label.grid(row=0, column=0, padx=50, pady=50)


    ''' Toggle grid '''

    def _toggle_frame_grid(self, frame: CTkFrame, grid: bool):
        if grid:
            frame.grid()
        else:
            frame.grid_remove()

    def _toggle_project_number_frame_grid(self, grid: bool):
        if grid:
            self.get_title_frame().set_project_number(self._get_project_number())
            self.get_title_frame().grid_project_number_frame()
        else:
            self.get_title_frame().ungrid_project_number_frame()  
        self.update()


    ''' Main CRUD functions '''
    
    ## Create ##

    def create_project_action(self):

        # Validate inputs
        new_project_info_errors = self.new_project_frame_project_info_section.validate_inputs()
        if len(new_project_info_errors) > 0:
            message = '\n\n'.join(new_project_info_errors)

            notification_dialog = NotificationDialog(self, title='Error', text=message)
            notification_dialog.attributes('-topmost', True)
            notification_dialog.mainloop()
            return
        
        # Get inputs
        new_project_info = self.new_project_frame_project_info_section.get_project_info_inputs()

        # Validate project number doesn't exist
        if new_project_info.project_number in self.PROJECT_NUMBERS:
            message = 'Project already exists!'

            notification_dialog = NotificationDialog(self, title='Error', text=message)
            notification_dialog.attributes('-topmost', True)
            notification_dialog.mainloop()
            return

        # Show loading frame while executing
        self.show_loading_frame_action('Creating new project...')

        # Get inputs
        self._set_project_number(new_project_info.project_number)

        # Initialize a DataProfiler instance
        self._init_data_profiler()

        # Create project
        response = self.DataProfiler.create_new_project(project_info=new_project_info)

        notification_dialog = None
        if response.success:
            # Create home page with project info
            self._refresh_project_numbers()
            self._refresh_project_info()
            self._create_home_frame()

            # Clear new project form
            self.new_project_frame_project_info_section.clear_frame()

            # Navigate to home
            self.navigate_to_home_action()

            # Display notification of results
            notification_dialog = NotificationDialog(self, title='Success!', text=f'Created new data project for {self._get_project_number()}')
        
        else:
            # Navigate back to new project screen
            self.navigate_to_new_project_frame_action()

            # Display notification of results
            message = f'Something went wrong when creating new project for {self._get_project_number()}:\n\n{response.error_message}'
            notification_dialog = NotificationDialog(self, title='Error', text=message)

        notification_dialog.attributes('-topmost', True)
        notification_dialog.mainloop()
        return
    
    def upload_data_action(self):
        data_dir = self.upload_frame_data_directory_browse.get_path()
        
        # Transform options don't need validation (cuz they're dropdowns and checkboxes)       
        transform_options = TransformOptions(
            date_for_analysis=DateForAnalysis(self.upload_frame_date_for_analysis.get_variable_value()),
            weekend_date_rule=WeekendDateRules(self.upload_frame_weekend_date_rule.get_variable_value()),
            data_directory_type=DataDirectoryType(self.upload_frame_data_upload_type.get_value()),
            process_inbound_data=self.upload_frame_process_inbound_data.get_value(),
            process_inventory_data=self.upload_frame_process_inventory_data.get_value(),
            process_outbound_data=self.upload_frame_process_outbound_data.get_value(),
        )

        # Show loading frame while executing
        self.show_loading_frame_action('Transforming and uploading data...')

        # Transform and upload
        results = self.DataProfiler.transform_and_upload_data(data_directory=data_dir, transform_options=transform_options, update_progress_text_func=self._update_progess_text)

        # Navigate appropriately based on success
        message = ''
        if not results.success:
            # Navigate back to upload frame
            self.navigate_to_upload_data_frame_action()

            # Display notification of results
            message = results.message 
        else:
            # Reset upload page
            self._create_upload_data_frame()
            
            # Navigate to home
            self._refresh_project_info()
            self._create_home_frame()
            self.navigate_to_home_action()

            # Display notification of results
            message = f'Successful transformation and data upload!\n\n{self.pretty_print_rows_inserted(results.rows_inserted)}'
            
        # Report results
        notification_dialog = ResultsDialogWithLogFile(self, 
                                                       success=results.success, 
                                                       text=message, 
                                                       log_file_path=results.log_file_path)         
        notification_dialog.attributes('-topmost', True)
        notification_dialog.mainloop()
        return
    
    ## Read ##

    def _refresh_project_info(self):
        self.project_info = self.DataProfiler.get_project_info()

    def _refresh_project_numbers(self) -> list[str]:
        project_numbers = []

        with OutputTablesService(dev=self.dev) as service:
            project_numbers = service.get_output_tables_project_numbers()

        self.PROJECT_NUMBERS = project_numbers

        if hasattr(self, 'select_project_number_dropdown'):
            self.select_project_number_dropdown.set_dropdown_values(values=self.PROJECT_NUMBERS)

    ## Update ##

    def save_project_info_changes(self):
        # Show loading frame while executing
        self.show_loading_frame_action('Saving changes...')

        # Create new project info object using inputs
        current_project_info: ExistingProjectProjectInfo = self._get_project_info()
        home_frame_project_info_inputs: BaseProjectInfo = self.home_frame_project_info_section.get_project_info_inputs()

        # Create ExistingProjectProjectInfo using new inputs and current data info
        new_project_info = ExistingProjectProjectInfo(
            project_number=home_frame_project_info_inputs.project_number,
            project_name=home_frame_project_info_inputs.project_name,
            company_name=home_frame_project_info_inputs.company_name,
            company_location=home_frame_project_info_inputs.company_location,
            salesperson=home_frame_project_info_inputs.salesperson,
            email=home_frame_project_info_inputs.email,
            start_date=home_frame_project_info_inputs.start_date,
            notes=home_frame_project_info_inputs.notes,
            data_uploaded=current_project_info.data_uploaded,
            upload_date=current_project_info.upload_date,
            transform_options=current_project_info.transform_options,
            uploaded_file_paths=current_project_info.uploaded_file_paths
        )
        
        # Submit changes to DB
        response = self.DataProfiler.update_project_info(new_project_info=new_project_info)

        notification_dialog = None
        if response.success:
            # Update home page
            self._refresh_project_info()
            self._create_home_frame()

            # Notify of success
            notification_dialog = NotificationDialog(self, title='Success!', text='Saved project info changes to database.')
        else:
            # Notify of failure
            notification_dialog = NotificationDialog(self, title='Error', text=f'Could not save project info changes to database:\n\n{response.error_message}')

        # Navigate back to home
        self.navigate_to_home_action()

        # Display notification of results
        notification_dialog.attributes('-topmost', True)
        notification_dialog.mainloop()
        return

    def update_item_master(self):
        # Make sure project has data exists
        notification_dialog = None
        if not self._get_project_info().data_uploaded:
            message = f'Project has no data! Please upload data before updating item master'

            notification_dialog = NotificationDialog(self, title='Data Profiler', text=message)
            notification_dialog.attributes('-topmost', True)
            notification_dialog.mainloop()
            return
        
        # Get selected file path
        file_path = self.more_actions_frame_update_item_master_browse.get_path()

        if not file_path:
            notification_dialog = NotificationDialog(self, title='Error', text='Update Item Master:\n\nPlease select a valid CSV file.')
            notification_dialog.attributes('-topmost', True)
            notification_dialog.mainloop()
            return

        # Show loading frame while executing
        self.show_loading_frame_action('Loading...')

        # Delete project
        response = self.DataProfiler.update_item_master(file_path=file_path, update_progress_text_func=self._update_progess_text)

        # Back to more actions
        self.navigate_to_more_actions_action()

        # Clear browse, if operation was successful
        if response.success:
            self.more_actions_frame_update_item_master_browse.clear_input()
        
        # Notify of results
        title = 'Success!' if response.success else 'Error'
        notification_dialog = NotificationDialog(self, title=title, text=f'Update Item Master:\n\n{response.message}')
        notification_dialog.attributes('-topmost', True)
        notification_dialog.mainloop()

        return
    
    
    ## Delete ##

    def delete_project(self):
        # Show loading frame while executing
        self.show_loading_frame_action('Deleting project...')

        # Delete project
        response = self.DataProfiler.delete_project()

        if response.success:
            # Navigate back to start
            self.logout_action()
    
            # Display notification of results
            notification_dialog = NotificationDialog(self, title='Success!', text='Deleted project successfully.')        
        
        else:
            # Navigate back to home
            self.navigate_to_home_action()

            # Display notification of results
            notification_dialog = NotificationDialog(self, title='Error', text=f'Trouble deleting project:\n\n{response.error_message}')        
        
        notification_dialog.attributes('-topmost', True)
        notification_dialog.mainloop()
        return
    
    def delete_project_data(self):
        if not self._get_project_info().data_uploaded:
            print(f'NOTHING TO DELETE')
            return

        # Show loading frame while executing
        self.show_loading_frame_action('Deleting project data...')

        results = self.DataProfiler.delete_project_data(update_progress_text_func=self._update_progess_text)

        message = ''
        if results.success:
            self._refresh_project_info()
            self._create_home_frame()

            message = 'Deleted project data successfully.'
        else:
            message = f'Encountered {len(results.errors_encountered)} errors when attempting to delete project data. Check log.'

        # Show self again
        self.navigate_to_home_action()

        # Display notification of results
        notification_dialog = ResultsDialogWithLogFile(self, 
                                                       success=results.success, 
                                                       text=message, 
                                                       log_file_path=results.log_file_path)
        notification_dialog.attributes('-topmost', True)
        notification_dialog.mainloop()
        return
    

    ''' Other button actions '''

    def _start_frame_submit_action(self):
        if not self.select_project_number_dropdown.get_variable_value():
            return
        else:
            self._set_project_number(self.select_project_number_dropdown.get_variable_value())
        
        # Show loading frame while executing
        self.show_loading_frame_action('Loading...')

        # Initialize a DataProfiler instance
        self._init_data_profiler()

        # Does the project number exist?
        # NOTE - as of 10-10-24, it should always exist, as it pulls project #s for dropdown from DB
        if self.DataProfiler.get_project_exists():
            # Create home frame
            self._create_home_frame()

            # Navigate to home
            self.navigate_to_home_action()

            print(self._get_project_info())
        else:
            confirm_dialog = ConfirmDeleteDialog(self, title='Data Profiler', 
                                             text=f'A data project for "{self._get_project_number()}" does not yet exist. Would you like to start one?',
                                             positive_action=self.navigate_to_new_project_frame_action,
                                             negative_action=self.logout_action)
        
            confirm_dialog.attributes('-topmost', True)
            confirm_dialog.mainloop()

        self.update()

    def _save_project_info_changes_action(self):
        # Validate inputs
        project_info_errors = self.home_frame_project_info_section.validate_inputs()
        if len(project_info_errors) > 0:
            message = '\n\n'.join(project_info_errors)

            notification_dialog = NotificationDialog(self, title='Error', text=message)
            notification_dialog.attributes('-topmost', True)
            notification_dialog.mainloop()
            return
            
        # Create objects
        current_project_info = BaseProjectInfo(**self._get_project_info().model_dump())
        home_frame_project_info_inputs = self.home_frame_project_info_section.get_project_info_inputs()

        print(f'--------------------- OLD ---------------------------')
        pprint(current_project_info.model_dump())
        print(f'--------------------- NEW ---------------------------')
        pprint(home_frame_project_info_inputs.model_dump())

        if home_frame_project_info_inputs != current_project_info:     
            confirm_dialog = ConfirmDeleteDialog(self, title='Confirm Save', 
                                                text=f'Are you sure you would like to save project info changes for "{self._get_project_number()}"?',
                                                positive_action=self.save_project_info_changes,
                                                negative_action=self.void)
            
            confirm_dialog.attributes('-topmost', True)
            confirm_dialog.mainloop()
        else:
             print('INFO IS THE SAME. DONT DO ANYTHING')

        return

    def _delete_project_action(self):
        notification_dialog = None
        if self._get_project_info().data_uploaded:
            message = f'Please delete project data before deleting project.'
            notification_dialog = NotificationDialog(self, title='Data Profiler', text=message)
        else:
            message = f'Are you sure you would like to delete project "{self._get_project_number()}"?'
            notification_dialog = ConfirmDeleteDialog(self, 
                                                      title='Confirm Deletion', 
                                                        text=message,
                                                        positive_action=self.delete_project,
                                                        negative_action=self.void)
            
        notification_dialog.attributes('-topmost', True)
        notification_dialog.mainloop()
        return

    def _delete_project_data_action(self):
        confirm_dialog = ConfirmDeleteDialog(self, 
                                             title='Confirm Deletion', 
                                             text=f'Are you sure you would like to delete project data for "{self._get_project_number()}"?',
                                             positive_action=self.delete_project_data,
                                             negative_action=self.void)
        
        confirm_dialog.attributes('-topmost', True)
        confirm_dialog.mainloop()
        return
    
    def _download_data_submit_action(self):
        download_path = self.more_actions_frame_download_data_folder_browse.get_path()
        download_option_input = self.more_actions_frame_download_data_options_dropdown.get_variable_value()

        # Make sure project has data exists
        message = None

        if not self._get_project_info().data_uploaded:
            message = f'Project has no data! Please upload data before attempting to downloading data or reports.'
        elif not download_option_input:
            message = f'Please select a download option from the dropdown.'
        elif not download_path:
            message = f'Please select a download folder.'
        
        # If it's not a valid request, notify and quit
        if message:
            notification_dialog = NotificationDialog(self, title='Data Profiler', text=message)
            notification_dialog.attributes('-topmost', True)
            notification_dialog.mainloop()
            return

        # Show loading frame while executing
        self.show_loading_frame_action(f'Downloading "{download_option_input}"...')

        # Make the request to DataProfiler
        download_option = DownloadDataOptions(download_option_input)
        download_response = self.DataProfiler.download_data(download_option=download_option, target_directory=download_path)

        # Notify of results
        notification_dialog = None
        if download_response.success:
            # Display notification of results
            notification_dialog = ResultsDialog(self, title='Success!', text=f'Downloaded "{download_option.value}" for {self._get_project_number()}.', results_dir=download_response.download_path)        
        else:
            # Display notification of results
            notification_dialog = NotificationDialog(self, title='Error', text=f'Trouble downloading "{download_option.value}" :\n\n{download_response.message}') 

        # Navigate back to more actions
        self.navigate_to_more_actions_action()

        # Display dialog
        notification_dialog.attributes('-topmost', True)
        notification_dialog.mainloop()

    def _data_describer_set_sheet_names(self):
        file_path = self.more_actions_data_describer_browse.get_path()
        file_suffix = file_path.split('.')[-1]

        if file_suffix == 'xlsx':
            # Populate dropdown with sheet names from that book
            sheets: list[str] = []
            with pd.ExcelFile(file_path) as file:
                sheets = file.sheet_names
            self.more_actions_data_describer_sheet_name.set_variable_value(val=sheets[0])
            self.more_actions_data_describer_sheet_name.set_dropdown_values(values=sheets)
        else:
            # Set to nothin
            self.more_actions_data_describer_sheet_name.set_variable_value(val=None)
            self.more_actions_data_describer_sheet_name.set_dropdown_values(values=[])

    def _data_describer_submit_action(self):
        # Variables
        file = self.more_actions_data_describer_browse.get_path()
        sheet_name = self.more_actions_data_describer_sheet_name.get_variable_value()

        # Open file and get columns
        file_suffix = file.split('.')[-1]
        if not file:
            return
        
        given_cols: list[str] = []
        try:
            if file_suffix == 'csv':
                df = pd.read_csv(file, nrows=1)
                given_cols = df.columns.tolist()
            else:
                if not sheet_name:
                    raise ValueError(f'XLSX file uploaded, but no sheet name given!')
                df = pd.read_excel(file, sheet_name=sheet_name, nrows=1)
                given_cols = df.columns.tolist()

        except Exception as e:
            # Display dialog
            notification_dialog = NotificationDialog(self, title='Data Profiler', text=f'Data Describer ERROR:\n{e}')
            notification_dialog.attributes('-topmost', True)
            notification_dialog.mainloop()
            return
        
        # Have user select the columns to include
        column_selector = DataDescriberColumnSelector(self, columns=given_cols)
        column_selector.attributes('-topmost', True)
        self.wait_window(column_selector)

        # Run description, if user saved inputs
        if column_selector.get_saved():
            # Validate inputs
            success, message = column_selector.validate_inputs()
            if not success:
                # Display dialog
                notification_dialog = NotificationDialog(self, title='Data Profiler', text=f'Data Describer ERROR:\n{message}')
                notification_dialog.attributes('-topmost', True)
                notification_dialog.mainloop()
                return

            # Show loading frame while executing
            self.show_loading_frame_action(f'Describing data...')
            
            # Get user inputted values
            grouping_col = column_selector.get_grouping_col()
            selected_columns = column_selector.get_selected_columns()

            # Call data_describer
            output_dir = self.DataProfiler.describe_data_frame(file_path=file, columns=selected_columns, file_type=file_suffix, sheet_name=sheet_name, group_col=grouping_col)

            # Navigate back to more actions
            self.navigate_to_more_actions_action()

            notification_dialog = ResultsDialog(self, title='Success!', text=f'Described data.', results_dir=output_dir)
            notification_dialog.attributes('-topmost', True)
            notification_dialog.mainloop()
        

    ## Navigations ##

    def logout_action(self):
        '''
        This is basically an app reset. It ungrids every page, updates the set of project numbers, and navigates back to the start frame.
        '''
        
        # Destroy our data profiler instance
        self._destroy_data_profiler()

        # Clear project number
        self._set_project_number('')
        self.select_project_number_dropdown.set_variable_value('')       

        # Ungrid everything
        if hasattr(self, 'home_frame'):
            self._toggle_frame_grid(frame=self.home_frame, grid=False)
        self._toggle_frame_grid(frame=self.upload_frame, grid=False)
        self._toggle_frame_grid(frame=self.more_actions_frame, grid=False)
        self._toggle_frame_grid(frame=self.new_project_frame, grid=False)
        self._toggle_frame_grid(frame=self.loading_frame, grid=False)
        self._toggle_project_number_frame_grid(grid=False)
        self._toggle_frame_grid(frame=self.start_frame, grid=False)

        # Show loading screen while fetching project numbers
        self._set_loading_frame_text('Fetching projects...')
        self._toggle_frame_grid(frame=self.loading_frame, grid=True)
        self.update()

        self._refresh_project_numbers()

        # Once projects are loaded, nav to start
        self._toggle_frame_grid(frame=self.loading_frame, grid=False)
        self._toggle_frame_grid(frame=self.start_frame, grid=True)
        self.update()

    def show_loading_frame_action(self, text: str):
        self._set_loading_frame_text(text)
        self._navigate(self.loading_frame)

    def navigate_to_new_project_frame_action(self):
        self._navigate(self.new_project_frame)

    def navigate_to_upload_data_frame_action(self):
        self._navigate(self.upload_frame)
        self._toggle_project_number_frame_grid(grid=True)

    def navigate_to_home_action(self):
        self._navigate(to_frame=self.home_frame)
        self._toggle_project_number_frame_grid(grid=True)

    def navigate_to_more_actions_action(self):
        self._navigate(to_frame=self.more_actions_frame)
        self._toggle_project_number_frame_grid(grid=True)


    ''' Other critical/logic functions '''

    def _init_data_profiler(self):
        self.DataProfiler = DataProfiler(project_number=self._get_project_number(), dev=self.dev)
        self._refresh_project_info()

    def _destroy_data_profiler(self):
        self.DataProfiler = None
        self.project_info = None

    def _navigate(self, to_frame: CTkFrame):
        
        # Ungrid everything
        self._toggle_frame_grid(frame=self.start_frame, grid=False)
        self._toggle_frame_grid(frame=self.new_project_frame, grid=False)
        self._toggle_frame_grid(frame=self.upload_frame, grid=False)
        self._toggle_frame_grid(frame=self.more_actions_frame, grid=False)
        self._toggle_project_number_frame_grid(grid=False)
        self._toggle_frame_grid(frame=self.loading_frame, grid=False)

        # Home frame isn't created right away, so check it if exists before ungridding
        if hasattr(self, 'home_frame'):
            self._toggle_frame_grid(frame=self.home_frame, grid=False)

        # Grid the to frame
        self._toggle_frame_grid(frame=to_frame, grid=True)
        self.update()


    ''' Helpers '''

    def void(self):
        return
    
    def pretty_print_rows_inserted(self, rows: TransformRowsInserted):
        return_str = ''

        return_str += f'Total rows inserted: {rows.total_rows_inserted}\n'
        return_str += f'SKUs: {rows.skus}\n'
        return_str += f'Inbound Receipts: {rows.inbound_pos}\n'
        return_str += f'Inbound Lines: {rows.inbound_lines}\n'
        return_str += f'Inventory Lines: {rows.inventory_lines}\n'
        return_str += f'Outbound Orders: {rows.outbound_orders}\n'
        return_str += f'Outbound Lines: {rows.outbound_lines}'

        return return_str


    ''' Getters/Setters '''

    def _get_project_number(self):
        return self.project_number

    def _set_project_number(self, val: str):
        self.project_number = val

    def _get_project_info(self) -> ExistingProjectProjectInfo:
        return self.project_info

    def _set_loading_frame_text(self, text: str):
        self.loading_frame_text_var.set(text)

    def _update_progess_text(self, text: str):
        self._set_loading_frame_text(text)
        self.update()