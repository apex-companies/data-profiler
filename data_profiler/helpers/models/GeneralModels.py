'''
Jack Miller
Apex Companies
Dec 2024

Pydantic models to represent general app models and constants
'''

from enum import Enum

class UnitOfMeasure(str, Enum):
    EACH = 'Each'
    INNER = 'Inner'
    CARTON = 'Carton'
    PALLET = 'Pallet'

class DownloadDataOptions(str, Enum):
    STORAGE_ANALYZER_INPUTS = 'StorageAnalyzer Inputs'
    INVENTORY_STRATIFICATION_REPORT = 'Inventory Stratification Report'
    SUBWAREHOUSE_MATERIAL_FLOW_REPORT_CARTONS = 'Subwarehouse Material Flow Report - Cartons'
    SUBWAREHOUSE_MATERIAL_FLOW_REPORT_PALLETS = 'Subwarehouse Material Flow Report - Pallets'
    ITEMS_MATERIAL_FLOW_REPORT_EACHES = 'Items Material Flow Report - Eaches'
    ITEMS_MATERIAL_FLOW_REPORT_CARTONS = 'Items Material Flow Report - Cartons'
    ITEMS_MATERIAL_FLOW_REPORT_PALLETS = 'Items Material Flow Report - Pallets'