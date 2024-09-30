
from pydantic import BaseModel
from ..helpers.constants import UploadFileTypes


class FileValidation(BaseModel):
    file_type: UploadFileTypes
    file_path: str = ''
    is_present: bool = True
    is_valid: bool = True
    missing_columns: list = []


class DataDirectoryValidation(BaseModel):
    file_path: str
    is_valid: bool = True
    missing_files: list = []
    invalid_files: list = []
    item_master: FileValidation = FileValidation(file_type=UploadFileTypes.ITEM_MASTER)
    inbound_header: FileValidation = FileValidation(file_type=UploadFileTypes.INBOUND_HEADER)
    inbound_details: FileValidation = FileValidation(file_type=UploadFileTypes.INBOUND_DETAILS)
    inventory: FileValidation = FileValidation(file_type=UploadFileTypes.INVENTORY)
    order_header: FileValidation = FileValidation(file_type=UploadFileTypes.ORDER_HEADER)
    order_details: FileValidation = FileValidation(file_type=UploadFileTypes.ORDER_DETAILS)