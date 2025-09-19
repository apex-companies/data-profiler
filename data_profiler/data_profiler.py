'''
Jack Miller
Apex Companies
Oct 2024

Main Python class for DataProfiler app logic. This class shouldn't interact directly with DB - hand off to Service classes for this
'''

# Python
from typing import Literal, Callable
import os
from io import TextIOWrapper
from time import time
from datetime import datetime, timedelta
import math
from pathlib import Path
from pprint import pprint

import pandas as pd
import pyodbc
import plotly.express as px
from plotly.graph_objects import Figure

# Data Profiler
from .helpers.functions.functions import find_new_file_path

from .helpers.models.ProjectInfo import BaseProjectInfo, ExistingProjectProjectInfo
from .helpers.models.TransformOptions import TransformOptions
from .helpers.models.Responses import BaseDBResponse, TransformResponse, DBDownloadResponse
from .helpers.models.DataFiles import UploadFileType, UploadedFilePaths
from .helpers.models.GeneralModels import DownloadDataOptions, UnitOfMeasure
from .helpers.constants.data_file_constants import FILE_TYPES_COLUMNS_MAPPER
from .helpers.functions.data_file_functions import validate_file_structure, read_and_cleanse_uploaded_data_file

from .helpers.data_directory import DataDirectory

from .services.output_tables_service import OutputTablesService
from .services.transform_service import TransformService



class DataProfiler:

    def __init__(self, project_number: str, dev: bool = False):
        
        # Instantiate variables
        self.project_number = project_number
        self.dev = dev

        self.outputs_dir = os.getcwd()

        if self.dev and os.path.isdir('logs'):
            self.outputs_dir = f'{os.getcwd()}/logs'
        else:
            downloads_path = f'{Path.home()}/Downloads'
            if os.path.isdir(downloads_path):
                self.outputs_dir = downloads_path

        self.project_exists = False
        self.project_info = None
        
        # If project exists, update relevant variables
        project_numbers = self.get_output_tables_projects()
        if project_number in set(project_numbers):
            self.project_exists = True
            self.refresh_project_info()
        

    ''' Main functions - Create, Read, Update, Delete (CRUD) '''

    ## Create ##

    def create_new_project(self, project_info: BaseProjectInfo) -> BaseDBResponse:
        '''
        Create new project row in Project table

        Return
        ------
        BaseDBResponse
        '''
        
        if self.get_project_exists():
            return 'Project already exists. Try updating it instead'
        
        response = BaseDBResponse(project_number=project_info.project_number)

        try:
            with OutputTablesService(dev=self.dev) as service:
                response.rows_affected = service.insert_new_project_to_project_table(project_info=project_info)

                if response.rows_affected == 1:
                    response.success = True
        
                    self.project_exists = True
                    self.refresh_project_info()
        except pyodbc.DatabaseError as e:
            response.success = False
            response.message = e

        return response
    

    ## Read ##

    def get_output_tables_projects(self) -> list[str]:
        project_numbers = []

        with OutputTablesService(dev=self.dev) as service:
            project_numbers = service.get_output_tables_project_numbers()

        return project_numbers

    def refresh_project_info(self):
        if not self.get_project_exists():
            raise ValueError('Project does not yet exist')
        
        with OutputTablesService(dev=self.dev) as service:
            self.project_info = service.get_project_info(self.get_project_number())

    def download_data(self, download_option: DownloadDataOptions, target_directory: str) -> DBDownloadResponse:
        if not self.get_project_exists():
            raise ValueError('Project does not yet exist')
        
        project_info = self.get_project_info()
        project_number = project_info.project_number

        if not project_info.data_uploaded:
            raise ValueError('Project does not have any associated data. Upload some data first!')

        if not os.path.isdir(target_directory):
            raise FileNotFoundError(f'Invalid directory: "{target_directory}"')
        
        # Create subfolder
        today = datetime.today().strftime('%m-%d-%Y')
        subfolder_name = f'{project_number} - DataProfiler Data Download - {today}'
        download_directory = f'{target_directory}/{subfolder_name}'
        if not os.path.exists(download_directory):
            os.mkdir(download_directory)
        
        response = None
        if download_option == DownloadDataOptions.STORAGE_ANALYZER_INPUTS:
            # Create another subfolder for CSV files
            subfolder = find_new_file_path(f'{download_directory}/StorageAnalyzer Inputs')
            os.mkdir(subfolder)

            with OutputTablesService(dev=self.dev) as service:
                response = service.download_storage_analyzer_inputs(project_number=project_number, download_folder=subfolder)
                
        elif download_option == DownloadDataOptions.INVENTORY_STRATIFICATION_REPORT:
            with OutputTablesService(dev=self.dev) as service:
                response = service.download_inventory_stratification_report(project_number=project_number, download_folder=download_directory)

        elif download_option == DownloadDataOptions.SUBWAREHOUSE_MATERIAL_FLOW_REPORT_CARTONS:
            with OutputTablesService(dev=self.dev) as service:
                response = service.download_subwarehouse_material_flow_report(uom=UnitOfMeasure.CARTON, project_number=project_number, download_folder=download_directory)

        elif download_option == DownloadDataOptions.SUBWAREHOUSE_MATERIAL_FLOW_REPORT_PALLETS:
            with OutputTablesService(dev=self.dev) as service:
                response = service.download_subwarehouse_material_flow_report(uom=UnitOfMeasure.PALLET, project_number=project_number, download_folder=download_directory)

        elif download_option == DownloadDataOptions.ITEMS_MATERIAL_FLOW_REPORT_EACHES:
            with OutputTablesService(dev=self.dev) as service:
                response = service.download_items_material_flow_report(uom=UnitOfMeasure.EACH, project_number=project_number, download_folder=download_directory)

        elif download_option == DownloadDataOptions.ITEMS_MATERIAL_FLOW_REPORT_CARTONS:
            with OutputTablesService(dev=self.dev) as service:
                response = service.download_items_material_flow_report(uom=UnitOfMeasure.CARTON, project_number=project_number, download_folder=download_directory)

        elif download_option == DownloadDataOptions.ITEMS_MATERIAL_FLOW_REPORT_PALLETS:
            with OutputTablesService(dev=self.dev) as service:
                response = service.download_items_material_flow_report(uom=UnitOfMeasure.PALLET, project_number=project_number, download_folder=download_directory)

        else:
            response = DBDownloadResponse(project_number=project_number)
        

        return response


    ## Update ##

    def update_project_info(self, new_project_info: ExistingProjectProjectInfo) -> BaseDBResponse:
        if not self.get_project_exists():
            raise ValueError('Project does not yet exist')
        
        response = BaseDBResponse(project_number=new_project_info.project_number)

        try:
            with OutputTablesService(dev=self.dev) as service:
                response.rows_affected = service.update_project_in_project_table(new_project_info=new_project_info)

                if response.rows_affected == 1:
                    response.success = True

        except pyodbc.DatabaseError as e:
            response.success = False
            response.message = e

        self.refresh_project_info()

        return response
    
    def update_item_master(self, file_path: str, update_progress_text_func: Callable[[str], None] = None) -> BaseDBResponse:
        '''
        Update SKUs in Item Master with a CSV of valid item master columns

        Params
        ------
        file_path : str
            location of a file with valid item master columns. required cols = [ SKU ]

        Return
        ------
        BaseDBResponse
        '''

        ## Validate inputs
        if not self.get_project_exists():
            raise ValueError('Project does not yet exist')
                
        project_info = self.get_project_info()

        if not project_info.data_uploaded:
            raise ValueError('Project does not have any associated data. Upload some data first!')


        response = BaseDBResponse(project_number=project_info.project_number)

        # Validate given file
        if update_progress_text_func: update_progress_text_func('Validating file upload...')
        validation_obj = validate_file_structure(file_type=UploadFileType.ITEM_MASTER_UPDATE, file_path=file_path, required_columns=['SKU'], valid_columns=FILE_TYPES_COLUMNS_MAPPER['ItemMaster'])

        if not validation_obj.is_valid:
            response.success = False

            if not validation_obj.is_present:
                response.message = f'Given file "{file_path}" does not exist. Please choose a valid file! Quitting.'
            elif len(validation_obj.missing_columns) > 0:
                response.message = f'Given file "{file_path}" does is missing columns. Quitting.\n\nMissing columns: [{", ".join(validation_obj.missing_columns)}]\n\nGiven columns: [{", ".join(validation_obj.given_columns)}]'
            elif len(validation_obj.invalid_columns) > 0:
                response.message = f'Given file "{file_path}" has some invalid columns. ONLY provide valid Item Master columns. Quitting.\n\nInvalid columns: {", ".join(validation_obj.invalid_columns)}'
            else:
                response.message = f'Given file "{file_path}" is not valid. Please provide a valid data set. Quitting.'

            return response
        
        ## Update item master

        # Read file
        if update_progress_text_func: update_progress_text_func('Reading file...')
        df, errors_list = read_and_cleanse_uploaded_data_file(file_type=UploadFileType.ITEM_MASTER, file_path=file_path)
        if len(errors_list) > 0:
            print(f'Errors reading item master: {", ".join(errors_list)}')
            response.success = False
            response.message = f'Encountered some errors while reading file: {", ".join(errors_list)}'
            return response
        else:
            # Shave df back down to original columns
            # NOTE: read_and_cleanse_uploaded_data_file return dfs with all item master columns and NaNs filled for columns not given
            df = df[validation_obj.given_columns]
        
        print(df.head())

        # Persist
        try:
            with OutputTablesService(dev=self.dev) as service:
                if update_progress_text_func: update_progress_text_func('Validating SKUs...')
                # Get list of SKUs and drop any from list that don't exist in database
                sku_list = service.get_sku_list(project_number=project_info.project_number)
                sku_list_set = set(sku_list)

                b = len(df)
                df = df.loc[df['SKU'].isin(sku_list_set), :]
                a = len(df)
                skus_dropped = b - a
                print(f'Dropped {skus_dropped:,} SKUs not in database')

                # Update item master
                if update_progress_text_func: update_progress_text_func('Saving changes...')
                response.rows_affected = service.update_item_master(project_info.project_number, data_frame=df)

                if response.rows_affected > 0:
                    response.success = True

                    if skus_dropped > 0:
                        response.message += f'\n\nNote: Dropped {skus_dropped:,} SKUs from given file that are not in database.'

        except pyodbc.DatabaseError as e:
            response.success = False
            response.message = e

        self.refresh_project_info()

        return response
        
    def transform_and_upload_data(self, data_directory: str, transform_options: TransformOptions, update_progress_text_func: Callable[[str], None] = None) -> TransformResponse:
        if not self.get_project_exists():
            raise ValueError('Project does not yet exist.')
        
        project_info = self.get_project_info()

        if project_info.data_uploaded:
            raise ValueError('Project already has data uploaded. If you would like to update project data, delete it and re-upload.')

        # Create log file
        log_file_path = f'{self.get_outputs_dir()}/{project_info.project_number}-{datetime.now().strftime(format="%Y%m%d-%H.%M.%S")}_transform.txt'
        log_file = open(log_file_path, 'w+')

        log_file.write(f'PROJECT NUMBER: {project_info.project_number}\n\n')
        log_file.flush()

        # Create response object
        transform_response = TransformResponse(project_number=project_info.project_number, log_file_path=log_file_path)

        # Create DataDirectory object
        DataDirectoryObj = DataDirectory(path=data_directory, transform_options=transform_options, update_progress_text_func=update_progress_text_func)

        ## Validate data directory ##
        if update_progress_text_func: update_progress_text_func('Validating file uploads...')

        dir_validation_obj = DataDirectoryObj.validate_directory()
        if not dir_validation_obj.is_valid:
            errors_str = '\n\n'.join(dir_validation_obj.errors_list)
            message = f'Invalid data directory:\n\n{errors_str}'

            transform_response.success = False
            transform_response.message = message
            return transform_response

        # NOTE: not updated with dp-92-create-header-tables. Not worth updating database, these aren't used anywhere
        uploaded_files = UploadedFilePaths(
            item_master = dir_validation_obj.item_master.file_path,
            inbound_header = dir_validation_obj.inbound_header.file_path if transform_options.process_inbound_data else '',
            inbound_details = dir_validation_obj.inbound_details.file_path if transform_options.process_inbound_data else '',
            inventory = dir_validation_obj.inventory.file_path if transform_options.process_inventory_data else '',
            order_header = dir_validation_obj.order_header.file_path if transform_options.process_outbound_data else '',
            order_details = dir_validation_obj.order_details.file_path if transform_options.process_outbound_data else ''
        )


        ## Read files and validate contents
        success, message = DataDirectoryObj.read_and_validate_file_contents(log_file=log_file)
        if not success:
            transform_response.success = False
            transform_response.message = message
            return transform_response


        ## Transform and persist data ##
        
        transform_st = time()
        print('Transforming...')
    
        transform_response = None
        with TransformService(
                project_number=project_info.project_number, 
                DataDirectoryObj=DataDirectoryObj,
                transform_options=transform_options, 
                update_progress_text_func=update_progress_text_func, 
                dev=self.dev) as service:
            transform_response = service.transform_and_persist_dataframes(log_file=log_file)

        transform_response.log_file_path = log_file_path

        transform_et = time()
        print(f'Total transform time: {timedelta(seconds=transform_et-transform_st)}')

        # If unsuccessful, delete any rows that were inserted
        if not transform_response.success:
            if update_progress_text_func: update_progress_text_func('Something happened. Deleting data...\n\n(You may need to re-connect to VPN)')

            log_file.write('ERROR - Unsuccessful transform/insertion. Deleting any inserted data from DB.\n')
            self.delete_project_data(log_file=log_file)
        else:
            # Update row in Project
            new_project_info = project_info.model_copy()
            new_project_info.transform_options = transform_options
            new_project_info.data_uploaded = transform_response.success
            new_project_info.upload_date = datetime.strftime(datetime.today(), format='%Y-%m-%d')
            new_project_info.uploaded_file_paths = uploaded_files

            self.update_project_info(new_project_info=new_project_info)

        log_file.close()

        print(self.get_project_info())
        return transform_response
    

    ## Delete ##

    def delete_project_data(self, log_file: TextIOWrapper | None = None, update_progress_text_func: Callable[[str], None] = None) -> BaseDBResponse:
        if not self.get_project_exists():
            raise ValueError('Project does not yet exist')
        
        project_info = self.get_project_info()

        # Start log file
        log_file_given = (log_file != None)
        log_file_path = ''
        if not log_file_given:
            log_file_path = f'{self.get_outputs_dir()}/{project_info.project_number}-{datetime.now().strftime(format="%Y%m%d-%H.%M.%S")}_delete_from_output_tables.txt'

            log_file = open(log_file_path, 'w+')
            log_file.write(f'PROJECT NUMBER: {project_info.project_number}\n\n')
            log_file.flush()

        # Try delete
        response: BaseDBResponse = None
        with OutputTablesService(dev=self.dev) as service:
            response = service.delete_project_data(project_number=project_info.project_number, log_file=log_file, update_progress_text_func=update_progress_text_func)
            response.log_file_path = log_file_path

        # Update row in Project, if successful
        if response.success:
            new_project_info = self.get_project_info().model_copy()
            new_project_info.transform_options = TransformOptions(date_for_analysis=None, weekend_date_rule=None)
            new_project_info.data_uploaded = False
            new_project_info.upload_date = None
            new_project_info.uploaded_file_paths = UploadedFilePaths()

            self.update_project_info(new_project_info=new_project_info)

        if not log_file_given:
            log_file.close()

        return response
    
    def delete_project(self) -> BaseDBResponse:
        if not self.get_project_exists():
            raise ValueError('Project does not yet exist')
        
        project_info = self.get_project_info()

        if project_info.data_uploaded:
            raise ValueError('Please delete project data before deleting project.')
        
        # Try delete
        response = BaseDBResponse(project_number=project_info.project_number)
        try:
            with OutputTablesService(dev=self.dev) as service:
                response.rows_affected = service.delete_project(project_number=project_info.project_number)

                if response.rows_affected == 1:
                        response.success = True

        except pyodbc.DatabaseError as e:
            response.success = False
            response.message = e
        
        return response


    ''' Main Functions - Other Analysis '''

    def describe_data_frame(self, file_path: str, columns: str, file_type: Literal['csv', 'xslx'] = 'csv', sheet_name: str = None, group_col: str = None) -> str:
        '''
        A function that describes a data frame. Its goal is to summarize the range of values found in every column and to alert the user to any flaws or errors in the data.

        Params
        ------
        df : pd.DataFrame
            a pandas dataframe
        group_col : str
            a *categorical* column in df by which the data is usefully grouped / aggregated

        Returns
        -------
        Path to the folder of the exports. Exports:

        1. an XLSX book with the original df and a sheet that describes its columns  
        2. an HTML file with distribution charts of the numeric df columns
        '''
    
        ## Create subfolder
        project_info = self.get_project_info()

        subfolder = f'{self.project_number} Data Description'
        OUTPUT_DIR = f'{self.outputs_dir}/{subfolder}'
        if not os.path.exists(OUTPUT_DIR):
            os.mkdir(OUTPUT_DIR)

        ## Start
        df: pd.DataFrame = None
        
        if file_type == 'csv':
            df = pd.read_csv(file_path, usecols=columns)
        else:
            df = pd.read_excel(file_path, sheet_name=sheet_name, usecols=columns)

        df = df.replace('', pd.NA)

        df_length = df.shape[0]
        print(f'Data frame # rows: {df_length}')

        ## Create Describe table
        df_val = df.describe(include='all').transpose()

        df_val['IQR'] = df_val['75%'] - df_val['25%']
        df_val['Lower Fence'] = df_val['25%'] - (1.5 * df_val['IQR'])
        df_val['Upper Fence'] = df_val['75%'] + (1.5 * df_val['IQR'])
        df_val['Extreme Upper Fence'] = df_val['75%'] + (3 * df_val['IQR'])

        df_val['Missing Values'] = df_length - df_val['count']

        ## Explore numeric columns
        df_val['Negative Values'] = 0
        df_val['Zero Values'] = 0
        df_val['Lower Outliers'] = 0
        df_val['Upper Outliers'] = 0
        df_val['Extreme Upper Outliers'] = 0

        summary_strs: list[str] = []
        histograms: list[Figure] = []
        box_plots: list[Figure] = []

        numeric_cols = df.select_dtypes(include='number').columns
        for col in numeric_cols:
            print('-'*50)
            print(f'|{col.center(48)}|')
            print('-'*50)

            ## Min / Avg / Max
            mini = df_val.loc[col, 'min']
            avg = df_val.loc[col, 'mean']
            maxi = df_val.loc[col, 'max']

            print(f'Min: {mini:,}')
            print(f'Avg: {avg:,.3f}')
            print(f'Max: {maxi:,}')

            ## Missing / Negatives / Zeros
            missing_values = df_val.loc[col, 'Missing Values']

            negative_values = len(df.loc[df[col] < 0, :])
            df_val.loc[col, 'Negative Values'] = negative_values

            zero_values = len(df.loc[df[col] == 0, :])
            df_val.loc[col, 'Zero Values'] = zero_values

            print(f'\nMissing: {missing_values:,.0f}')
            print(f'Negatives: {negative_values:,.0f}')
            print(f'Zeros: {zero_values:,.0f}')

            ## Outliers
            lower_fence = df_val.loc[col, 'Lower Fence']
            upper_fence = df_val.loc[col, 'Upper Fence']
            extreme_upper_fence = df_val.loc[col, 'Extreme Upper Fence']

            lower_outliers = len(df.loc[df[col] < lower_fence, :])
            upper_outliers = len(df.loc[df[col] > upper_fence, :])
            extreme_upper_outliers = len(df.loc[df[col] > extreme_upper_fence, :])
            
            df_val.loc[col, 'Lower Outliers'] = lower_outliers
            df_val.loc[col, 'Upper Outliers'] = upper_outliers
            df_val.loc[col, 'Extreme Upper Outliers'] = extreme_upper_outliers
            
            print(f'\nLower Fence: {lower_fence:,.3f}')
            print(f'   Outliers: {lower_outliers:,.0f}')
            print(f'Upper Fence: {upper_fence:,.3f}')
            print(f'   Outliers: {upper_outliers:,.0f}')
            print(f'Extreme Upper Fence: {extreme_upper_fence:,.3f}')
            print(f'   Outliers: {extreme_upper_outliers:,.0f}')

            ## Summary
            header = f"<h2>{col}</h2>"
            avgs = f"Min: {mini:,}<br>Avg: {avg:,.3f}<br>Max: {maxi:,}<br>"
            bad_vals = f"<br>Missing: {missing_values:,.0f}<br>Negatives: {negative_values:,.0f}<br>Zeros: {zero_values:,.0f}<br>"
            outliers = f"<br>Lower Fence: {lower_fence:,.3f}<br>   Outliers: {lower_outliers:,.0f}<br>Upper Fence: {upper_fence:,.3f}<br>   Outliers: {upper_outliers:,.0f}<br>Extreme Upper Fence: {extreme_upper_fence:,.3f}<br>   Outliers: {extreme_upper_outliers:,.0f}<br>"

            summary_str = header + avgs + bad_vals + outliers

            ## Charts
            histogram = px.histogram(
                data_frame=df,
                x=col,
                title=f'Distribution: {col}'
            )
            histogram.update_layout(yaxis_title='# SKUs')

            box_plot_title = f'Distribution by {group_col}: {col}' if group_col else f'Distribution: {col}'
            box_plot = px.box(
                data_frame=df,
                x=group_col,
                y=col,
                title=box_plot_title
            )

            summary_strs.append(summary_str)
            histograms.append(histogram)
            box_plots.append(box_plot)


        ## Export
        df_val_col_order = ['Missing Values', 'Negative Values',
        'Zero Values', 'Lower Outliers', 'Upper Outliers',
        'Extreme Upper Outliers', 'count', 'unique', 'top', 'freq', 'mean', 'std', 'min', '25%', '50%',
        '75%', 'max', 'IQR', 'Lower Fence', 'Upper Fence',
        'Extreme Upper Fence']
        df_val = df_val.reindex(columns=df_val_col_order)
        
        with pd.ExcelWriter(f'{OUTPUT_DIR}/description.xlsx') as writer:
            df_size = df.shape[0] * df.shape[1]
            if df_size < 100000:
                df.to_excel(writer, index=False, sheet_name='Original')
            df_val.to_excel(writer, index=True, sheet_name='Description Sheet')

        with open(f'{OUTPUT_DIR}/distribution charts.html', 'w+') as f:
            f.write(f'''<!DOCTYPE html>
                        <html>
                        <head>
                        <meta charset="utf-8" />   <!--It is necessary to use the UTF-8 encoding with plotly graphics to get e.g. negative signs to render correctly -->
                        <meta name="viewport" content="width=device-width, initial-scale=1.0" />
                        </head>

                        <body>
                        <h1>{self.project_number} - {project_info.company_name} - {project_info.company_location}</h1>
                        <p>{file_path}</p>
                        <br><br>
                    ''')
            
            for i in range(len(summary_strs)):
                summary_str = summary_strs[i]
                histogram = histograms[i]
                box_plot = box_plots[i]

                hist_html = histogram.to_html(full_html=False, include_plotlyjs='cdn')
                box_html = box_plot.to_html(full_html=False, include_plotlyjs='cdn')
                
                f.write(summary_str)
                f.write(hist_html)
                f.write(box_html)

            f.write('</body></html>')

        return OUTPUT_DIR


    ''' Getters/Setters '''

    def get_project_number(self) -> str:
        return self.project_number

    def get_project_exists(self) -> bool:
        return self.project_exists
    
    def get_project_info(self) -> ExistingProjectProjectInfo:
        return self.project_info
    
    def get_outputs_dir(self) -> str:
        return self.outputs_dir
    
    def set_outputs_dir(self, path: str):
        if not os.path.isdir(path):
            return
        
        self.outputs_dir = path