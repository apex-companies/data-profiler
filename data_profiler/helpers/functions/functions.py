'''
Jack Miller
Apex Companies
Oct 2024

Module containing various helper functions used throughout the codebase
'''

import pandas as pd
import os

# Checks if the given file_path can be opened as a pandas dataframe
def file_path_is_valid_data_frame(file_path: str) -> bool:

    try:
        df = pd.read_csv(file_path, nrows=5)
    except Exception as e:
        return False
    
    return True

# Determines whether the file_path contains an empty dataframe
# Empty means it has headers but no row data
def data_frame_is_empty(file_path: str) -> bool:
    
    df = pd.read_csv(file_path, nrows=5)

    return (len(df) == 0)

# Takes name of CSV file and list of required columns and returns list of missing columns
def csv_missing_column_names(file_path, columns):
    given_cols = []
    with open(file_path, 'r+') as f:
        given_cols = f.readline().strip().split(',')

    missing_cols = []
    for col in columns:
        if col not in given_cols:
            missing_cols.append(col)

    return missing_cols

# Takes name of CSV files and list of valid columns and returns list of columns that are not valid
def csv_invalid_column_names(file_path, valid_cols: list) -> list:
    given_cols = []
    with open(file_path, 'r+') as f:
        given_cols = f.readline().strip().split(',')

    invalid_cols = []
    for col in given_cols:
        if col not in valid_cols:
            invalid_cols.append(col)

    return invalid_cols

# Given a list of primary keys, this returns a list of keys that are invalid (a Falsy value)
def validate_primary_keys(pk_list: list) -> list[str]:
    erroneous_pks = []

    for key in pk_list:
        if not key:
            erroneous_pks.append(key)
    
    return erroneous_pks

# Given a list of primary keys and a list of foreign keys, this returns a list of 
#   foreign keys that aren't in the list of primary keys
def check_mismatching_primary_key_values(pk_list: list, fk_list: list) -> list[str]:
    erroneous_fks = []
    
    pk_set = set(pk_list)
    fk_set = set(fk_list)

    for key in fk_set:
        if key not in pk_set:
            erroneous_fks.append(key)

    return erroneous_fks

# Given a file path, find one that's new by adding a suffix like "Items Report (2).xlsx"
def find_new_file_path(file_path: str):
    # If it's not taken, return it
    if not os.path.exists(file_path):
        return file_path
    
    # Add suffixes
    i = 1
    return_file_path = file_path
    while i < 100:
        i += 1
        return_file_path = f'{file_path} ({i})'
        
        if not os.path.exists(return_file_path):
            return return_file_path

    # If suffixes didn't work, just return original
    return file_path
