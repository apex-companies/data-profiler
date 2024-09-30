
from enum import Enum

######################
### Uploaded Files ###
######################

class UploadFileTypes(str, Enum):
    ITEM_MASTER = 'ItemMaster'
    INBOUND_HEADER = 'InboundHeader'
    INBOUND_DETAILS = 'InboundDetails'
    INVENTORY = 'Inventory'
    ORDER_HEADER = 'OrderHeader'
    ORDER_DETAILS = 'OrderDetails'

ITEM_MASTER_UPLOAD_REQUIRED_COLS = ['SKU','SKUDescription','SKUClass','UnitOfMeasure','EachLength','EachWidth','EachHeight','EachWeight','InnerQuantity','InnerLength','InnerWidth','InnerHeight','InnerWeight','CartonQuantity','CartonLength','CartonWidth','CartonHeight','CartonWeight','CartonsPerPallet','PalletTie','PalletHigh','MaxPalletStack','PalletLength','PalletWidth','PalletHeight','PalletWeight','Conveyable','Subwarehouse','AllowToPickPallet','AllowToPickCarton','AllowToPickInnerPacks','AllowToPickUnits']
INBOUND_HEADER_UPLOAD_REQUIRED_COLS = ['ReceiptNumber', 'ArrivalDate', 'ArrivalTime', 'ExpectedDate', 'ExpectedTime', 'Carrier', 'Mode']
INBOUND_DETAILS_UPLOAD_REQUIRED_COLS = ['ReceiptNumber', 'SKU', 'UnitOfMeasure', 'Quantity', 'VendorID', 'SourcePoint']
INVENTORY_UPLOAD_REQUIRED_COLS = ['Period','SKU','Quantity','UnitOfMeasure','Location','Lot','Subwarehouse']
ORDER_HEADER_UPLOAD_REQUIRED_COLS = ['OrderNumber','ReceivedDate','PickDate','ShipDate','Channel']
ORDER_DETAILS_UPLOAD_REQUIRED_COLS = ['OrderNumber','SKU','Quantity','UnitOfMeasure', 'BusinessUnit', 'ShipContainerType', 'SpecialHandlingCodes', 'Carrier']

UPLOADS_REQUIRED_COLUMNS_MAPPER = {
    'ItemMaster': ITEM_MASTER_UPLOAD_REQUIRED_COLS,
    'InboundHeader': INBOUND_HEADER_UPLOAD_REQUIRED_COLS,
    'InboundDetails': INBOUND_DETAILS_UPLOAD_REQUIRED_COLS,
    'Inventory': INVENTORY_UPLOAD_REQUIRED_COLS,
    'OrderHeader': ORDER_HEADER_UPLOAD_REQUIRED_COLS,
    'OrderDetails': ORDER_DETAILS_UPLOAD_REQUIRED_COLS
}

ITEM_MASTER_UPLOAD_REQUIRED_DTYPES = {
    # 'ProjectNumber': 'object',
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
    # 'ProjectNumber': 'object',
    'ReceiptNumber': 'object',
    'ArrivalDate': 'date', 
    'ArrivalTime': 'time' , 
    'ExpectedDate': 'date', 
    'ExpectedTime': 'time', 
    'Carrier': 'object', 
    'Mode': 'object'
}

INBOUND_DETAILS_UPLOAD_REQUIRED_DTYPES = {
    # 'ProjectNumber': 'object',
    'ReceiptNumber': 'object', 
    'SKU': 'object', 
    'UnitOfMeasure': 'object', 
    'Quantity': 'float64', 
    'VendorID': 'object', 
    'SourcePoint': 'object'
}

INVENTORY_UPLOAD_REQUIRED_DTYPES = {
    # 'ProjectNumber': 'object',
    'Period':'date',
    'SKU':'object',
    'Quantity':'int64',
    'UnitOfMeasure':'object',
    'Location': 'object',
    'Lot': 'object',
    'Subwarehouse': 'object'
}

ORDER_HEADER_UPLOAD_REQUIRED_DTYPES = {
    # 'ProjectNumber': 'object',
    'OrderNumber':'object',
    'ReceivedDate':'date',
    'PickDate':'date',
    'ShipDate':'date',
    'Channel':'object'
}

ORDER_DETAILS_UPLOAD_REQUIRED_DTYPES = {
    # 'ProjectNumber': 'object',
    'OrderNumber':'object',
    'SKU':'object',
    'Quantity':'int64',
    'UnitOfMeasure':'object',
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