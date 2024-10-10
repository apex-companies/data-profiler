'''
Jack Miller
Apex Companies
Oct 2024

Module containing various helper functions used throughout the codebase
'''

import pandas as pd


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
def validate_csv_column_names(file_path, columns):
    given_cols = []
    with open(file_path, 'r+') as f:
        given_cols = f.readline().strip().split(',')

    missing_cols = []
    for col in columns:
        if col not in given_cols:
            missing_cols.append(col)

    return missing_cols

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