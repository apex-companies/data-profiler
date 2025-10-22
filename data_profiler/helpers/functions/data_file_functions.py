'''
Jack Miller
Apex Companies
Sep 2025
'''

from io import TextIOWrapper
import os
import math
import pandas as pd

from .functions import csv_given_columns, missing_column_names, invalid_column_names, file_path_is_valid_data_frame, data_frame_is_empty

from ..constants.data_file_constants import FILE_TYPES_DTYPES_MAPPER, DTYPES_DEFAULT_VALUES
from ..models.DataFiles import UploadFileType, FileValidation



def validate_file_structure( file_type: UploadFileType, file_path: str, required_columns: list, valid_columns: list = None) -> FileValidation:
    # Start
    validation_obj = FileValidation(file_type=file_type, file_path=file_path)

    # Is it present?
    if not os.path.exists(validation_obj.file_path) or os.stat(validation_obj.file_path).st_size == 0:
        validation_obj.is_present = False
        validation_obj.is_valid = False
        validation_obj.file_path = ''
        return validation_obj
    else:
        validation_obj.is_present = True

    # Is it a data frame?
    if not file_path_is_valid_data_frame(validation_obj.file_path):
        validation_obj.is_valid = False
        return validation_obj
    
    # Find given columns
    given_cols = csv_given_columns(file_path=validation_obj.file_path)
    validation_obj.given_columns = given_cols

    # Does it have all required columns?
    missing_cols = missing_column_names(given_cols=given_cols, required_cols=required_columns)
    if missing_cols:
        validation_obj.is_valid = False
        validation_obj.missing_columns = missing_cols
        return validation_obj

    # Does it have any columns it ain't supposed to?
    if valid_columns:
        invalid_cols = invalid_column_names(given_cols=given_cols, valid_cols=valid_columns)
        if invalid_cols:
            validation_obj.is_valid = False
            validation_obj.invalid_columns = invalid_cols
            return validation_obj

    # Is dataframe empty?
    if data_frame_is_empty(file_path=validation_obj.file_path):     # Empty = headers present but no row data
        validation_obj.is_present = False
        return validation_obj
    
    # Otherwise, it's valid
    return validation_obj

def read_and_cleanse_uploaded_data_file(file_type: UploadFileType, file_path: str, log_file: TextIOWrapper = None) -> tuple[pd.DataFrame, list]:
    ''' 
    Reads given file and returns a cleansed dataframe. Converts column types to match database and re-order columns. Finds type errors now before attempting DB transactions.

    Return
    ------
    pd.DataFrame
    '''

    if log_file: log_file.write(f'Reading {file_type.value}\n')

    dtypes = FILE_TYPES_DTYPES_MAPPER[file_type.value]

    df = pd.read_csv(file_path)
    if log_file: log_file.write(f'Shape: {df.shape}\n')

    errors_encountered = 0
    errors_list = []
    for col, dtype in dtypes.items():
        if not col in df.columns:
            continue

        try:
            rows_to_fill = 0
            default_val = DTYPES_DEFAULT_VALUES[dtype]

            if dtype == 'date':
                df[col] = pd.to_datetime(df[col], format='%Y-%m-%d', errors='raise')                # Be strict with dates... want to get these right
            elif dtype == 'time':
                df[col] = pd.to_datetime(df[col], format='%H:%M:%S', errors='coerce')
            elif dtype == 'float64' or dtype == 'int64':
                df[col] = pd.to_numeric(df[col], errors='coerce')
            elif dtype == 'object':
                df[col] = df[col].astype("string")
            
            rows_to_fill = len(df.loc[df[col].isna(), :])
            df[col] = df[col].replace(to_replace=math.nan, value=default_val)
            
            if rows_to_fill > 0:
                if log_file: log_file.write(f'{col} - replacing erroneous cells with default value "{default_val}" to {rows_to_fill} rows\n')

        except Exception as e:
            if log_file: log_file.write(f'ERROR - Could not convert field "{col}" to correct type {dtype}: {e}\n')
            print(f'ERROR converting field "{col}" to correct type: {e}\n')
            errors_list.append(e)
            errors_encountered += 1

    if errors_encountered > 0:
        if log_file: log_file.write(f'{errors_encountered} error(s) encountered converting to correct dtypes.\n\n')
        print(f'{errors_encountered} error(s) encountered converting to correct dtypes. Quitting before DB insertion.')
    else:
        if log_file: log_file.write(f'Dtype conversions successful.\n\n')
        print(f'Dtype conversions successful.')

    # Reindex for consistent column order
    df = df.reindex(columns=dtypes.keys())

    if log_file: log_file.flush()
    
    return df, errors_list