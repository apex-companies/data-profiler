
from pydantic import BaseModel
from ..helpers.constants import UploadFileTypes



''' File Errors '''

DIRECTORY_ERROR_DOES_NOT_EXIST = 'The given data directory does not exist.'

FILE_ERROR_MISSING_ITEM_MASTER = 'Item Master is missing. Cannot continue.'
FILE_ERROR_INBOUND_NO_HEADER = 'Inbound Details was provided without Inbound Header.'
FILE_ERROR_INBOUND_NO_DETAILS = 'Inbound Header was provided without Inbound Details.'
FILE_ERROR_OUTBOUND_NO_HEADER = 'Outbound Details was provided without Outbound Header.'
FILE_ERROR_OUTBOUND_NO_DETAILS = 'Outbound Header was provided without Outbound Details.'

FILE_ERROR_ITEM_MASTER_MISSING_COLUMNS = 'Item Master is missing columns.'
FILE_ERROR_INBOUND_HEADER_MISSING_COLUMNS = 'Inbound Header is missing columns.'
FILE_ERROR_INBOUND_DETAILS_MISSING_COLUMNS = 'Inbound Details is missing columns.'
FILE_ERROR_INVENTORY_MISSING_COLUMNS = 'Inventory is missing columns.'
FILE_ERROR_ORDER_HEADER_MISSING_COLUMNS = 'Order Header is missing columns.'
FILE_ERROR_ORDER_DETAILS_MISSING_COLUMNS = 'Order Details is missing columns.'

''' Models '''

class FileValidation(BaseModel):
    file_type: UploadFileTypes
    file_path: str = ''
    is_present: bool = True
    is_valid: bool = True
    missing_columns: list = []


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