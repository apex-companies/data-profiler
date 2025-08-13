'''
Jack Miller
Apex Companies
Oct 2024

Pydantic models relating to input/upload files for DataProfiler
'''

from pydantic import BaseModel
from enum import Enum

from typing import Union

class FileType(Enum):
# class FileType(BaseModel):
    BASE_FILE = 'BaseFile'

# class UploadFileTypes(FileType, Enum):
class UploadFileTypes(str, Enum):
    ITEM_MASTER = 'ItemMaster'
    INBOUND_HEADER = 'InboundHeader'
    INBOUND_DETAILS = 'InboundDetails'
    INVENTORY = 'Inventory'
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
    inbound_header: str = ''
    inbound_details: str = ''
    inventory: str = ''
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
    is_valid: bool = True
    given_files: list = []
    errors_list: list = []
    item_master: FileValidation = FileValidation(file_type=UploadFileTypes.ITEM_MASTER)
    inbound_header: FileValidation = FileValidation(file_type=UploadFileTypes.INBOUND_HEADER)
    inbound_details: FileValidation = FileValidation(file_type=UploadFileTypes.INBOUND_DETAILS)
    inventory: FileValidation = FileValidation(file_type=UploadFileTypes.INVENTORY)
    order_header: FileValidation = FileValidation(file_type=UploadFileTypes.ORDER_HEADER)
    order_details: FileValidation = FileValidation(file_type=UploadFileTypes.ORDER_DETAILS)