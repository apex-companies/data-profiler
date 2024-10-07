
from pydantic import BaseModel
from pprint import pprint
from data_profiler.models.Responses import TransformRowsInserted


rows = TransformRowsInserted(
    total_rows_inserted=1000,
    skus=100,
    inbound_receipts=55,
    inbound_lines=1039,
    inventory_lines=904,
    outbound_orders=657,
    outbound_lines=12034
)


def pretty_print_rows_inserted(rows: TransformRowsInserted):
    s = ''

    s += f'Total rows inserted: {rows.total_rows_inserted}\n'
    s += f'SKUs: {rows.skus}\n'
    s += f'Inbound Receipts: {rows.inbound_receipts}\n'
    s += f'Inbound Lines: {rows.inbound_lines}\n'
    s += f'Inventory Lines: {rows.inventory_lines}\n'
    s += f'Outbound Orders: {rows.outbound_orders}\n'
    s += f'Outbound Lines: {rows.outbound_lines}'

    return s

s = pretty_print_rows_inserted(rows)

m = f'Successful transform!\n\n{s}\n\nSee results in folder.'

print(m)