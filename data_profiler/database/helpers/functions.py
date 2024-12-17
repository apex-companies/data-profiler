'''
Jack Miller
Apex Companies
December 2024

Common helper functions for interacting with database 
'''

from io import TextIOWrapper
from datetime import timedelta
from time import time

from pyodbc import Connection
import pandas as pd



def download_table_from_query(connection: Connection, query: str) -> pd.DataFrame:
    '''
    Run a SQL query and load the results as a pandas DataFrame  

    Params
    ------
    connection : pyodbc.Connection  
        some pyodbc connection object  
    query : str  
        some SQL query  
    dev : bool  
        if dev == True, use dev schema. Otherwise, use production schema  

    Return
    ------
    pd.DataFrame loaded with query results
    '''
    
    cursor = connection.cursor()

    # Execute the query
    cursor.execute(query)

    # Grab the results
    data = cursor.fetchall()
    columns = [column[0] for column in cursor.description]

    # Put it all together as a dataframe
    df = pd.DataFrame.from_records(columns=columns, data=data)

    return df


def insert_table_to_db(connection: Connection, table_name: str, data_frame: pd.DataFrame, sql_file_path: str, log_file: TextIOWrapper) -> int:
    '''
    Inserts a dataframe into the database. Uses fast_executemany to insert data all in one transaction, thus speeding up process greatly

    Note
    ------
    data_frame MUST BE 
        1) in base python types
        2) in type expected by table schema. make sure dates are stored as datetimes, etc.

    Args
    ------
    connection : Connection
        a valid pyodbc Connection object (should be connected to aasdevserverfree)
    table_name : str
        the name of a table in the OutputTables schema. Only used for logging purposes
    data_frame : pd.DataFrame
        the data to insert
    sql_file_path : str
        the path to the insert sql file for the table
    log_file : TextIOWrapper
        a file-like object used for logging            

    Return
    ------
    Number of rows inserted or -1 if error
    '''

    # If dataframe is empty, don't try inserting
    log_file.write(f'{table_name}\n')
    if len(data_frame) == 0:
        log_file.write('Table is empty\n\n')
        return 0
    
    # Configure cursor
    # https://stackoverflow.com/questions/29638136/how-to-speed-up-bulk-insert-to-ms-sql-server-using-pyodbc/47057189#47057189
    cursor = connection.cursor()
    connection.autocommit = False                   # autocommit = True could force a DB transaction for each query, which would defeat the point
    cursor.fast_executemany = True

    # Get sql query
    # fd = open(f'{self.sql_dir}/{sql_file_path}')
    fd = open(sql_file_path)
    insert_query = fd.read()
    fd.close()
    
    # Get data to insert in form of 2d list
    data_lst = data_frame.to_dict('split')['data']
    print(data_lst[0])
    log_file.write(f'{data_lst[0]}\n')

    ## Batch insert ##
    rows_inserted: int = 0
    batch_size = 100000
    batch_num = 1
    error_encountered = False
    insert_st = time()

    for i in range(0, len(data_lst), batch_size):
        # Only proceed if no errors have been found
        if not error_encountered:
            start_idx = i
            end_idx = i + batch_size

            # Partition data into batch
            batch_data = data_lst[start_idx:end_idx]
        
            # Insert using excutemany
            st = time()
            print(f'Batch {batch_num}: attempting insert into {table_name}...')
            log_file.write(f'Batch {batch_num}: attempting insert into {table_name}...\n')

            cursor.executemany(insert_query, batch_data)
            connection.commit()

            et = time()
            print(f'Inserted {len(batch_data)} rows into {table_name} in {timedelta(seconds=et-st)} seconds.')
            log_file.write(f'Inserted {len(batch_data)} rows into {table_name} in {timedelta(seconds=et-st)} seconds\n')
            rows_inserted += len(batch_data)

        batch_num += 1

    insert_et = time()
    print(f'Inserted {batch_num-1} batches into {table_name} in {timedelta(seconds=insert_et-insert_st)} seconds')
    log_file.write(f'Inserted {batch_num-1} batches into {table_name} in {timedelta(seconds=insert_et-insert_st)} seconds\n\n')

    # Close cursor
    connection.autocommit = True
    cursor.close()

    return rows_inserted