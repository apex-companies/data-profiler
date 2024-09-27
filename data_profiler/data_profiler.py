'''
Jack Miller
Apex Companies
Oct 2024

Main Python class for DataProfiler app logic
'''

import os
from time import time
from datetime import datetime, timedelta
from typing import Annotated
import math

import pandas as pd

from .models.ProjectInfo import BaseProjectInfo, ExistingProjectProjectInfo, UploadedFile, UploadedFilePaths
from .models.TransformOptions import TransformOptions

from .helpers.constants import UploadFileTypes, UPLOADS_REQUIRED_COLUMNS_MAPPER, UPLOADS_REQUIRED_DTYPES_MAPPER
from .helpers.functions import validate_csv_column_names

from .services.output_tables_service import OutputTablesService
from .services.transform_service import TransformService

class DataProfiler:

    def __init__(self, project_number: Annotated[str, 'Apex Project Number'], dev: bool = False):
        
        # Instantiate variables
        self.project_number = project_number
        self.dev = dev

        self.project_exists = False
        self.project_info = None
        
        self.OutputTablesService = OutputTablesService(dev=self.dev)
        self.TransformService = TransformService(dev=self.dev)
        
        # If project exists, update relevant variables
        project_numbers = self.get_output_tables_projects()
        if project_number in project_numbers:
            self.project_exists = True
            self.refresh_project_info()
        

    ''' Main functions '''

    def get_output_tables_projects(self) -> list[str]:
        return self.OutputTablesService.get_output_tables_project_numbers()

    def refresh_project_info(self):
        if not self.get_project_exists():
            return 'Project does not yet exist'
        
        self.project_info = self.OutputTablesService.get_project_info(self.project_number)

        # info = { }
        # print(project_number)

        # project_numbers = get_output_tables_project_numbers()
        # if project_number not in project_numbers:
        #     response.status_code = status.HTTP_400_BAD_REQUEST
        #     return { "Error": "Project Number not found" }
        
        # company_table_records = get_company_table_row_for_project(project_number=project_number)
        # item_master_skus = get_skus_in_item_master_for_project(project_number=project_number)
        # lines_in_outbound = get_lines_in_outbound_for_project(project_number=project_number)

        # info['ProjectNumber'] = company_table_records[0][0]
        # info['Client'] = company_table_records[0][1]
        # info['Project Name'] = company_table_records[0][4]
        # info['Client Location'] = company_table_records[0][3]
        # info['Salesman'] = company_table_records[0][2]
        # info['SKUs'] = len(item_master_skus)
        # info['Lines in Outbound'] = lines_in_outbound

        # return info

    def create_new_project(self, project_info: BaseProjectInfo): #-> Response
        if self.get_project_exists():
            return 'Project already exists. Try updating it instead'
        
        rows_inserted = self.OutputTablesService.insert_new_project_to_project_table(project_info=project_info)
        self.refresh_project_info()

        return rows_inserted

    def update_project_info(self, new_project_info: ExistingProjectProjectInfo): #-> Response:
        if not self.get_project_exists():
            return 'Project does not yet exist'
        
        rows_inserted = self.OutputTablesService.update_project_in_project_table(new_project_info=new_project_info)
        self.refresh_project_info()

        return rows_inserted

    def _validate_data_directory(self, data_directory: str) -> list[str]:
        # Validate data directory
        missing_files = []
        for file in UploadFileTypes:
            if not os.path.exists(f'{data_directory}/{file.value}.csv'):
                missing_files.append(file.value)

        return missing_files
    
    def _validate_file_columns(self, file_paths: UploadedFilePaths) -> dict:
        # Validate columns
        missing_cols_dict = {}
        
        missing_cols = validate_csv_column_names(file_path=file_paths.item_master, columns=UPLOADS_REQUIRED_COLUMNS_MAPPER[UploadFileTypes.ITEM_MASTER.value])
        if missing_cols:
            missing_cols_dict[UploadFileTypes.ITEM_MASTER.value] = missing_cols

        missing_cols = validate_csv_column_names(file_path=file_paths.inbound_header, columns=UPLOADS_REQUIRED_COLUMNS_MAPPER[UploadFileTypes.INBOUND_HEADER.value])
        if missing_cols:
            missing_cols_dict[UploadFileTypes.INBOUND_HEADER.value] = missing_cols

        missing_cols = validate_csv_column_names(file_path=file_paths.inbound_details, columns=UPLOADS_REQUIRED_COLUMNS_MAPPER[UploadFileTypes.INBOUND_DETAILS.value])
        if missing_cols:
            missing_cols_dict[UploadFileTypes.INBOUND_DETAILS.value] = missing_cols

        missing_cols = validate_csv_column_names(file_path=file_paths.inventory, columns=UPLOADS_REQUIRED_COLUMNS_MAPPER[UploadFileTypes.INVENTORY.value])
        if missing_cols:
            missing_cols_dict[UploadFileTypes.INVENTORY.value] = missing_cols

        missing_cols = validate_csv_column_names(file_path=file_paths.order_header, columns=UPLOADS_REQUIRED_COLUMNS_MAPPER[UploadFileTypes.ORDER_HEADER.value])
        if missing_cols:
            missing_cols_dict[UploadFileTypes.ORDER_HEADER.value] = missing_cols

        missing_cols = validate_csv_column_names(file_path=file_paths.order_details, columns=UPLOADS_REQUIRED_COLUMNS_MAPPER[UploadFileTypes.ORDER_DETAILS.value])
        if missing_cols:
            missing_cols_dict[UploadFileTypes.ORDER_DETAILS.value] = missing_cols    
        
        # missing = validate_csv_column_names(file_path=file_paths.inbound_header, columns=UPLOADS_REQUIRED_COLUMNS_MAPPER[UploadFileTypes.INBOUND_HEADER.value])
        # missing = validate_csv_column_names(file_path=file_paths.inbound_details, columns=UPLOADS_REQUIRED_COLUMNS_MAPPER[UploadFileTypes.INBOUND_DETAILS.value])
        # missing = validate_csv_column_names(file_path=file_paths.inventory, columns=UPLOADS_REQUIRED_COLUMNS_MAPPER[UploadFileTypes.INVENTORY.value])
        # missing = validate_csv_column_names(file_path=file_paths.order_header, columns=UPLOADS_REQUIRED_COLUMNS_MAPPER[UploadFileTypes.ORDER_HEADER.value])
        # missing = validate_csv_column_names(file_path=file_paths.order_details, columns=UPLOADS_REQUIRED_COLUMNS_MAPPER[UploadFileTypes.ORDER_DETAILS.value])
        
        # if missing_cols != {}:
        #     raise ValueError(f'Missing columns in files:\n {missing_cols}')

        return missing_cols_dict
    
    def _read_and_cleanse_uploaded_data_file(self, file_type: UploadFileTypes, file_path: str) -> tuple[pd.DataFrame, list]:

        # # Convert column types to match database and re-order columns. Find type errors now before attempting DB transactions
        # # Returns cleansed dataframe
        # # def cleanse_raw_data_table(file_type: str, df: pd.DataFrame) -> pd.DataFrame:
        # for file in file_paths:

        dtypes = UPLOADS_REQUIRED_DTYPES_MAPPER[file_type.value]

        df = pd.read_csv(file_path)

        st = time()
        errors_encountered = 0
        errors_list = []
        for col, dtype in dtypes.items():
            try:
                if dtype == 'date':
                    df[col] = pd.to_datetime(df[col], dayfirst=True, format='mixed', errors='coerce')
                    df[col] = df[col].replace(to_replace=math.nan, value='1900-01-01')
                elif dtype == 'float64' or dtype == 'int64':
                    df[col] = pd.to_numeric(df[col], errors='coerce')
                    df[col] = df[col].replace(to_replace=math.nan, value=0)
                elif dtype == 'object':
                    df[col] = df[col].astype("string")
            except Exception as e:
                # if log_file: log_file.write(f'ERROR converting field "{col}" to correct type: {e}\n')
                print(f'ERROR converting field "{col}" to correct type: {e}\n')
                errors_list.append(e)
                errors_encountered += 1

        # if errors_encountered > 0:
            # if log_file: log_file.write(f'{errors_encountered} error(s) encountered converting to correct dtypes. Quitting before DB insertion.\n')
            # print(f'{errors_encountered} error(s) encountered converting to correct dtypes. Quitting before DB insertion.\n')
            # raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f'Error(s) converting types: {", ".join(errors_list)}')
        # else:
            # if log_file: log_file.write(f'Dtype conversions successful. Inserting to db.\n')
            # print(f'Dtype conversions successful. Inserting to db.\n')

        et = time()
        # print(f'Time to convert: {timedelta(seconds=et-st)}')

        st = time()
        # Reorder columns to match SQL insert query order
        df = df.reindex(columns=dtypes.keys())
        et = time()
        # print(f'Time to reindex: {timedelta(seconds=et-st)}')


        # return df
        return df, errors_list


    def transform_and_upload_data(self, data_directory: str, transform_options: Annotated[TransformOptions, 'Some options for analysis']): #-> Response
        if not self.get_project_exists():
            return 'Project does not yet exist'
        
        project_info = self.get_project_info()

        if project_info.data_uploaded:
            return 'Project already exists. If you would like to update project data, delete it and re-upload'
        
        # Validate data directory
        missing_files = self._validate_data_directory(data_directory=data_directory)
                    
        if len(missing_files) > 0:
            raise FileNotFoundError(f'Some files missing from data directory: {", ".join(missing_files)}')
        
        # Validate uploaded files
        uploaded_files = UploadedFilePaths(
            item_master = f'{data_directory}/{UploadFileTypes.ITEM_MASTER.value}.csv',
            inbound_header = f'{data_directory}/{UploadFileTypes.INBOUND_HEADER.value}.csv',
            inbound_details = f'{data_directory}/{UploadFileTypes.INBOUND_DETAILS.value}.csv',
            inventory = f'{data_directory}/{UploadFileTypes.INVENTORY.value}.csv',
            order_header = f'{data_directory}/{UploadFileTypes.ORDER_HEADER.value}.csv',
            order_details = f'{data_directory}/{UploadFileTypes.ORDER_DETAILS.value}.csv'
            # item_master = UploadedFile(file_type=UploadFileTypes.ITEM_MASTER, file_path=f'{data_directory}/{UploadFileTypes.ITEM_MASTER.value}.csv'),
            # inbound_header = UploadedFile(file_type=UploadFileTypes.INBOUND_HEADER, file_path=f'{data_directory}/{UploadFileTypes.INBOUND_HEADER.value}.csv'),
            # inbound_details = UploadedFile(file_type=UploadFileTypes.INBOUND_DETAILS, file_path=f'{data_directory}/{UploadFileTypes.INBOUND_DETAILS.value}.csv'),
            # inventory = UploadedFile(file_type=UploadFileTypes.INVENTORY, file_path=f'{data_directory}/{UploadFileTypes.INVENTORY.value}.csv'),
            # order_header = UploadedFile(file_type=UploadFileTypes.ORDER_HEADER, file_path=f'{data_directory}/{UploadFileTypes.ORDER_HEADER.value}.csv'),
            # order_details = UploadedFile(file_type=UploadFileTypes.ORDER_DETAILS, file_path=f'{data_directory}/{UploadFileTypes.ORDER_DETAILS.value}.csv')'
        )
        
        missing_cols_dict = self._validate_file_columns(file_paths=uploaded_files)
        if missing_cols_dict != {}:
            raise ValueError(f'Missing columns in files:\n {missing_cols_dict}')

        master_errors_dict = {}

        # Read files (and cleanse along the way)
        item_master, item_master_errors_list = self._read_and_cleanse_uploaded_data_file(file_type=UploadFileTypes.ITEM_MASTER, file_path=uploaded_files.item_master)
        print(item_master.head())
        print(f'Errors reading item master: {", ".join(item_master_errors_list)}')
        if len(item_master_errors_list) > 0:
            master_errors_dict[UploadFileTypes.ITEM_MASTER.value] = item_master_errors_list

        inbound_header, inbound_header_errors_list = self._read_and_cleanse_uploaded_data_file(file_type=UploadFileTypes.INBOUND_HEADER, file_path=uploaded_files.inbound_header)
        print(inbound_header.head())
        print(f'Errors reading inbound header: {", ".join(inbound_header_errors_list)}')
        if len(inbound_header_errors_list) > 0:
            master_errors_dict[UploadFileTypes.INBOUND_HEADER.value] = inbound_header_errors_list

        inbound_details, inbound_details_errors_list = self._read_and_cleanse_uploaded_data_file(file_type=UploadFileTypes.INBOUND_DETAILS, file_path=uploaded_files.inbound_details)
        print(inbound_details.head())
        print(f'Errors reading inbound details: {", ".join(inbound_details_errors_list)}')
        if len(inbound_details_errors_list) > 0:
            master_errors_dict[UploadFileTypes.INBOUND_DETAILS.value] = inbound_details_errors_list

        inventory, inventory_errors_list = self._read_and_cleanse_uploaded_data_file(file_type=UploadFileTypes.INVENTORY, file_path=uploaded_files.inventory)
        print(inventory.head())
        print(f'Errors reading inventory: {", ".join(inventory_errors_list)}')
        if len(inventory_errors_list) > 0:
            master_errors_dict[UploadFileTypes.INVENTORY.value] = inventory_errors_list

        order_header, order_header_errors_list = self._read_and_cleanse_uploaded_data_file(file_type=UploadFileTypes.ORDER_HEADER, file_path=uploaded_files.order_header)
        print(order_header.head())
        print(f'Errors reading order header: {", ".join(order_header_errors_list)}')
        if len(order_header_errors_list) > 0:
            master_errors_dict[UploadFileTypes.ORDER_HEADER.value] = order_header_errors_list

        order_details, order_details_errors_list = self._read_and_cleanse_uploaded_data_file(file_type=UploadFileTypes.ORDER_DETAILS, file_path=uploaded_files.order_details)
        print(order_details.head())
        print(f'Errors reading order details: {", ".join(order_details_errors_list)}')
        if len(order_details_errors_list) > 0:
            master_errors_dict[UploadFileTypes.ORDER_DETAILS.value] = order_details_errors_list

        if master_errors_dict != {}:
            return f'Errors. Quitting.\n{master_errors_dict}'

        ''' Transform and persist data '''
        transform_st = time()
        print('Transforming...')
        rows_inserted = self.TransformService.transform_and_persist_dataframes(project_number=project_info.project_number, transform_options=transform_options, 
                                                        item_master_df=item_master, inbound_header_df=inbound_header, inbound_details_df=inbound_details,
                                                        inventory_df=inventory, order_header_df=order_header, order_details_df=order_details)

        transform_et = time()
        print(f'Total transform time: {timedelta(seconds=transform_et-transform_st)}')


        # Update row in Project
        new_project_info = project_info.model_copy()
        new_project_info.transform_options = transform_options
        new_project_info.data_uploaded = True
        new_project_info.upload_date = datetime.strftime(datetime.today(), format='%Y-%m-%d')
        new_project_info.uploaded_file_paths = uploaded_files

        self.update_project_info(new_project_info=new_project_info)

        print(self.get_project_info())
        return rows_inserted

        # response_obj = BaseDBInteractionResponse()

        # # check to make sure data exists in RawData schema
        # raw_data_project_numbers = get_raw_data_project_numbers()
        # if project_number not in raw_data_project_numbers:
        #     response.status_code = status.HTTP_400_BAD_REQUEST
        #     response_obj.rows_affected = 0
        #     response_obj.message = "Project # has no raw data. Please upload raw data to database before continuing."
        #     return response_obj

        # # Check if Project # is already in OutputTables
        # output_tables_project_numbers = get_output_tables_project_numbers()
        # if project_number in output_tables_project_numbers:
        #     response.status_code = status.HTTP_400_BAD_REQUEST
        #     response_obj.rows_affected = 0
        #     response_obj.message = "Project # already has output table data. Please wipe data from output tables before starting afresh, if desired."
        #     return response_obj

        # # Transform and persist data
        # print('Transforming...')
        # rows_inserted = transform_by_project_number(project_number=project_number, project_info=project_info, variables_and_switches=variables_and_switches)
        
        # response_obj.rows_affected = rows_inserted
        # response_obj.message = "Insert seems to have been successful. Check logs to ensure."
        # return response_obj 

    def delete_project_data(self): # -> Response:
        if not self.get_project_exists():
            return 'Project does not yet exist'
        
        rows_deleted = self.OutputTablesService.delete_project_data(project_number=self.project_number)

        # Update row in Project
        new_project_info = self.get_project_info().model_copy()
        new_project_info.transform_options = TransformOptions(date_for_analysis=None, weekend_date_rule=None)
        new_project_info.data_uploaded = False
        new_project_info.upload_date = None
        new_project_info.uploaded_file_paths = UploadedFilePaths()

        self.update_project_info(new_project_info=new_project_info)

        print(self.get_project_info())
        return rows_deleted
    
        # response_obj = BaseDBInteractionResponse()
        
        # project_nums = get_output_tables_project_numbers()
        # if project_number not in project_nums:
        #     response.status_code = status.HTTP_400_BAD_REQUEST
        #     response_obj.rows_affected = 0
        #     response_obj.message = f"Project Number {project_number} does not exist."
        #     return response_obj

        # # Delete
        # rows_affected = delete_from_output_tables_by_project_number(project_number=project_number)
        
        # response_obj.rows_affected = rows_affected
        # response_obj.message = "Delete seems to have been successful. Check logs to ensure."
        # return response_obj

    ''' Getters/Setters '''

    def get_project_exists(self) -> bool:
        return self.project_exists
    
    def get_project_info(self) -> ExistingProjectProjectInfo:
        return self.project_info