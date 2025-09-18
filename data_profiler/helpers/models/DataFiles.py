'''
Jack Miller
Apex Companies
Oct 2024

Pydantic models relating to input/upload files for DataProfiler
'''

from pydantic import BaseModel
from enum import Enum

from typing import Union


class DataUploadType(str, Enum):
    REGULAR = 'Regular'
    HEADERS = 'Headers'

class UploadFileTypes(str, Enum):
    ITEM_MASTER = 'ItemMaster'
    INBOUND = 'Inbound'
    INBOUND_HEADER = 'InboundHeader'
    INBOUND_DETAILS = 'InboundDetails'
    INVENTORY = 'Inventory'
    OUTBOUND = 'Outbound'
    ORDER_HEADER = 'OrderHeader'
    ORDER_DETAILS = 'OrderDetails'
    SUBWHSE_UPDATE = 'SubwhseUpdate'
    ITEM_MASTER_UPDATE = 'ItemMasterUpdate'

class OtherFileTypes(str, Enum):
    SUBWHSE_UPDATE = 'SubwhseUpdate'

class UploadedFile(BaseModel):
    file_type: UploadFileTypes
    file_path: str

class UploadedFilePaths(BaseModel):
    item_master: str = ''
    inbound: str = ''
    inventory: str = ''
    outbound: str = ''
    
    inbound_header: str = ''
    inbound_details: str = ''
    order_header: str = ''
    order_details: str = ''


class FileValidation(BaseModel):
    file_type: UploadFileTypes
    file_path: str = ''
    is_present: bool = True
    is_valid: bool = True
    given_columns: list = []
    missing_columns: list = []
    invalid_columns: list = []


class DataDirectoryValidation(BaseModel):
    file_path: str
    data_upload_type: DataUploadType = DataUploadType.REGULAR
    given_files: list = []

    is_valid: bool = True
    errors_list: list = []

    item_master: FileValidation = FileValidation(file_type=UploadFileTypes.ITEM_MASTER)
    inbound: FileValidation = FileValidation(file_type=UploadFileTypes.INBOUND)
    inventory: FileValidation = FileValidation(file_type=UploadFileTypes.INVENTORY)
    outbound: FileValidation = FileValidation(file_type=UploadFileTypes.OUTBOUND)

    inbound_header: FileValidation = FileValidation(file_type=UploadFileTypes.INBOUND_HEADER)
    inbound_details: FileValidation = FileValidation(file_type=UploadFileTypes.INBOUND_DETAILS)
    order_header: FileValidation = FileValidation(file_type=UploadFileTypes.ORDER_HEADER)
    order_details: FileValidation = FileValidation(file_type=UploadFileTypes.ORDER_DETAILS)