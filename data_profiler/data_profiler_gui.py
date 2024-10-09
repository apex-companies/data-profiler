'''
Jack Miller
Apex Companies
Oct 2024

GUI for data profiler app. Creates an instance of DataProfiler as backend logic and to interact with database
'''

# Python
from pprint import pprint
import customtkinter
from customtkinter import CTkLabel, StringVar, CTkFrame,CTkImage
from PIL import Image

# DataProfiler
from .models.ProjectInfo import ExistingProjectProjectInfo
from .models.TransformOptions import DateForAnalysis, WeekendDateRules, TransformOptions
from .models.Responses import TransformRowsInserted
from .helpers.constants import RESOURCES_DIR, RESOURCES_DIR_DEV
from .frames.custom_widgets import ProjectInfoFrame
from .data_profiler import DataProfiler

# Apex GUI
from apex_gui.apex_app import ApexApp
from apex_gui.frames.notification_dialogs import NotificationDialog, ResultsDialogWithLogFile, ConfirmDeleteDialog
from apex_gui.frames.styled_widgets import Page, Section, SectionWithScrollbar, Frame, TransparentIconButton, PositiveIconButton, NeutralIconButton, DangerIconButton
from apex_gui.frames.custom_widgets import StaticValueWithLabel, DropdownWithLabel, CheckbuttonWithLabel, FileBrowser
from apex_gui.styles.fonts import AppSubtitleFont, SectionHeaderFont, SectionSubheaderFont
from apex_gui.styles.colors import *


class DataProfilerGUI(ApexApp):

    PROJECT_NUMBERS = ['TESTNATIVE', 'AAS24-010101', 'AAS23-016549']

    def __init__(self, dev: bool = False):
        """
        Constructs an instance of the DataProfiler app. Use dev=True if running locally in a python environment.
        """

        self.resources_dir = f'{RESOURCES_DIR_DEV if dev else RESOURCES_DIR}'

        theme_path = f'{self.resources_dir}/apex-theme.json'
        customtkinter.set_default_color_theme(theme_path)

        icon_path = f'{self.resources_dir}/apex-a.ico'
        logo_url = f'{self.resources_dir}/apex-a.png'
        logo = Image.open(logo_url)

        super().__init__(title='Data Profiler', icon_path=icon_path, logo=logo, dev=dev)

        self.geometry('1100x700')

        self.dev = dev

        ''' Variables '''

        # self.project_number_var = StringVar(self)
        self.DataProfiler: DataProfiler = None
        self.project_info: ExistingProjectProjectInfo = None

        ''' Icons '''
        self.back_icon = CTkImage(light_image=Image.open(f'{self.resources_dir}/back-icon-win-10.png'), size=(26, 26))
        self.trash_icon = CTkImage(light_image=Image.open(f'{self.resources_dir}/trash-icon-win-10.png'), size=(26, 26))
        self.save_icon = CTkImage(light_image=Image.open(f'{self.resources_dir}/save-icon-win-10.png'), size=(26, 26))
        self.check_icon = CTkImage(light_image=Image.open(f'{self.resources_dir}/check-icon-win-10.png'), size=(26, 26))
        self.upload_icon = CTkImage(light_image=Image.open(f'{self.resources_dir}/upload-icon-win-10.png'), size=(26, 26))

        ''' Create self '''

        # https://stackoverflow.com/questions/34276663/tkinter-gui-layout-using-frames-and-grid
        # self._create_self()
        self._create_start_frame()
        self._create_new_project_frame()
        self._create_loading_frame()
        self._create_upload_data_frame()

        ''' Toggle grids '''
        # Ungrid everything but start
        self._toggle_frame_grid(frame=self.loading_frame, grid=False)
        self._toggle_frame_grid(frame=self.upload_frame, grid=False)
        self._toggle_frame_grid(frame=self.new_project_frame, grid=False)
        self._toggle_project_number_frame_grid(grid=False)

        self._toggle_frame_grid(frame=self.start_frame, grid=True)

        # if dev:
        #     self._dev_startup()


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
        self.start_frame_submit = PositiveIconButton(self.start_frame_content_frame, image=self.check_icon, command=self._start_frame_submit_action)

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
        self.new_project_frame_project_info_section = ProjectInfoFrame(self.new_project_frame_content_frame)
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
        self.home_frame_delete_project_frame = TransparentIconButton(self.home_frame_header_frame, image=self.trash_icon, command=self.delete_project_action)

        # LEVEL 1 - Parent = home_frame_content_container
        self.home_frame_project_info_frame = Frame(self.home_frame_content_container)
        self.home_frame_data_info_frame = Frame(self.home_frame_content_container)

        # LEVEL 2 - home_frame_project_info_frame
        self.home_frame_project_info_title = CTkLabel(self.home_frame_project_info_frame, text='Project Info', font=SectionHeaderFont())
        self.home_frame_project_info_section = ProjectInfoFrame(self.home_frame_project_info_frame)
        self.home_frame_save_changes_button = NeutralIconButton(self.home_frame_project_info_frame, image=self.save_icon, command=self.save_project_info_changes_action)

        # LEVEL 3 - home_frame_data_info_section
        # Within ProjectInfoFrame
        self.home_frame_project_info_section.set_project_info(self._get_project_info())

        # LEVEL 2 - Parent = home_frame_data_info_frame
        self.home_frame_data_info_title = CTkLabel(self.home_frame_data_info_frame, text='Project Data Info', font=SectionHeaderFont())
        self.home_frame_data_info_section = SectionWithScrollbar(self.home_frame_data_info_frame, width=350, height=250)
        self.delete_project_data_button = DangerIconButton(self.home_frame_data_info_frame, image=self.trash_icon, command=self.delete_project_data_action)
        self.home_frame_upload_data_button = PositiveIconButton(self.home_frame_data_info_frame, image=self.upload_icon, command=self.show_upload_data_frame_action)

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
        # self.home_frame_item_master_file = StaticValueWithLabel(self.home_frame_data_info_frame, label_text='Item Master File', value=str(self.project_info.uploaded_file_paths.item_master)[len(self.project_info.uploaded_file_paths.item_master) - 30:])#, alignment='vertical')
        # self.home_frame_inbound_header_file = StaticValueWithLabel(self.home_frame_data_info_frame, label_text='Inbound Header File', value=str(self.project_info.uploaded_file_paths.inbound_header)[len(self.project_info.uploaded_file_paths.inbound_header) - 30:])#, alignment='vertical')
        # self.home_frame_inbound_details_file = StaticValueWithLabel(self.home_frame_data_info_frame, label_text='Inbound Details File', value=str(self.project_info.uploaded_file_paths.inbound_details)[len(self.project_info.uploaded_file_paths.inbound_details) - 30:])#, alignment='vertical')
        # self.home_frame_inventory_file = StaticValueWithLabel(self.home_frame_data_info_frame, label_text='Inventory File', value=str(self.project_info.uploaded_file_paths.inventory)[len(self.project_info.uploaded_file_paths.inventory) - 30:])#, alignment='vertical')
        # self.home_frame_order_header_file = StaticValueWithLabel(self.home_frame_data_info_frame, label_text='Order Header File', value=str(self.project_info.uploaded_file_paths.order_header)[len(self.project_info.uploaded_file_paths.order_header) - 30:])#, alignment='vertical')
        # self.home_frame_order_details_file = StaticValueWithLabel(self.home_frame_data_info_frame, label_text='Order Details File', value=str(self.project_info.uploaded_file_paths.order_details)[len(self.project_info.uploaded_file_paths.order_details) - 30:])#, alignment='vertical')


        # Grid
        self._grid_home_frame()


    def _create_upload_data_frame(self):
        self.upload_frame = Page(self)

        # TOP LEVEL - upload_frame
        self.upload_frame_header_frame = CTkFrame(self.upload_frame, fg_color=APEX_LIGHT_GRAY, corner_radius=0)
        self.upload_frame_content_frame = Frame(self.upload_frame)

        # LEVEL 1 - upload_frame_header_frame
        self.upload_frame_title = CTkLabel(self.upload_frame_header_frame, text='Upload Project Data', font=AppSubtitleFont())
        self.upload_frame_back_to_home_btn = TransparentIconButton(self.upload_frame_header_frame, image=self.back_icon, command=self.upload_frame_back_to_home_action)

        # LEVEL 2 - upload_frame_content_frame
        self.upload_frame_upload_section = SectionWithScrollbar(self.upload_frame_content_frame, width=375, height=420)
        self.upload_frame_submit_btn = PositiveIconButton(self.upload_frame_content_frame, image=self.check_icon, command=self.upload_data_action)#, state='disabled')

        # LEVEL 3 - upload_frame_upload_section
        self.upload_frame_data_directory_browse = FileBrowser(self.upload_frame_upload_section, label_text='Select a data directory', path_type='folder')#, btn_action=self.validate_data_directory)

        self.upload_frame_date_for_analysis = DropdownWithLabel(self.upload_frame_upload_section, label_text='Date for Analysis', default_val=DateForAnalysis.PICK_DATE.value,
                                                                dropdown_values=[DateForAnalysis.RECEIVED_DATE.value, DateForAnalysis.PICK_DATE.value, DateForAnalysis.SHIP_DATE.value],
                                                                dropdown_sticky='')
        self.upload_frame_weekend_date_rule = DropdownWithLabel(self.upload_frame_upload_section, label_text='Weekend Date Rule', default_val=WeekendDateRules.AS_IS.value,
                                                                dropdown_values=[WeekendDateRules.NEAREST_WEEKDAY.value, WeekendDateRules.ALL_TO_FRIDAY.value, WeekendDateRules.ALL_TO_MONDAY.value, WeekendDateRules.AS_IS.value],
                                                                dropdown_sticky='')

        self.upload_frame_process_inbound_data = CheckbuttonWithLabel(self.upload_frame_upload_section, label_text='Process Inbound Data', default_val=True)
        self.upload_frame_process_inventory_data = CheckbuttonWithLabel(self.upload_frame_upload_section, label_text='Process Inventory Data', default_val=True)
        self.upload_frame_process_outbound_data = CheckbuttonWithLabel(self.upload_frame_upload_section, label_text='Process Outbound Data', default_val=True)

        # Grid
        self._grid_upload_frame()


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

        self.select_project_number_dropdown.grid(row=0, column=0, padx=50, sticky='ew', pady=(20, 25))
        self.start_frame_submit.grid(row=1, column=0, sticky='ew', padx=50, pady=(25, 20))

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
        self.home_frame_delete_project_frame.grid(row=0, column=0, sticky='e', padx=(0,19), pady=5)

        # LEVEL 1 - home_frame_content_container
        self.home_frame_content_container.grid_rowconfigure(0, weight=1)
        self.home_frame_content_container.grid_columnconfigure([0,1], weight=1)

        self.home_frame_project_info_frame.grid(row=0, column=0, padx=(50, 25), sticky='nsew')      # LEVEL 2 and 3 within ProjectInfoFrame class
        self.home_frame_data_info_frame.grid(row=0, column=1, padx=(25, 50), sticky='nsew')

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
        # self.home_frame_item_master_file.grid(row=4, column=0, sticky='ew', padx=50, pady=(20, 0))
        # self.home_frame_inbound_header_file.grid(row=5, column=0, sticky='ew', padx=50, pady=(20, 0))
        # self.home_frame_inbound_details_file.grid(row=6, column=0, sticky='ew', padx=50, pady=(20, 0))
        # self.home_frame_inventory_file.grid(row=7, column=0, sticky='ew', padx=50, pady=(20, 0))
        # self.home_frame_order_header_file.grid(row=8, column=0, sticky='ew', padx=50, pady=(20, 0))
        # self.home_frame_order_details_file.grid(row=9, column=0, sticky='ew', padx=50, pady=(20, 20))


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

        self.upload_frame_data_directory_browse.grid(row=0, column=0, sticky='ew', padx=20, pady=(5, 20))

        self.upload_frame_date_for_analysis.grid(row=1, column=0, sticky='ew', padx=20, pady=(20, 0))
        self.upload_frame_weekend_date_rule.grid(row=2, column=0, sticky='ew', padx=20, pady=(20, 20))

        self.upload_frame_process_inbound_data.grid(row=3, column=0, sticky='ew', padx=20, pady=(20, 0))
        self.upload_frame_process_inventory_data.grid(row=4, column=0, sticky='ew', padx=20, pady=(20, 0))
        self.upload_frame_process_outbound_data.grid(row=5, column=0, sticky='ew', padx=20, pady=(20, 5))        


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


    ''' Button actions '''

    def _start_frame_submit_action(self):
        if not self._get_project_number():
            return
        
        # Show loading frame while executing
        self._set_loading_frame_text('Loading...')
        self._toggle_frame_grid(frame=self.start_frame, grid=False)
        self._toggle_frame_grid(frame=self.loading_frame, grid=True)
        self.update()

        # Initialize a DataProfiler instance
        self._init_data_profiler()

        # Does the project number exist?
        if self.DataProfiler.get_project_exists():
            # Create home frame
            self._create_home_frame()

            # Navigate to hom
            self._toggle_frame_grid(frame=self.loading_frame, grid=False)
            self._toggle_frame_grid(frame=self.home_frame, grid=True)
            self._toggle_project_number_frame_grid(grid=True)

            print(self._get_project_info())
        else:
            confirm_dialog = ConfirmDeleteDialog(self, title='Data Profiler', 
                                             text=f'A data project for "{self._get_project_number()}" does not yet exist. Would you like to start one?',
                                             positive_action=self.show_new_project_frame,
                                             negative_action=self.logout_action)
        
            confirm_dialog.attributes('-topmost', True)
            confirm_dialog.mainloop()

        self.update()

    def show_new_project_frame(self):
        self._toggle_frame_grid(self.loading_frame, False)
        self._toggle_frame_grid(self.start_frame, False)
        self._toggle_frame_grid(self.new_project_frame, True)
        self._toggle_project_number_frame_grid(grid=True)

        self.update()

    def create_project_action(self):

        # Validate inputs
        # if not self.new_project_frame_start_date.has_valid_input():
        # if not self.new_project_frame_project_info_frame.has_valid_inputs():
        if not self.new_project_frame_project_info_section.has_valid_inputs():
            # Display notification of results
            message = f'Invalid date format for Start Date:\n{self.new_project_frame_project_info_section.start_date.get_variable_value()}\n\nDate format should be "yyyy-mm-dd"'

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
        # new_project_info = BaseProjectInfo(
        #     project_number=self._get_project_number(),
        #     project_name=self.new_project_frame_project_name.get_variable_value(),
        #     company_name=self.new_project_frame_company.get_variable_value(),
        #     company_location=self.new_project_frame_company_location.get_variable_value(),
        #     email=self.new_project_frame_email.get_variable_value(),
        #     salesperson=self.new_project_frame_salesperson.get_variable_value(),
        #     start_date=self.new_project_frame_start_date.get_variable_value(),
        #     notes=self.new_project_frame_notes.get_variable_value()
        # )
        new_project_info = self.new_project_frame_project_info_section.get_project_info_inputs(self._get_project_number())

        # rows_inserted = self.DataProfiler.create_new_project(project_info=new_project_info)
        response = self.DataProfiler.create_new_project(project_info=new_project_info)

        notification_dialog = None
        # if rows_inserted == 1:
        if response.success:
            # Create home page with project info
            self._refresh_project_info()
            self._create_home_frame()

            # Clear new project form
            # self.new_project_frame_project_name.clear_input(),
            # self.new_project_frame_company.clear_input(),
            # self.new_project_frame_company_location.clear_input(),
            # self.new_project_frame_email.clear_input(),
            # self.new_project_frame_salesperson.clear_input(),
            # self.new_project_frame_start_date.clear_input(),
            # self.new_project_frame_notes.clear_input()
            self.new_project_frame_project_info_section.clear_frame()

            self._toggle_frame_grid(frame=self.loading_frame, grid=False)
            self._toggle_frame_grid(frame=self.home_frame, grid=True)
            self.update()

            # Display notification of results
            notification_dialog = NotificationDialog(self, title='Success!', text=f'Created new data project for {self._get_project_number()}')
        
        else:
            self._toggle_frame_grid(frame=self.loading_frame, grid=False)
            self._toggle_frame_grid(frame=self.new_project_frame, grid=True)
            self.update()

            # Display notification of results
            message = f'Something went wrong when creating new project for {self._get_project_number()}:\n\n{response.error_message}'
            notification_dialog = NotificationDialog(self, title='Error', text=message)

        notification_dialog.attributes('-topmost', True)
        notification_dialog.mainloop()
        return

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
        # Validate inputs
        # if not self.home_frame_start_date.has_valid_input():
        # if not self.home_frame_project_info_frame.has_valid_inputs():
        if not self.home_frame_project_info_section.has_valid_inputs():
            # Display notification of results
            # message = f'Invalid date given for Start Date ({self.home_frame_start_date.get_variable_value()})\n\nDate format should be "yyyy-mm-dd"'
            message = f'Invalid date given for Start Date ({self.home_frame_project_info_section.start_date.get_variable_value()})\n\nDate format should be "yyyy-mm-dd"'

            notification_dialog = NotificationDialog(self, title='Error', text=message)
            notification_dialog.attributes('-topmost', True)
            notification_dialog.mainloop()
            return
            
        # Create objects
        current_project_info = self._get_project_info()

        new_project_info_inputs = self.home_frame_project_info_section.get_project_info_inputs(self._get_project_number())

        new_project_info = ExistingProjectProjectInfo(
            project_number=self._get_project_number(),
            project_name=new_project_info_inputs.project_name,
            company_name=new_project_info_inputs.company_name,
            company_location=new_project_info_inputs.company_location,
            salesperson=new_project_info_inputs.salesperson,
            email=new_project_info_inputs.email,
            start_date=new_project_info_inputs.start_date,
            # notes=self.home_frame_notes.get_variable_value(),
            # notes=self.home_frame_notes.get(0.0, 'end-1c'),
            notes=new_project_info_inputs.notes,
            data_uploaded=current_project_info.data_uploaded,
            upload_date=current_project_info.upload_date,
            transform_options=current_project_info.transform_options,
            uploaded_file_paths=current_project_info.uploaded_file_paths
        )

        print(f'--------------------- OLD ---------------------------')
        pprint(current_project_info.model_dump())
        print(f'--------------------- NEW ---------------------------')
        pprint(new_project_info.model_dump())

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

        # new_project_info = ExistingProjectProjectInfo(
        #     project_number=self._get_project_number(),
        #     project_name=self.home_frame_project_name.get_variable_value(),
        #     company_name=self.home_frame_company.get_variable_value(),
        #     company_location=self.home_frame_company_location.get_variable_value(),
        #     salesperson=self.home_frame_salesperson.get_variable_value(),
        #     email=self.home_frame_email.get_variable_value(),
        #     start_date=self.home_frame_start_date.get_variable_value(),
        #     # notes=self.home_frame_notes.get_variable_value(),
        #     # notes=self.home_frame_notes.get(0.0, 'end-1c'),
        #     notes=self.home_frame_notes.get_text(),
        #     data_uploaded=current_project_info.data_uploaded,
        #     upload_date=current_project_info.upload_date,
        #     transform_options=current_project_info.transform_options,
        #     uploaded_file_paths=current_project_info.uploaded_file_paths
        # )
        new_project_info_inputs = self.home_frame_project_info_section.get_project_info_inputs(self._get_project_number())
        new_project_info = ExistingProjectProjectInfo(
            project_number=self._get_project_number(),
            project_name=new_project_info_inputs.project_name,
            company_name=new_project_info_inputs.company_name,
            company_location=new_project_info_inputs.company_location,
            salesperson=new_project_info_inputs.salesperson,
            email=new_project_info_inputs.email,
            start_date=new_project_info_inputs.start_date,
            # notes=self.home_frame_notes.get_variable_value(),
            # notes=self.home_frame_notes.get(0.0, 'end-1c'),
            notes=new_project_info_inputs.notes,
            data_uploaded=current_project_info.data_uploaded,
            upload_date=current_project_info.upload_date,
            transform_options=current_project_info.transform_options,
            uploaded_file_paths=current_project_info.uploaded_file_paths
        )
        
        # Submit changes to DB
        # rows_updated = self.DataProfiler.update_project_info(new_project_info=new_project_info)
        response = self.DataProfiler.update_project_info(new_project_info=new_project_info)

        notification_dialog = None
        # if rows_updated == 1:
        if response.success:
            # Update home page
            self._refresh_project_info()
            self._create_home_frame()

            notification_dialog = NotificationDialog(self, title='Success!', text='Saved project info changes to database.')
        else:
            notification_dialog = NotificationDialog(self, title='Error', text=f'Could not save project info changes to database:\n\n{response.error_message}')

        # Show self again
        self._toggle_frame_grid(frame=self.loading_frame, grid=False)
        self._toggle_frame_grid(frame=self.home_frame, grid=True)
        self.update()

        # Display notification of results
        notification_dialog.attributes('-topmost', True)
        notification_dialog.mainloop()
        return

    def upload_frame_back_to_home_action(self):
        # Show self again
        self._toggle_frame_grid(frame=self.upload_frame, grid=False)
        self._toggle_frame_grid(frame=self.home_frame, grid=True)
        self.update()


    ''' UNUSED '''
    def validate_data_directory(self):
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
        else:
            self.upload_frame_submit_btn.configure(state='normal')


    def upload_data_action(self):
        data_dir = self.upload_frame_data_directory_browse.get_path()

        # Transform options don't need validation (cuz they're dropdowns and checkboxes)
        transform_options = TransformOptions(
            date_for_analysis=DateForAnalysis(self.upload_frame_date_for_analysis.get_variable_value()),
            weekend_date_rule=WeekendDateRules(self.upload_frame_weekend_date_rule.get_variable_value()),
            process_inbound_data=self.upload_frame_process_inbound_data.get_value(),
            process_inventory_data=self.upload_frame_process_inventory_data.get_value(),
            process_outbound_data=self.upload_frame_process_outbound_data.get_value(),
        )

        # Validate data directory
        data_directory_validation = self.DataProfiler.validate_data_directory(data_directory=data_dir, transform_options=transform_options)
        if not data_directory_validation.is_valid:
            errors_str = '\n\n'.join(data_directory_validation.errors_list)
            message = f'Data directory is not valid:\n\n{errors_str}'

            # Display error
            notification_dialog = NotificationDialog(self, title='Error', text=message)
            notification_dialog.attributes('-topmost', True)
            notification_dialog.mainloop()

            print(f'DATA DIR NOT VALID')
            return
        
        # Show loading frame while executing
        self._set_loading_frame_text('Transforming and uploading data...')
        self._toggle_frame_grid(frame=self.upload_frame, grid=False)
        self._toggle_frame_grid(frame=self.loading_frame, grid=True)
        self.update()

        # Transform and upload
        results = self.DataProfiler.transform_and_upload_data(data_directory=data_dir, transform_options=transform_options)

        # Navigate appropriately based on success
        message = ''
        self._toggle_frame_grid(frame=self.loading_frame, grid=False)
        if not results.success:
            # Back to upload frame
            self._toggle_frame_grid(frame=self.upload_frame, grid=True)

            # Display notification of results
            message = f'Trouble with the upload:\n{results.message}' 
        else:
            # Reset upload page
            self._create_upload_data_frame()
            self._toggle_frame_grid(frame=self.upload_frame, grid=False)
            
            # Back to home
            self._refresh_project_info()
            self._create_home_frame()
            self._toggle_frame_grid(frame=self.home_frame, grid=True)

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


    def show_upload_data_frame_action(self):
        self._toggle_frame_grid(self.home_frame, grid=False)
        self._toggle_frame_grid(self.upload_frame, grid=True)
        return


    def delete_project_action(self):
        
        notification_dialog = None

        if self._get_project_info().data_uploaded:
            message = f'Please delete project data before deleting project.'
            notification_dialog = NotificationDialog(self, title='Data Profiler', text=message)
        else:
            message = f'Are you sure you would like to delete project {self._get_project_number()}?'
            notification_dialog = ConfirmDeleteDialog(self, 
                                                      title='Confirm Deletion', 
                                                        text=message,
                                                        positive_action=self.delete_project,
                                                        negative_action=self.void)
            
        notification_dialog.attributes('-topmost', True)
        notification_dialog.mainloop()
        return
    
    def delete_project(self):
        # Show loading frame while executing
        self._set_loading_frame_text('Deleting project...')
        self._toggle_frame_grid(frame=self.home_frame, grid=False)
        self._toggle_frame_grid(frame=self.loading_frame, grid=True)
        self.update()

        # Delete project
        # rows_deleted = self.DataProfiler.delete_project()
        response = self.DataProfiler.delete_project()

        # if rows_deleted == 1:
        if response.success:
            # Show self again
            self._toggle_frame_grid(frame=self.loading_frame, grid=False)
            self._toggle_frame_grid(frame=self.start_frame, grid=True)
            self.update()
    
            # Display notification of results
            notification_dialog = NotificationDialog(self, title='Success!', text='Deleted project successfully.')        
        
        else:
            # Show self again
            self._toggle_frame_grid(frame=self.loading_frame, grid=False)
            self._toggle_frame_grid(frame=self.home_frame, grid=True)
            self.update()

            # Display notification of results
            notification_dialog = NotificationDialog(self, title='Error', text=f'Trouble deleting project:\n\n{response.error_message}')        
        
        notification_dialog.attributes('-topmost', True)
        notification_dialog.mainloop()
        return


    def delete_project_data_action(self):
        confirm_dialog = ConfirmDeleteDialog(self, 
                                             title='Confirm Deletion', 
                                             text=f'Are you sure you would like to delete project data for {self._get_project_number()}?',
                                             positive_action=self.delete_project_data,
                                             negative_action=self.void)
        
        confirm_dialog.attributes('-topmost', True)
        confirm_dialog.mainloop()
        return
    
    def delete_project_data(self):
        if not self._get_project_info().data_uploaded:
            print(f'NOTHING TO DELETE')
            return

        # Show loading frame while executing
        self._set_loading_frame_text('Deleting project data...')
        self._toggle_frame_grid(frame=self.home_frame, grid=False)
        self._toggle_frame_grid(frame=self.loading_frame, grid=True)
        self.update()

        results = self.DataProfiler.delete_project_data()

        message = ''
        if results.success:
            self._refresh_project_info()
            self._create_home_frame()

            message = 'Deleted project data successfully.'
        else:
            message = f'Encountered {len(results.errors_encountered)} errors when attempting to delete project data. Check log.'

        # Show self again
        self._toggle_frame_grid(frame=self.loading_frame, grid=False)
        self._toggle_frame_grid(frame=self.home_frame, grid=True)
        self.update()

        # Display notification of results
        notification_dialog = ResultsDialogWithLogFile(self, 
                                                       success=results.success, 
                                                       text=message, 
                                                       log_file_path=results.log_file_path)
        notification_dialog.attributes('-topmost', True)
        notification_dialog.mainloop()
        return


    ''' Critical functions '''

    def _init_data_profiler(self):
        self.DataProfiler = DataProfiler(project_number=self._get_project_number(), dev=self.dev)
        self._refresh_project_info()

    def _destroy_data_profiler(self):
        self.DataProfiler = None
        self.project_info = None

    ''' Helpers '''

    def pretty_print_rows_inserted(self, rows: TransformRowsInserted):
        return_str = ''

        return_str += f'Total rows inserted: {rows.total_rows_inserted}\n'
        return_str += f'SKUs: {rows.skus}\n'
        return_str += f'Inbound Receipts: {rows.inbound_receipts}\n'
        return_str += f'Inbound Lines: {rows.inbound_lines}\n'
        return_str += f'Inventory Lines: {rows.inventory_lines}\n'
        return_str += f'Outbound Orders: {rows.outbound_orders}\n'
        return_str += f'Outbound Lines: {rows.outbound_lines}'

        return return_str

    ''' Getters/Setters '''

    def _get_project_number(self):
        # return self.project_number_var.get()
        return self.select_project_number_dropdown.get_variable_value()
    
    # def _set_project_number(self, pn: str):
    #     self.project_number_var.set(pn)  

    def _get_project_info(self) -> ExistingProjectProjectInfo:
        return self.project_info
    
    def _refresh_project_info(self):
        self.project_info = self.DataProfiler.get_project_info()

    def _set_loading_frame_text(self, text: str):
        self.loading_frame_text_var.set(text)