'''
Jack Miller
Apex Companies
Oct 2024

Some helpful pydantic models for relaying/returning information about database interactions
'''

from pydantic import BaseModel


class TransformRowsInserted(BaseModel):
    total_rows_inserted: int = 0
    skus: int = 0
    inbound_pos: int = 0
    inbound_lines: int = 0
    inventory_lines: int = 0
    outbound_lines: int = 0
    outbound_orders: int = 0


class TransformResponse(BaseModel):
    project_number: str
    success: bool = False
    message: str = ''
    rows_inserted: TransformRowsInserted = TransformRowsInserted()
    log_file_path: str = ''


class DeleteResponse(BaseModel):
    project_number: str
    success: bool = True
    errors_encountered: list = []
    rows_deleted: int = 0
    log_file_path: str = ''


class DBWriteResponse(BaseModel):
    success: bool = False
    rows_affected: int = 0
    error_message: str = ''


