'''
Jack Miller
Apex Companies
Oct 2024

Main Python class for DataProfiler app logic. This class shouldn't interact directly with DB - hand off to Service classes for this
'''

# Python
import os
from io import TextIOWrapper
from time import time
from datetime import datetime, timedelta
import math
from pathlib import Path
from pprint import pprint

import pandas as pd
import pyodbc

# Data Profiler
from .helpers.models.ProjectInfo import BaseProjectInfo, ExistingProjectProjectInfo
from .helpers.models.TransformOptions import TransformOptions
from .helpers.models.Responses import DBWriteResponse, TransformResponse, DeleteResponse
from .helpers.models.DataFiles import DataDirectoryValidation, FileValidation, UploadFileTypes, UploadedFilePaths
from .helpers.constants.data_file_constants import UPLOADS_REQUIRED_COLUMNS_MAPPER, UPLOADS_REQUIRED_DTYPES_MAPPER,\
    DTYPES_DEFAULT_VALUES, DIRECTORY_ERROR_DOES_NOT_EXIST, FILE_ERROR_INBOUND_DETAILS_MISSING_COLUMNS,\
    FILE_ERROR_INBOUND_HEADER_MISSING_COLUMNS, FILE_ERROR_INVENTORY_MISSING_COLUMNS, FILE_ERROR_ITEM_MASTER_MISSING_COLUMNS,\
    FILE_ERROR_MISSING_ITEM_MASTER, FILE_ERROR_ORDER_DETAILS_MISSING_COLUMNS, FILE_ERROR_ORDER_HEADER_MISSING_COLUMNS,\
    FILE_ERROR_MISSING_INVENTORY, FILE_ERROR_MISSING_INBOUND_HEADER, FILE_ERROR_MISSING_INBOUND_DETAILS,\
    FILE_ERROR_MISSING_OUTBOUND_HEADER, FILE_ERROR_MISSING_OUTBOUND_DETAILS
from .helpers.functions.functions import file_path_is_valid_data_frame, data_frame_is_empty, validate_csv_column_names,\
    validate_primary_keys, check_mismatching_primary_key_values

from .services.output_tables_service import OutputTablesService
from .services.transform_service import TransformService



class DataProfiler:

    def __init__(self, project_number: str, dev: bool = False):
        
        # Instantiate variables
        self.project_number = project_number
        self.dev = dev

        self.outputs_dir = 'logs' if self.dev else Path.home() / 'Downloads'
        if not os.path.isdir(self.outputs_dir):
            self.outputs_dir = '.'

        self.project_exists = False
        self.project_info = None
        
        # If project exists, update relevant variables
        project_numbers = self.get_output_tables_projects()
        if project_number in set(project_numbers):
            self.project_exists = True
            self.refresh_project_info()
        

    ''' Main functions - Create, Read, Update, Delete (CRUD) '''

    ## Create ##

    def create_new_project(self, project_info: BaseProjectInfo) -> DBWriteResponse:
        '''
        Create new project row in Project table

        Return
        ------
        DBWriteResponse
        
        '''
        if self.get_project_exists():
            return 'Project already exists. Try updating it instead'
        
        response = DBWriteResponse()

        try:
            with OutputTablesService(dev=self.dev) as service:
                response.rows_affected = service.insert_new_project_to_project_table(project_info=project_info)

                if response.rows_affected == 1:
                    response.success = True
        
                    self.project_exists = True
                    self.refresh_project_info()
        except pyodbc.DatabaseError as e:
            response.success = False
            response.error_message = e

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


    ## Update ##

    def update_project_info(self, new_project_info: ExistingProjectProjectInfo) -> DBWriteResponse:
        if not self.get_project_exists():
            raise ValueError('Project does not yet exist')
        
        response = DBWriteResponse()

        try:
            with OutputTablesService(dev=self.dev) as service:
                response.rows_affected = service.update_project_in_project_table(new_project_info=new_project_info)

                if response.rows_affected == 1:
                    response.success = True

        except pyodbc.DatabaseError as e:
            response.success = False
            response.error_message = e

        self.refresh_project_info()

        return response

    def transform_and_upload_data(self, data_directory: str, transform_options: TransformOptions) -> TransformResponse:
        if not self.get_project_exists():
            raise ValueError('Project does not yet exist.')
        
        project_info = self.get_project_info()

        if project_info.data_uploaded:
            raise ValueError('Project already has data uploaded. If you would like to update project data, delete it and re-upload.')
        
        ## 1. Validate data directory ##
        data_directory_validation = self.validate_data_directory(data_directory=data_directory, transform_options=transform_options)
        pprint(data_directory_validation.model_dump())

        if not data_directory_validation.is_valid:
            errors_str = '\n\n'.join(data_directory_validation.errors_list)
            raise ValueError(f'Invalid data directory: {errors_str}')
        
        uploaded_files = UploadedFilePaths(
            item_master = data_directory_validation.item_master.file_path,
            inbound_header = data_directory_validation.inbound_header.file_path if transform_options.process_inbound_data else '',
            inbound_details = data_directory_validation.inbound_details.file_path if transform_options.process_inbound_data else '',
            inventory = data_directory_validation.inventory.file_path if transform_options.process_inventory_data else '',
            order_header = data_directory_validation.order_header.file_path if transform_options.process_outbound_data else '',
            order_details = data_directory_validation.order_details.file_path if transform_options.process_outbound_data else ''
        )
        
        ## 2. Read files ##
    
        # Create log file
        log_file_path = f'{self.get_outputs_dir()}/{project_info.project_number}-{datetime.now().strftime(format="%Y%m%d-%H.%M.%S")}_transform.txt'
        if self.dev:
            log_file_path = f'{os.getcwd()}/{log_file_path}'        # prepend full absolute path if in dev

        log_file = open(log_file_path, 'w+')
        log_file.write(f'PROJECT NUMBER: {project_info.project_number}\n\n')

        valid_data = True
        transform_response = TransformResponse(project_number=project_info.project_number, log_file_path=log_file_path)

        log_file.write(f'1. READ IN UPLOADED FILES\n')
        master_errors_dict = {}

        item_master = None
        inbound_header = None
        inbound_details = None
        inventory = None
        order_header = None
        order_details = None

        IM_SKUS = []
        IB_SKUS = []
        INV_SKUS = []
        OB_SKUS = []

        IBH_RECEIPTS = []
        IBD_RECEIPTS = []

        OBH_ORDERS = []
        OBD_ORDERS = []

        ## Read files (and cleanse along the way)
        
        # If item master isn't present, error will already have come up
        item_master, item_master_errors_list = self._read_and_cleanse_uploaded_data_file(file_type=UploadFileTypes.ITEM_MASTER, file_path=uploaded_files.item_master, log_file=log_file)
        print(item_master.head())
        print(f'Errors reading item master: {", ".join(item_master_errors_list)}')
        if (len(item_master_errors_list) > 0):
            valid_data = False
            master_errors_dict[UploadFileTypes.ITEM_MASTER.value] = item_master_errors_list
        IM_SKUS = item_master['SKU'].unique().tolist()

        if transform_options.process_inbound_data:
            inbound_header, inbound_header_errors_list = self._read_and_cleanse_uploaded_data_file(file_type=UploadFileTypes.INBOUND_HEADER, file_path=uploaded_files.inbound_header, log_file=log_file)
            print(inbound_header.head())
            print(f'Errors reading inbound header: {", ".join(inbound_header_errors_list)}')
            if len(inbound_header_errors_list) > 0:
                valid_data = False
                master_errors_dict[UploadFileTypes.INBOUND_HEADER.value] = inbound_header_errors_list

            inbound_details, inbound_details_errors_list = self._read_and_cleanse_uploaded_data_file(file_type=UploadFileTypes.INBOUND_DETAILS, file_path=uploaded_files.inbound_details, log_file=log_file)
            print(inbound_details.head())
            print(f'Errors reading inbound details: {", ".join(inbound_details_errors_list)}')
            if len(inbound_details_errors_list) > 0:
                valid_data = False
                master_errors_dict[UploadFileTypes.INBOUND_DETAILS.value] = inbound_details_errors_list

            IB_SKUS = inbound_details['SKU'].unique().tolist()
            IBH_RECEIPTS = inbound_header['ReceiptNumber'].unique().tolist()
            IBD_RECEIPTS = inbound_details['ReceiptNumber'].unique().tolist()

        if transform_options.process_inventory_data:
            inventory, inventory_errors_list = self._read_and_cleanse_uploaded_data_file(file_type=UploadFileTypes.INVENTORY, file_path=uploaded_files.inventory, log_file=log_file)
            print(inventory.head())
            print(f'Errors reading inventory: {", ".join(inventory_errors_list)}')
            if len(inventory_errors_list) > 0:
                valid_data = False
                master_errors_dict[UploadFileTypes.INVENTORY.value] = inventory_errors_list

            INV_SKUS = inventory['SKU'].unique().tolist()

        if transform_options.process_outbound_data:
            order_header, order_header_errors_list = self._read_and_cleanse_uploaded_data_file(file_type=UploadFileTypes.ORDER_HEADER, file_path=uploaded_files.order_header, log_file=log_file)
            print(order_header.head())
            print(f'Errors reading order header: {", ".join(order_header_errors_list)}')
            if len(order_header_errors_list) > 0:
                valid_data = False
                master_errors_dict[UploadFileTypes.ORDER_HEADER.value] = order_header_errors_list

            order_details, order_details_errors_list = self._read_and_cleanse_uploaded_data_file(file_type=UploadFileTypes.ORDER_DETAILS, file_path=uploaded_files.order_details, log_file=log_file)
            print(order_details.head())
            print(f'Errors reading order details: {", ".join(order_details_errors_list)}')
            if len(order_details_errors_list) > 0:
                valid_data = False
                master_errors_dict[UploadFileTypes.ORDER_DETAILS.value] = order_details_errors_list

            OB_SKUS = order_details['SKU'].unique().tolist()
            OBH_ORDERS = order_header['OrderNumber'].unique().tolist()
            OBD_ORDERS = order_details['OrderNumber'].unique().tolist()
            
        if not valid_data:
            log_file.write(f'\nCritical issues reading the data. Cannot continue.\n')
            log_file.close()

            transform_response.success = False
            transform_response.message = f'ERROR - Some critical issues reading the data. Check log.'

            return transform_response
        
        ## 3. Validate files once they're read ##

        # SKU Checks
        bad_im_skus = validate_primary_keys(IM_SKUS)

        if len(bad_im_skus) > 0:
            valid_data = False
            log_file.write(f'ERROR - Found {len(bad_im_skus)} erroneous Item Master SKUs\n')
            log_file.write(f'{bad_im_skus[:10]}...\n')

        bad_ib_skus = check_mismatching_primary_key_values(IM_SKUS, IB_SKUS)
        bad_inv_skus = check_mismatching_primary_key_values(IM_SKUS, INV_SKUS)
        bad_ob_skus = check_mismatching_primary_key_values(IM_SKUS, OB_SKUS)

        if len(bad_ib_skus) > 0:
            valid_data = False
            log_file.write(f'ERROR - {len(bad_ib_skus)} Inbound Details SKUs not in Item Master\n')
            log_file.write(f'{bad_ib_skus[:10]}...\n')
        
        if len(bad_inv_skus) > 0:
            valid_data = False
            log_file.write(f'ERROR - {len(bad_inv_skus)} Inventory SKUs not in Item Master\n')
            log_file.write(f'{bad_inv_skus[:10]}...\n')

        if len(bad_ob_skus) > 0:
            valid_data = False
            log_file.write(f'ERROR - {len(bad_ob_skus)} Order Details SKUs not in Item Master\n')
            log_file.write(f'{bad_ob_skus[:10]}...\n')

        # Receipt/Order Number Checks
        bad_receipt_numbers = validate_primary_keys(IBH_RECEIPTS)
        bad_order_numbers = validate_primary_keys(OBH_ORDERS)

        if len(bad_receipt_numbers) > 0:
            valid_data = False
            log_file.write(f'ERROR - Found {len(bad_receipt_numbers)} erroneous Inbound Header receipt numbers\n')
            log_file.write(f'{bad_receipt_numbers[:10]}...\n')

        if len(bad_order_numbers) > 0:
            valid_data = False
            log_file.write(f'ERROR - Found {len(bad_order_numbers)} erroneous Order Header order numbers\n')
            log_file.write(f'{bad_order_numbers[:10]}...\n')

        bad_ibd_receipts = check_mismatching_primary_key_values(IBH_RECEIPTS, IBD_RECEIPTS)
        bad_obd_receipts = check_mismatching_primary_key_values(OBH_ORDERS, OBD_ORDERS)
        
        if len(bad_ibd_receipts) > 0:
            valid_data = False
            log_file.write(f'ERROR - {len(bad_ibd_receipts)} Inbound Details receipt numbers not in Inbound Header\n')
            log_file.write(f'{bad_ibd_receipts[:10]}...\n')

        if len(bad_obd_receipts) > 0:
            valid_data = False
            log_file.write(f'ERROR - {len(bad_obd_receipts)} Order Details order numbers not in Order Header\n')
            log_file.write(f'{bad_obd_receipts[:10]}...\n')

        if not valid_data:
            log_file.write(f'\nSome primary/foreign key issues. Cannot continue.\n')
            log_file.close()

            transform_response.success = False
            transform_response.message = f'ERROR - Found some primary/foreign key issues. Cannot continue. Check log.'

            return transform_response

        ## 4. Transform and persist data ##

        transform_st = time()
        print('Transforming...')
    
        transform_response = None
        with TransformService(project_number=project_info.project_number, transform_options=transform_options, dev=self.dev) as service:
            transform_response = service.transform_and_persist_dataframes(item_master_df=item_master, inbound_header_df=inbound_header, inbound_details_df=inbound_details,
                                                            inventory_df=inventory, order_header_df=order_header, order_details_df=order_details,
                                                            log_file=log_file)

        transform_response.log_file_path = log_file_path

        transform_et = time()
        print(f'Total transform time: {timedelta(seconds=transform_et-transform_st)}')

        # If unsuccessful, delete any rows that were inserted
        if not transform_response.success:
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

    def delete_project_data(self, log_file: TextIOWrapper | None = None) -> DeleteResponse:
        if not self.get_project_exists():
            raise ValueError('Project does not yet exist')
        
        project_info = self.get_project_info()

        # Start log file
        log_file_given = (log_file != None)
        log_file_path = ''
        if not log_file_given:
            log_file_path = f'{self.get_outputs_dir()}/{project_info.project_number}-{datetime.now().strftime(format="%Y%m%d-%H.%M.%S")}_delete_from_output_tables.txt'
            if self.dev:
                log_file_path = f'{os.getcwd()}/{log_file_path}'

            log_file = open(log_file_path, 'w+')
            log_file.write(f'PROJECT NUMBER: {project_info.project_number}\n\n')

        # Try delete
        response = None
        with OutputTablesService(dev=self.dev) as service:
            response = service.delete_project_data(project_number=project_info.project_number, log_file=log_file)
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
    
    def delete_project(self) -> DBWriteResponse:
        if not self.get_project_exists():
            raise ValueError('Project does not yet exist')
        
        project_info = self.get_project_info()

        if project_info.data_uploaded:
            raise ValueError('Please delete project data before deleting project.')
        
        # Try delete
        response = DBWriteResponse()
        try:
            with OutputTablesService(dev=self.dev) as service:
                response.rows_affected = service.delete_project(project_number=project_info.project_number)

                if response.rows_affected == 1:
                        response.success = True

        except pyodbc.DatabaseError as e:
            response.success = False
            response.error_message = e
        
        return response


    ''' Main Functions - Validation '''

    def validate_data_directory(self, data_directory: str, transform_options: TransformOptions) -> DataDirectoryValidation: 
        '''
        Validates a data directory. 

        Valid data directory =  
            1) All files are present  
            2) those files have all required column headers
        '''

        validation_obj = DataDirectoryValidation(file_path=data_directory)
        
        if not os.path.isdir(data_directory):
            validation_obj.errors_list.append(DIRECTORY_ERROR_DOES_NOT_EXIST)
            validation_obj.is_valid = False

            return validation_obj

        validation_obj.item_master = self._validate_file(data_directory=data_directory, file_type=UploadFileTypes.ITEM_MASTER)
        validation_obj.inbound_header = self._validate_file(data_directory=data_directory, file_type=UploadFileTypes.INBOUND_HEADER)
        validation_obj.inbound_details = self._validate_file(data_directory=data_directory, file_type=UploadFileTypes.INBOUND_DETAILS)
        validation_obj.inventory = self._validate_file(data_directory=data_directory, file_type=UploadFileTypes.INVENTORY)
        validation_obj.order_header = self._validate_file(data_directory=data_directory, file_type=UploadFileTypes.ORDER_HEADER)
        validation_obj.order_details = self._validate_file(data_directory=data_directory, file_type=UploadFileTypes.ORDER_DETAILS)
                
        # Item Master
        if validation_obj.item_master.is_present:
            validation_obj.given_files.append(UploadFileTypes.ITEM_MASTER.value)

            if len(validation_obj.item_master.missing_columns) > 0:
                error = f'{FILE_ERROR_ITEM_MASTER_MISSING_COLUMNS}\n[{", ".join(validation_obj.item_master.missing_columns)}]'
                validation_obj.errors_list.append(error)
        else:
            validation_obj.errors_list.append(FILE_ERROR_MISSING_ITEM_MASTER)

        if transform_options.process_inbound_data:
            # Inbound Header
            if validation_obj.inbound_header.is_present:
                validation_obj.given_files.append(UploadFileTypes.INBOUND_HEADER.value)

                if len(validation_obj.inbound_header.missing_columns) > 0:
                    error = f'{FILE_ERROR_INBOUND_HEADER_MISSING_COLUMNS}\n[{", ".join(validation_obj.inbound_header.missing_columns)}]'
                    validation_obj.errors_list.append(error)
            else:
                validation_obj.errors_list.append(FILE_ERROR_MISSING_INBOUND_HEADER)

            # Inbound Details
            if validation_obj.inbound_details.is_present:
                validation_obj.given_files.append(UploadFileTypes.INBOUND_DETAILS.value)

                if len(validation_obj.inbound_details.missing_columns) > 0:
                    error = f'{FILE_ERROR_INBOUND_DETAILS_MISSING_COLUMNS}\n[{", ".join(validation_obj.inbound_details.missing_columns)}]'
                    validation_obj.errors_list.append(error)
            else:
                validation_obj.errors_list.append(FILE_ERROR_MISSING_INBOUND_DETAILS)

        if transform_options.process_inventory_data:
            # Inventory
            if validation_obj.inventory.is_present:
                validation_obj.given_files.append(UploadFileTypes.INVENTORY.value)

                if len(validation_obj.inventory.missing_columns) > 0:
                    error = f'{FILE_ERROR_INVENTORY_MISSING_COLUMNS}\n[{", ".join(validation_obj.inventory.missing_columns)}]'
                    validation_obj.errors_list.append(error)
            else:
                validation_obj.errors_list.append(FILE_ERROR_MISSING_INVENTORY)

        if transform_options.process_outbound_data:
            # Order Header
            if validation_obj.order_header.is_present:
                validation_obj.given_files.append(UploadFileTypes.ORDER_HEADER.value)

                if len(validation_obj.order_header.missing_columns) > 0:
                    error = f'{FILE_ERROR_ORDER_HEADER_MISSING_COLUMNS}\n[{", ".join(validation_obj.order_header.missing_columns)}]'
                    validation_obj.errors_list.append(error)
            else:
                validation_obj.errors_list.append(FILE_ERROR_MISSING_OUTBOUND_HEADER)

            # Order Details
            if validation_obj.order_details.is_present:
                validation_obj.given_files.append(UploadFileTypes.ORDER_DETAILS.value)

                if len(validation_obj.order_details.missing_columns) > 0:
                    error = f'{FILE_ERROR_ORDER_DETAILS_MISSING_COLUMNS}\n[{", ".join(validation_obj.order_details.missing_columns)}]'
                    validation_obj.errors_list.append(error)
            else:
                validation_obj.errors_list.append(FILE_ERROR_MISSING_OUTBOUND_DETAILS)

        if len(validation_obj.errors_list) > 0:
            validation_obj.is_valid = False
            
        return validation_obj
    
    def _validate_file(self, data_directory: str, file_type: UploadFileTypes) -> FileValidation:
        validation_obj = FileValidation(file_type=file_type, file_path=f'{data_directory}/{file_type.value}.csv')

        # Is it present?
        if not os.path.exists(validation_obj.file_path) or os.stat(validation_obj.file_path).st_size == 0:
            validation_obj.is_present = False
            validation_obj.is_valid = False
            validation_obj.file_path = ''
            return validation_obj
        else:
            validation_obj.is_present = True

        # Is it valid?
        if not file_path_is_valid_data_frame(validation_obj.file_path):
            validation_obj.is_valid = False
            return validation_obj
        
        missing_cols = validate_csv_column_names(file_path=validation_obj.file_path, columns=UPLOADS_REQUIRED_COLUMNS_MAPPER[file_type.value])
        if missing_cols:
            validation_obj.is_valid = False
            validation_obj.missing_columns = missing_cols
            return validation_obj

        # Is dataframe empty?
        if data_frame_is_empty(file_path=validation_obj.file_path):     # Empty = headers present but no row data
            validation_obj.is_present = False
            return validation_obj
        
        # Otherwise, it's valid
        return validation_obj


    ''' Main Function - Read & Cleanse data '''

    def _read_and_cleanse_uploaded_data_file(self, file_type: UploadFileTypes, file_path: str, log_file: TextIOWrapper) -> tuple[pd.DataFrame, list]:

        ''' 
        Reads given file and returns a cleansed dataframe. Converts column types to match database and re-order columns. Finds type errors now before attempting DB transactions.

        Return
        ------
        pd.DataFrame
        '''

        log_file.write(f'Reading {file_type.value}\n')

        dtypes = UPLOADS_REQUIRED_DTYPES_MAPPER[file_type.value]

        df = pd.read_csv(file_path)
        log_file.write(f'Shape: {df.shape}\n')

        errors_encountered = 0
        errors_list = []
        for col, dtype in dtypes.items():
            try:
                rows_to_fill = 0
                default_val = DTYPES_DEFAULT_VALUES[dtype]

                if dtype == 'date':
                    df[col] = pd.to_datetime(df[col], dayfirst=True, format='mixed', errors='coerce')
                elif dtype == 'time':
                    df[col] = pd.to_datetime(df[col], format='%H:%M:%S', errors='coerce')
                elif dtype == 'float64' or dtype == 'int64':
                    df[col] = pd.to_numeric(df[col], errors='coerce')
                elif dtype == 'object':
                    df[col] = df[col].astype("string")
                
                rows_to_fill = len(df.loc[df[col].isna(), :])
                df[col] = df[col].replace(to_replace=math.nan, value=default_val)
                
                if rows_to_fill > 0:
                    log_file.write(f'{col} - replacing erroneous cells with default value "{default_val}" to {rows_to_fill} rows\n')

            except Exception as e:
                log_file.write(f'ERROR - Could not convert field "{col}" to correct type {dtype}: {e}\n')
                print(f'ERROR converting field "{col}" to correct type: {e}\n')
                errors_list.append(e)
                errors_encountered += 1

        if errors_encountered > 0:
            log_file.write(f'{errors_encountered} error(s) encountered converting to correct dtypes.\n\n')
            print(f'{errors_encountered} error(s) encountered converting to correct dtypes. Quitting before DB insertion.')
        else:
            log_file.write(f'Dtype conversions successful.\n\n')
            print(f'Dtype conversions successful.')

        # Reindex for consistent column order
        df = df.reindex(columns=dtypes.keys())

        return df, errors_list


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