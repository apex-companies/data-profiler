

from pydantic import BaseModel


class TransformRowsInserted(BaseModel):
    total_rows_inserted: int = 0
    skus: int = 0
    inbound_receipts: int = 0
    inbound_lines: int = 0
    inventory_lines: int = 0
    outbound_lines: int = 0
    outbound_orders: int = 0

class TransformResponse(BaseModel):
    project_number: str
    success: bool = False
    message: str = ''
    rows_inserted: TransformRowsInserted = TransformRowsInserted()

