'''
Jack Miller
Apex Companies
Oct 2024

Some helpful pydantic models for relaying/returning information about database interactions
'''

from pydantic import BaseModel


''' Base '''

class BaseResponse(BaseModel):
    project_number: str

    success: bool = False
    message: str = ''
    log_file_path: str = ''

class BaseDBResponse(BaseResponse):
    rows_affected: int = 0


''' Various DB '''

class DBDownloadResponse(BaseDBResponse):    
    download_path: str = ''


''' Transform '''

class TransformRowsInserted(BaseModel):
    total_rows_inserted: int = 0
    skus: int = 0
    inbound_pos: int = 0
    inbound_lines: int = 0
    inventory_lines: int = 0
    outbound_lines: int = 0
    outbound_orders: int = 0

class TransformResponse(BaseResponse):
    rows_inserted: TransformRowsInserted = TransformRowsInserted()
