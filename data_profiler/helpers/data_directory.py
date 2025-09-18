'''
Jack Miller
Apex Companies
Sep 2025
'''

from typing import Callable
import os
from io import TextIOWrapper
import pandas as pd

from ..helpers.functions.functions import validate_primary_keys, check_mismatching_primary_key_values
from ..helpers.functions.data_file_functions import validate_file_structure, read_and_cleanse_uploaded_data_file
from ..helpers.constants.data_file_constants import *

from .models.DataFiles import DataDirectoryType, DataDirectoryValidation, UploadFileType, FileValidation
from .models.TransformOptions import TransformOptions



class DataDirectory:
    '''
    Used to track the contents and validity of a data directory for data uploads
    '''

    def __init__(self, path: str, transform_options: TransformOptions, update_progress_text_func: Callable[[str], None] = None):
        self.path = path
        self.directory_type = transform_options.data_directory_type
        self.transform_options = transform_options
        self.update_progress_text_func = update_progress_text_func

        self.validation_obj = DataDirectoryValidation(file_path=self.path)

        self.item_master = None
        self.inbound_header = None
        self.inbound_details = None
        self.inventory = None
        self.order_header = None
        self.order_details = None

    ''' Main Functions '''

    def validate_directory(self) -> DataDirectoryValidation: 
        '''
        Validates a data directory. 

        Valid data directory =  
            1) All files are present  
            2) those files have all required column headers
        '''
        
        if not os.path.isdir(self.path):
            self.validation_obj.errors_list.append(DIRECTORY_ERROR_DOES_NOT_EXIST)
            self.validation_obj.is_valid = False

            return self.validation_obj

        self.validation_obj.data_directory_type = self.directory_type

        ## Item Master

        # Validate contents
        self.validation_obj.item_master = self._validate_file_structure(file_type=UploadFileType.ITEM_MASTER)

        # Error strings
        if self.validation_obj.item_master.is_present:
            self.validation_obj.given_files.append(UploadFileType.ITEM_MASTER.value)

            if len(self.validation_obj.item_master.missing_columns) > 0:
                error = f'{FILE_ERROR_ITEM_MASTER_MISSING_COLUMNS}\n[{", ".join(self.validation_obj.item_master.missing_columns)}]'
                self.validation_obj.errors_list.append(error)
        else:
            self.validation_obj.errors_list.append(FILE_ERROR_MISSING_ITEM_MASTER)

        ## Inbound
        if self.transform_options.process_inbound_data:            
            if self.directory_type == DataDirectoryType.REGULAR:
                # Validate contents
                self.validation_obj.inbound = self._validate_file_structure(file_type=UploadFileType.INBOUND)

                # Error strings
                if self.validation_obj.inbound.is_present:
                    self.validation_obj.given_files.append(UploadFileType.INBOUND.value)

                    if len(self.validation_obj.inbound.missing_columns) > 0:
                        error = f'{FILE_ERROR_INBOUND_MISSING_COLUMNS}\n[{", ".join(self.validation_obj.inbound.missing_columns)}]'
                        self.validation_obj.errors_list.append(error)
                else:
                    self.validation_obj.errors_list.append(FILE_ERROR_MISSING_INBOUND)  

            else:
                # Validate contents
                self.validation_obj.inbound_header = self._validate_file_structure(file_type=UploadFileType.INBOUND_HEADER)
                self.validation_obj.inbound_details = self._validate_file_structure(file_type=UploadFileType.INBOUND_DETAILS)

                # Error strings
                if self.validation_obj.inbound_header.is_present:
                    self.validation_obj.given_files.append(UploadFileType.INBOUND_HEADER.value)

                    if len(self.validation_obj.inbound_header.missing_columns) > 0:
                        error = f'{FILE_ERROR_INBOUND_HEADER_MISSING_COLUMNS}\n[{", ".join(self.validation_obj.inbound_header.missing_columns)}]'
                        self.validation_obj.errors_list.append(error)
                else:
                    self.validation_obj.errors_list.append(FILE_ERROR_MISSING_INBOUND_HEADER)

                # Inbound Details
                if self.validation_obj.inbound_details.is_present:
                    self.validation_obj.given_files.append(UploadFileType.INBOUND_DETAILS.value)

                    if len(self.validation_obj.inbound_details.missing_columns) > 0:
                        error = f'{FILE_ERROR_INBOUND_DETAILS_MISSING_COLUMNS}\n[{", ".join(self.validation_obj.inbound_details.missing_columns)}]'
                        self.validation_obj.errors_list.append(error)
                else:
                    self.validation_obj.errors_list.append(FILE_ERROR_MISSING_INBOUND_DETAILS)

        ## Inventory
        if self.transform_options.process_inventory_data:
            # Validate contents
            self.validation_obj.inventory = self._validate_file_structure(file_type=UploadFileType.INVENTORY)
            
            # Error strings
            if self.validation_obj.inventory.is_present:
                self.validation_obj.given_files.append(UploadFileType.INVENTORY.value)

                if len(self.validation_obj.inventory.missing_columns) > 0:
                    error = f'{FILE_ERROR_INVENTORY_MISSING_COLUMNS}\n[{", ".join(self.validation_obj.inventory.missing_columns)}]'
                    self.validation_obj.errors_list.append(error)
            else:
                self.validation_obj.errors_list.append(FILE_ERROR_MISSING_INVENTORY)

        ## Outbound
        if self.transform_options.process_outbound_data:
            if self.directory_type == DataDirectoryType.REGULAR:
                # Validate contents
                self.validation_obj.outbound = self._validate_file_structure(file_type=UploadFileType.OUTBOUND)

                # Error strings
                if self.validation_obj.outbound.is_present:
                    self.validation_obj.given_files.append(UploadFileType.OUTBOUND.value)

                    if len(self.validation_obj.outbound.missing_columns) > 0:
                        error = f'{FILE_ERROR_OUTBOUND_MISSING_COLUMNS}\n[{", ".join(self.validation_obj.outbound.missing_columns)}]'
                        self.validation_obj.errors_list.append(error)
                else:
                    self.validation_obj.errors_list.append(FILE_ERROR_MISSING_OUTBOUND)  
            else:    
                # Validate contents
                self.validation_obj.order_header = self._validate_file_structure(file_type=UploadFileType.ORDER_HEADER)
                self.validation_obj.order_details = self._validate_file_structure(file_type=UploadFileType.ORDER_DETAILS)
                    
                # Error strings
                if self.validation_obj.order_header.is_present:
                    self.validation_obj.given_files.append(UploadFileType.ORDER_HEADER.value)

                    if len(self.validation_obj.order_header.missing_columns) > 0:
                        error = f'{FILE_ERROR_ORDER_HEADER_MISSING_COLUMNS}\n[{", ".join(self.validation_obj.order_header.missing_columns)}]'
                        self.validation_obj.errors_list.append(error)
                else:
                    self.validation_obj.errors_list.append(FILE_ERROR_MISSING_OUTBOUND_HEADER)

                # Order Details
                if self.validation_obj.order_details.is_present:
                    self.validation_obj.given_files.append(UploadFileType.ORDER_DETAILS.value)

                    if len(self.validation_obj.order_details.missing_columns) > 0:
                        error = f'{FILE_ERROR_ORDER_DETAILS_MISSING_COLUMNS}\n[{", ".join(self.validation_obj.order_details.missing_columns)}]'
                        self.validation_obj.errors_list.append(error)
                else:
                    self.validation_obj.errors_list.append(FILE_ERROR_MISSING_OUTBOUND_DETAILS)

        if len(self.validation_obj.errors_list) > 0:
            self.validation_obj.is_valid = False
            
        return self.validation_obj
    
    def read_and_validate_file_contents(self, log_file: TextIOWrapper) -> tuple[bool, str]:
        '''
        Read files
        '''
        
        if self.update_progress_text_func: self.update_progress_text_func('Reading data...')

        ## Start
        
        log_file.write(f'1. READ IN UPLOADED FILES\n')
        log_file.flush()

        # Variables
        valid_data = True

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
        item_master, item_master_errors_list = read_and_cleanse_uploaded_data_file(file_type=UploadFileType.ITEM_MASTER, file_path=self.validation_obj.item_master.file_path, log_file=log_file)
        print(item_master.head())
        print(f'Errors reading item master: {", ".join(item_master_errors_list)}')
        if (len(item_master_errors_list) > 0):
            valid_data = False
            master_errors_dict[UploadFileType.ITEM_MASTER.value] = item_master_errors_list
        IM_SKUS = item_master['SKU'].unique().tolist()

        if self.transform_options.process_inbound_data:
            if self.directory_type == DataDirectoryType.REGULAR:
                inbound, inbound_errors_list = read_and_cleanse_uploaded_data_file(file_type=UploadFileType.INBOUND, file_path=self.validation_obj.inbound.file_path, log_file=log_file)
                print(inbound.head())
                print(f'Errors reading inbound: {", ".join(inbound_errors_list)}')
                if len(inbound_errors_list) > 0:
                    valid_data = False
                    master_errors_dict[UploadFileType.INBOUND.value] = inbound_errors_list

                IB_SKUS = inbound['SKU'].unique().tolist()

            else:
                inbound_header, inbound_header_errors_list = read_and_cleanse_uploaded_data_file(file_type=UploadFileType.INBOUND_HEADER, file_path=self.validation_obj.inbound_header.file_path, log_file=log_file)
                print(inbound_header.head())
                print(f'Errors reading inbound header: {", ".join(inbound_header_errors_list)}')
                if len(inbound_header_errors_list) > 0:
                    valid_data = False
                    master_errors_dict[UploadFileType.INBOUND_HEADER.value] = inbound_header_errors_list

                inbound_details, inbound_details_errors_list = read_and_cleanse_uploaded_data_file(file_type=UploadFileType.INBOUND_DETAILS, file_path=self.validation_obj.inbound_details.file_path, log_file=log_file)
                print(inbound_details.head())
                print(f'Errors reading inbound details: {", ".join(inbound_details_errors_list)}')
                if len(inbound_details_errors_list) > 0:
                    valid_data = False
                    master_errors_dict[UploadFileType.INBOUND_DETAILS.value] = inbound_details_errors_list

                IB_SKUS = inbound_details['SKU'].unique().tolist()
                IBH_RECEIPTS = inbound_header['PO_Number'].unique().tolist()
                IBD_RECEIPTS = inbound_details['PO_Number'].unique().tolist()

        if self.transform_options.process_inventory_data:
            inventory, inventory_errors_list = read_and_cleanse_uploaded_data_file(file_type=UploadFileType.INVENTORY, file_path=self.validation_obj.inventory.file_path, log_file=log_file)
            print(inventory.head())
            print(f'Errors reading inventory: {", ".join(inventory_errors_list)}')
            if len(inventory_errors_list) > 0:
                valid_data = False
                master_errors_dict[UploadFileType.INVENTORY.value] = inventory_errors_list

            INV_SKUS = inventory['SKU'].unique().tolist()

        if self.transform_options.process_outbound_data:
            if self.directory_type == DataDirectoryType.REGULAR:
                outbound, outbound_errors_list = read_and_cleanse_uploaded_data_file(file_type=UploadFileType.OUTBOUND, file_path=self.validation_obj.outbound.file_path, log_file=log_file)
                print(outbound.head())
                print(f'Errors reading outbound: {", ".join(outbound_errors_list)}')
                if len(outbound_errors_list) > 0:
                    valid_data = False
                    master_errors_dict[UploadFileType.OUTBOUND.value] = outbound_errors_list
                    
                OB_SKUS = outbound['SKU'].unique().tolist()

            else:
                order_header, order_header_errors_list = read_and_cleanse_uploaded_data_file(file_type=UploadFileType.ORDER_HEADER, file_path=self.validation_obj.order_header.file_path, log_file=log_file)
                print(order_header.head())
                print(f'Errors reading order header: {", ".join(order_header_errors_list)}')
                if len(order_header_errors_list) > 0:
                    valid_data = False
                    master_errors_dict[UploadFileType.ORDER_HEADER.value] = order_header_errors_list

                order_details, order_details_errors_list = read_and_cleanse_uploaded_data_file(file_type=UploadFileType.ORDER_DETAILS, file_path=self.validation_obj.order_details.file_path, log_file=log_file)
                print(order_details.head())
                print(f'Errors reading order details: {", ".join(order_details_errors_list)}')
                if len(order_details_errors_list) > 0:
                    valid_data = False
                    master_errors_dict[UploadFileType.ORDER_DETAILS.value] = order_details_errors_list

                OB_SKUS = order_details['SKU'].unique().tolist()
                OBH_ORDERS = order_header['OrderNumber'].unique().tolist()
                OBD_ORDERS = order_details['OrderNumber'].unique().tolist()
            
        if not valid_data:
            log_file.write(f'\nCritical issues reading the data. Cannot continue.\n')
            log_file.close()

            return False, f'ERROR - Some critical issues reading the data. Check log.'
        

        ## Validate files once they're read ##

        if self.update_progress_text_func: self.update_progress_text_func('Validating file contents...')

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
            log_file.write(f'ERROR - {len(bad_ib_skus)} Inbound{" Details" if self.directory_type == DataDirectoryType.HEADERS else ""} SKUs not in Item Master\n')
            log_file.write(f'{bad_ib_skus[:10]}...\n')
        
        if len(bad_inv_skus) > 0:
            valid_data = False
            log_file.write(f'ERROR - {len(bad_inv_skus)} Inventory SKUs not in Item Master\n')
            log_file.write(f'{bad_inv_skus[:10]}...\n')

        if len(bad_ob_skus) > 0:
            valid_data = False
            log_file.write(f'ERROR - {len(bad_ob_skus)} {"Order Details" if self.directory_type == DataDirectoryType.HEADERS else "Outbound"} SKUs not in Item Master\n')
            log_file.write(f'{bad_ob_skus[:10]}...\n')

        # Receipt/Order Number Checks
        if self.directory_type == DataDirectoryType.HEADERS:
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

            return False, f'ERROR - Found some primary/foreign key issues. Cannot continue. Check log.'
        
        ## Split to header / details if necessary
        if self.directory_type == DataDirectoryType.REGULAR:
            # Get headers
            inbound_header = self._get_header_from_inbound_df(inbound_df=inbound)
            order_header = self._get_header_from_outbound_df(outbound_df=outbound)

            # Reindex
            inbound_header = inbound_header.reindex(columns=FILE_TYPES_COLUMNS_MAPPER[UploadFileType.INBOUND_HEADER.value])
            inbound_details = inbound.reindex(columns=FILE_TYPES_COLUMNS_MAPPER[UploadFileType.INBOUND_DETAILS.value])
            order_header = order_header.reindex(columns=FILE_TYPES_COLUMNS_MAPPER[UploadFileType.ORDER_HEADER.value])
            order_details = outbound.reindex(columns=FILE_TYPES_COLUMNS_MAPPER[UploadFileType.ORDER_DETAILS.value])
        
        ## Save dataframes
        self.item_master = item_master
        self.inbound_header = inbound_header
        self.inbound_details = inbound_details
        self.inventory = inventory
        self.order_header = order_header
        self.order_details = order_details

        log_file.flush()

        return True, ''

    def get_df(self, file_type: UploadFileType):
        match file_type:
            case UploadFileType.ITEM_MASTER:
                return self.item_master
            case UploadFileType.INBOUND_HEADER:
                return self.inbound_header
            case UploadFileType.INBOUND_DETAILS:
                return self.inbound_details
            case UploadFileType.INVENTORY:
                return self.inventory
            case UploadFileType.ORDER_HEADER:
                return self.order_header
            case UploadFileType.ORDER_DETAILS:
                return self.order_details


    ''' Helper Functions '''

    def _validate_file_structure(self, file_type: UploadFileType) -> FileValidation:
        file_path = f'{self.path}/{file_type.value}.csv'
        required_columns = FILE_TYPES_COLUMNS_MAPPER[file_type.value]
        print(required_columns)
        
        return validate_file_structure(file_type=file_type, file_path=file_path, required_columns=required_columns)

    def _get_header_from_inbound_df(self, inbound_df: pd.DataFrame):
        inbound_header = inbound_df.groupby('PO_Number').aggregate({
            'ArrivalDate': 'first', 
            'ArrivalTime': 'first',
            'ExpectedDate': 'first', 
            'ExpectedTime': 'first', 
            'Carrier': 'first', 
            'Mode': 'first',
            'ShipmentNumber': 'first', 
            'UnloadType': 'first'
        }).reset_index()

        return inbound_header

    def _get_header_from_outbound_df(self, outbound_df: pd.DataFrame):
        order_header = outbound_df.groupby('OrderNumber').aggregate({
            'ReceivedDate': 'first',
            'PickDate': 'first',
            'ShipDate': 'first',
            'Channel': 'first'
        }).reset_index()
        
        return order_header