'''
Jack Miller
Apex Companies
Oct 2024

Module containing various helper functions used throughout the codebase
'''

import pandas as pd

def data_frame_opens(file_path: str) -> bool:

    try:
        df = pd.read_csv(file_path, nrows=5)
    except Exception as e:
        return False
    
    return True

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