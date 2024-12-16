'''
Jack Miller
Apex Companies
Dec 2024

Pydantic models to represent general app models and constants
'''

from enum import Enum


class DownloadDataOptions(str, Enum):
    STORAGE_ANALYZER_INPUTS = 'StorageAnalyzer Inputs'
    INVENTORY_STRATIFICATION_REPORT = 'Inventory Stratification Report'