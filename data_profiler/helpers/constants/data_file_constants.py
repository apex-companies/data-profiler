'''
Jack Miller
Apex Companies
Oct 2024

Python constants relating to input/upload files for DataProfiler
'''


''' Required Columns '''

ITEM_MASTER_UPLOAD_REQUIRED_COLS = ['SKU','SKUDescription','SKUClass','UnitOfMeasure','EachLength','EachWidth','EachHeight','EachWeight','InnerQuantity','InnerLength','InnerWidth','InnerHeight','InnerWeight','CartonQuantity','CartonLength','CartonWidth','CartonHeight','CartonWeight','CartonsPerPallet','PalletTie','PalletHigh','MaxPalletStack','PalletLength','PalletWidth','PalletHeight','PalletWeight','Conveyable','Subwarehouse','AllowToPickPallet','AllowToPickCarton','AllowToPickInnerPacks','AllowToPickUnits']
INBOUND_HEADER_UPLOAD_REQUIRED_COLS = ['PO_Number', 'ArrivalDate', 'ArrivalTime', 'ExpectedDate', 'ExpectedTime', 'Carrier', 'Mode', 'ShipmentNumber', 'UnloadType']
INBOUND_DETAILS_UPLOAD_REQUIRED_COLS = ['PO_Number', 'SKU', 'UnitOfMeasure', 'Quantity', 'VendorID', 'SourcePoint']
INVENTORY_UPLOAD_REQUIRED_COLS = ['Period','SKU','Quantity','UnitOfMeasure','Location','Lot','Subwarehouse']
ORDER_HEADER_UPLOAD_REQUIRED_COLS = ['OrderNumber','ReceivedDate','PickDate','ShipDate','Channel']
ORDER_DETAILS_UPLOAD_REQUIRED_COLS = ['OrderNumber','SKU', 'UnitOfMeasure', 'PickType', 'Quantity', 'BusinessUnit', 'ShipContainerType', 'SpecialHandlingCodes', 'Carrier']

UPLOADS_REQUIRED_COLUMNS_MAPPER = {
    'ItemMaster': ITEM_MASTER_UPLOAD_REQUIRED_COLS,
    'InboundHeader': INBOUND_HEADER_UPLOAD_REQUIRED_COLS,
    'InboundDetails': INBOUND_DETAILS_UPLOAD_REQUIRED_COLS,
    'Inventory': INVENTORY_UPLOAD_REQUIRED_COLS,
    'OrderHeader': ORDER_HEADER_UPLOAD_REQUIRED_COLS,
    'OrderDetails': ORDER_DETAILS_UPLOAD_REQUIRED_COLS
}


''' Required column types '''

ITEM_MASTER_UPLOAD_REQUIRED_DTYPES = {
    'SKU':'object',
    'SKUDescription':'object',
    'SKUClass':'object',
    'UnitOfMeasure':'object',
    'EachLength':'float64',
    'EachWidth':'float64',
    'EachHeight':'float64',
    'EachWeight':'float64',
    'InnerQuantity':'int64',
    'InnerLength':'float64',
    'InnerWidth':'float64',
    'InnerHeight':'float64',
    'InnerWeight':'float64',
    'CartonQuantity':'int64',
    'CartonLength':'float64',
    'CartonWidth':'float64',
    'CartonHeight':'float64',
    'CartonWeight':'float64',
    'CartonsPerPallet':'int64',
    'PalletTie':'int64',
    'PalletHigh':'int64',
    'MaxPalletStack': 'int64',
    'PalletLength':'float64',
    'PalletWidth':'float64',
    'PalletHeight':'float64',
    'PalletWeight':'float64',
    'Subwarehouse':'object'
}

INBOUND_HEADER_UPLOAD_REQUIRED_DTYPES = {
    'PO_Number': 'object',
    'ArrivalDate': 'date', 
    'ArrivalTime': 'time' , 
    'ExpectedDate': 'date', 
    'ExpectedTime': 'time', 
    'Carrier': 'object', 
    'Mode': 'object',
    'ShipmentNumber': 'object',
    'UnloadType': 'object'
}

INBOUND_DETAILS_UPLOAD_REQUIRED_DTYPES = {
    'PO_Number': 'object', 
    'SKU': 'object', 
    'UnitOfMeasure': 'object', 
    'Quantity': 'float64', 
    'VendorID': 'object', 
    'SourcePoint': 'object'
}

INVENTORY_UPLOAD_REQUIRED_DTYPES = {
    'Period':'date',
    'SKU':'object',
    'Quantity':'int64',
    'UnitOfMeasure':'object',
    'Location': 'object',
    'Lot': 'object',
    'Subwarehouse': 'object'
}

ORDER_HEADER_UPLOAD_REQUIRED_DTYPES = {
    'OrderNumber':'object',
    'ReceivedDate':'date',
    'PickDate':'date',
    'ShipDate':'date',
    'Channel':'object'
}

ORDER_DETAILS_UPLOAD_REQUIRED_DTYPES = {
    'OrderNumber': 'object',
    'SKU': 'object',
    'UnitOfMeasure': 'object',
    'PickType': 'object',
    'Quantity': 'int64',
    'BusinessUnit': 'object', 
    'ShipContainerType': 'object',
    'SpecialHandlingCodes': 'object', 
    'Carrier': 'object'
}

UPLOADS_REQUIRED_DTYPES_MAPPER = {
    'ItemMaster': ITEM_MASTER_UPLOAD_REQUIRED_DTYPES,
    'InboundHeader': INBOUND_HEADER_UPLOAD_REQUIRED_DTYPES,
    'InboundDetails': INBOUND_DETAILS_UPLOAD_REQUIRED_DTYPES,
    'Inventory': INVENTORY_UPLOAD_REQUIRED_DTYPES,
    'OrderHeader': ORDER_HEADER_UPLOAD_REQUIRED_DTYPES,
    'OrderDetails': ORDER_DETAILS_UPLOAD_REQUIRED_DTYPES
}

DTYPES_DEFAULT_VALUES = {
    'date': '1900-01-01',
    'time': '00:00:00',
    'object': '',
    'int64': 0,
    'float64': 0.0
}


''' File Errors '''

DIRECTORY_ERROR_DOES_NOT_EXIST = 'The given data directory does not exist.'

FILE_ERROR_MISSING_ITEM_MASTER = 'Item Master is missing. Cannot continue.'
FILE_ERROR_MISSING_INBOUND_HEADER = '"Process Inbound Data" set to true but Inbound Header is not found.'
FILE_ERROR_MISSING_INBOUND_DETAILS = '"Process Inbound Data" set to true but Inbound Details is not found.'
FILE_ERROR_MISSING_INVENTORY = '"Process Inventory Data" set to true but Inventory file is not found.'
FILE_ERROR_MISSING_OUTBOUND_HEADER = '"Process Outbound Data" set to true but Outbound Header is not found.'
FILE_ERROR_MISSING_OUTBOUND_DETAILS = '"Process Outbound Data" set to true but Outbound Details is not found.'

FILE_ERROR_ITEM_MASTER_MISSING_COLUMNS = 'Item Master is missing columns.'
FILE_ERROR_INBOUND_HEADER_MISSING_COLUMNS = 'Inbound Header is missing columns.'
FILE_ERROR_INBOUND_DETAILS_MISSING_COLUMNS = 'Inbound Details is missing columns.'
FILE_ERROR_INVENTORY_MISSING_COLUMNS = 'Inventory is missing columns.'
FILE_ERROR_ORDER_HEADER_MISSING_COLUMNS = 'Order Header is missing columns.'
FILE_ERROR_ORDER_DETAILS_MISSING_COLUMNS = 'Order Details is missing columns.'

# Unused
FILE_ERROR_INBOUND_NO_HEADER = 'Inbound Details was provided without Inbound Header.'
FILE_ERROR_INBOUND_NO_DETAILS = 'Inbound Header was provided without Inbound Details.'
FILE_ERROR_OUTBOUND_NO_HEADER = 'Outbound Details was provided without Outbound Header.'
FILE_ERROR_OUTBOUND_NO_DETAILS = 'Outbound Header was provided without Outbound Details.'
