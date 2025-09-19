'''
Jack Miller
Apex Companies
January 2024

Functions that interface with the OutputTables schema in the database
'''

# Python
from typing import Callable
from datetime import datetime, timedelta
from time import time
from io import TextIOWrapper
import math

import pyodbc
from pyodbc import DatabaseError
import pandas as pd

# Data Profiler
from ..helpers.functions.functions import find_new_file_path

from ..helpers.models.ProjectInfo import UploadedFilePaths, BaseProjectInfo, ExistingProjectProjectInfo
from ..helpers.models.TransformOptions import TransformOptions
from ..helpers.models.Responses import BaseDBResponse, DBDownloadResponse
from ..helpers.models.GeneralModels import UnitOfMeasure
from ..helpers.constants.app_constants import SQL_DIR, SQL_DIR_DEV

from ..database.database_manager import DatabaseConnection
from ..database.helpers.constants import *
from ..database.helpers.functions import download_table_from_query

class OutputTablesService:

    def __init__(self, dev: bool = False):
        self.dev = dev
        self.sql_dir = SQL_DIR_DEV if self.dev else SQL_DIR

    def __enter__(self):
        return self

    def __exit__(self, exception_type, exception_value, exception_traceback):
        # If there was an error in the with block, raise it
        if exception_type is not None:
            print(f'------ OUTPUT TABLES EXCEPTION ------\n{exception_type = }\n{exception_value = }\n{exception_traceback = }\n')
            raise exception_value


    ''' Main Functions '''

    def get_output_tables_project_numbers(self) -> list[str]:
        ''' Returns list of project numbers '''

        schema = 'OutputTables_Dev' if self.dev else 'OutputTables_Prod'
        query = f'''SELECT ProjectNumber FROM {schema}.Project'''
        results = []

        with DatabaseConnection(dev=self.dev) as db_conn:
            cursor = db_conn.cursor()

            cursor.execute(query)
            results = [result[0] for result in cursor.fetchall()]
            
            cursor.close()

        return results

    def get_project_info(self, project_number: str) -> ExistingProjectProjectInfo:
        ''' Returns Project table row for given project number'''
        
        results = []

        # Get query from sql file
        sql_file = DEV_OUTPUT_TABLES_SQL_FILE_SELECT_ALL_FROM_PROJECT if self.dev else OUTPUT_TABLES_SQL_FILE_SELECT_ALL_FROM_PROJECT

        f = open(f'{self.sql_dir}/{sql_file}')
        select_query = f.read()
        f.close()

        # Connect and run query    
        with DatabaseConnection(dev=self.dev) as db_conn:
            cursor = db_conn.cursor()

            print(select_query)
            cursor.execute(select_query, project_number)
            results = cursor.fetchall()[0]

        # Create ProjectInfoExistingProject object and return
        transform_options = TransformOptions(
            date_for_analysis=results[7] if results[7] else None,
            weekend_date_rule=results[8] if results[8] else None,
            process_inbound_data=results[18] if results[18] else False,
            process_inventory_data=results[19] if results[19] else False,
            process_outbound_data=results[20] if results[20] else False
        )

        upload_paths = UploadedFilePaths(
            item_master=results[12] if results[12] else '',
            inbound_header=results[13] if results[13] else '',
            inbound_details=results[14] if results[14] else '',
            inventory=results[15] if results[15] else '',
            order_header=results[16] if results[16] else '',
            order_details=results[17] if results[17] else '',
        )

        project_info = ExistingProjectProjectInfo(
            project_number=results[0],
            company_name=results[1],
            salesperson=results[2],
            company_location=results[3],
            project_name=results[4],
            email=results[5],
            start_date=datetime.strftime(results[6], format='%Y-%m-%d'),
            transform_options=transform_options,
            notes=results[9] if results[9] else '',
            data_uploaded=results[10],
            upload_date=datetime.strftime(results[11], format='%Y-%m-%d') if results[11] else '',
            uploaded_file_paths=upload_paths
        )

        return project_info

    def get_sku_list(self, project_number: str) -> list[str]:
        ''' Returns list of SKUs for given project number'''
        
        sku_list = []

        # Get query from sql file
        sql_file = DEV_OUTPUT_TABLES_SQL_FILE_GET_SKU_LIST if self.dev else OUTPUT_TABLES_SQL_FILE_GET_SKU_LIST

        f = open(f'{self.sql_dir}/{sql_file}')
        select_query = f.read()
        f.close()

        # Connect and run query    
        with DatabaseConnection(dev=self.dev) as db_conn:
            cursor = db_conn.cursor()

            cursor.execute(select_query, project_number)
            sku_list = [result[0] for result in cursor.fetchall()]

        return sku_list

    def download_storage_analyzer_inputs(self, project_number: str, download_folder: str) -> DBDownloadResponse:

        # Init empty dataframes
        item_master_df: pd.DataFrame
        inventory_df: pd.DataFrame
        outbound_data_df: pd.DataFrame

        # Get sql files    
        im_sql_file = DEV_SQL_FILE_DOWNLOAD_STORAGE_ANALYZER_INPUTS_SELECT_FROM_ITEM_MASTER if self.dev else SQL_FILE_DOWNLOAD_STORAGE_ANALYZER_INPUTS_SELECT_FROM_ITEM_MASTER
        inv_sql_file = DEV_SQL_FILE_DOWNLOAD_STORAGE_ANALYZER_INPUTS_SELECT_FROM_INVENTORY if self.dev else SQL_FILE_DOWNLOAD_STORAGE_ANALYZER_INPUTS_SELECT_FROM_INVENTORY
        ob_sql_file = DEV_SQL_FILE_DOWNLOAD_STORAGE_ANALYZER_INPUTS_SELECT_FROM_OUTBOUND if self.dev else SQL_FILE_DOWNLOAD_STORAGE_ANALYZER_INPUTS_SELECT_FROM_OUTBOUND
        
        # Read sql files
        f = open(f'{self.sql_dir}/{im_sql_file}')
        im_query = f.read()
        im_query = im_query.replace('?', f"'{project_number}'")
        f.close()

        f = open(f'{self.sql_dir}/{inv_sql_file}')
        inv_query = f.read()
        inv_query = inv_query.replace('?', f"'{project_number}'")
        f.close()

        f = open(f'{self.sql_dir}/{ob_sql_file}')
        ob_query = f.read()
        ob_query = ob_query.replace('?', f"'{project_number}'")
        f.close()
        
        # Download datas
        download_response = DBDownloadResponse(project_number=project_number, download_path=download_folder)
        with DatabaseConnection(dev=self.dev) as db_conn:
            try: 
                print(f'Downloading Item Master...')
                item_master_df = download_table_from_query(connection=db_conn, query=im_query)

                print(f'Downloading Inventory...')
                inventory_df = download_table_from_query(connection=db_conn, query=inv_query)

                print(f'Downloading Outbound...')
                outbound_data_df = download_table_from_query(connection=db_conn, query=ob_query)
            except DatabaseError as e:
                print(e)
                download_response.success = False
                download_response.message = f'Something went wrong when reading from the database. {e}'
            except Exception as e:
                print(e)
                download_response.success = False
                download_response.message = f'Something unknown went wrong. {e}'
            else:
                download_response.success = True
                download_response.rows_affected = len(item_master_df) + len(inventory_df) + len(outbound_data_df)

        # Export
        if download_response.success:
            item_master_df.to_csv(f'{download_folder}/ItemMaster.csv', index=False)
            inventory_df.to_csv(f'{download_folder}/Inventory.csv', index=False)
            outbound_data_df.to_csv(f'{download_folder}/OutboundData.csv', index=False)

        return download_response
    
    def download_inventory_stratification_report(self, project_number: str, download_folder: str):
        
        # Init empty dataframes
        each_df: pd.DataFrame
        inner_df: pd.DataFrame
        carton_df: pd.DataFrame
        pallet_df: pd.DataFrame

        # Get sql file
        sql_file = DEV_SQL_FILE_DOWNLOAD_INVENTORY_STRATIFICATION_REPORT if self.dev else SQL_FILE_DOWNLOAD_INVENTORY_STRATIFICATION_REPORT
        
        # Read sql files
        f = open(f'{self.sql_dir}/{sql_file}')
        query = f.read()
        query = query.replace('?', f'\'{project_number}\'', 1)
        f.close()

        download_response = DBDownloadResponse(download_path=download_folder)
        with DatabaseConnection(dev=self.dev) as db_conn:
            try: 
                # NOTE - run once for each UOM?
                print(f'Downloading Inventory Stratification Report...')

                each_query = query.replace('?', '\'Each\'', 1)
                print(each_query)
                each_df = download_table_from_query(connection=db_conn, query=each_query)

                inner_query = query.replace('?', '\'Inner\'', 1)
                print(inner_query)
                inner_df = download_table_from_query(connection=db_conn, query=inner_query)

                carton_query = query.replace('?', '\'Carton\'', 1)
                print(carton_query)
                carton_df = download_table_from_query(connection=db_conn, query=carton_query)

                pallet_query = query.replace('?', '\'Pallet\'', 1)
                print(pallet_query)
                pallet_df = download_table_from_query(connection=db_conn, query=pallet_query)
            except DatabaseError as e:
                print(e)
                download_response.success = False
                download_response.message = f'Something went wrong when reading from the database. {e}'
            except Exception as e:
                print(e)
                download_response.success = False
                download_response.message = f'Something unknown went wrong. {e}'
            else:
                download_response.success = True
                download_response.message = 'Success!'
                download_response.rows_downloaded = len(carton_df) + len(pallet_df)

        # Export
        if download_response.success:
            file_path = find_new_file_path(f'{download_folder}/Inventory Stratification')
            with pd.ExcelWriter(f'{file_path}.xlsx') as writer:
                each_df.to_excel(writer, sheet_name='Eaches', index=False)
                inner_df.to_excel(writer, sheet_name='Inners', index=False)
                carton_df.to_excel(writer, sheet_name='Cartons', index=False)
                pallet_df.to_excel(writer, sheet_name='Pallets', index=False)
            

        return download_response
    
    def download_subwarehouse_material_flow_report(self, uom: UnitOfMeasure, project_number: str, download_folder: str):
        
        # Init empty dataframes
        df: pd.DataFrame

        # Get sql file
        sql_file = DEV_SQL_FILE_DOWNLOAD_SUBWAREHOUSE_MATERIAL_FLOW_PALLETS_REPORT if self.dev else SQL_FILE_DOWNLOAD_SUBWAREHOUSE_MATERIAL_FLOW_PALLETS_REPORT
        
        # Read sql files
        f = open(f'{self.sql_dir}/{sql_file}')
        query = f.read()
        f.close()

        # Plug in project # and uom
        query = query.replace('?', f'\'{project_number}\'', 1)
        query = query.replace('?', f'\'{uom.value}\'', 1)

        download_response = DBDownloadResponse(download_path=download_folder)
        with DatabaseConnection(dev=self.dev) as db_conn:
            try: 
                # NOTE - run once for each UOM?
                print(f'Downloading Subwarehouse Material Flow - {uom.value} Report...')
                print(query)
                df = download_table_from_query(connection=db_conn, query=query)
            except DatabaseError as e:
                print(e)
                download_response.success = False
                download_response.message = f'Something went wrong when reading from the database. {e}'
            except Exception as e:
                print(e)
                download_response.success = False
                download_response.message = f'Something unknown went wrong. {e}'
            else:
                download_response.success = True
                download_response.message = 'Success!'
                download_response.rows_downloaded = len(df)

        # Export
        if download_response.success:
            file_path = find_new_file_path(f'{download_folder}/Subwarehouse Material Flow - {uom.value}')
            with pd.ExcelWriter(f'{file_path}.xlsx') as writer:
                df.to_excel(writer, sheet_name='Material Flow Summary', index=False)

        return download_response
    
    def download_items_material_flow_report(self, uom: UnitOfMeasure, project_number: str, download_folder: str):
        
        # Init empty dataframes
        df: pd.DataFrame

        # Get sql file
        sql_file = DEV_SQL_FILE_DOWNLOAD_ITEMS_MATERIAL_FLOW_REPORT if self.dev else SQL_FILE_DOWNLOAD_ITEMS_MATERIAL_FLOW_REPORT
        
        # Read sql files
        f = open(f'{self.sql_dir}/{sql_file}')
        query = f.read()
        f.close()
        
        # Plug in project # and uom
        query = query.replace('?', f'\'{project_number}\'', 1)
        query = query.replace('?', f'\'{uom.value}\'', 1)
        
        download_response = DBDownloadResponse(download_path=download_folder)
        with DatabaseConnection(dev=self.dev) as db_conn:
            try: 
                # NOTE - run once for each UOM?
                print(f'Downloading Items Material Flow - {uom.value} Report...')
                print(query)
                df = download_table_from_query(connection=db_conn, query=query)
            except DatabaseError as e:
                print(e)
                download_response.success = False
                download_response.message = f'Something went wrong when reading from the database. {e}'
            except Exception as e:
                print(e)
                download_response.success = False
                download_response.message = f'Something unknown went wrong. {e}'
            else:
                download_response.success = True
                download_response.message = 'Success!'
                download_response.rows_downloaded = len(df)

        # Export
        if download_response.success:
            file_path = find_new_file_path(f'{download_folder}/Items Material Flow - {uom.value}')
            with pd.ExcelWriter(f'{file_path}.xlsx') as writer:
                df.to_excel(writer, sheet_name='Material Flow Summary', index=False)

        return download_response

    def insert_new_project_to_project_table(self, project_info: BaseProjectInfo) -> int:
        '''
        Inserts a new row into Project

        Args
        ----
        project_info : BaseProjectInfo   
            project info to insert

        Return
        ------
        The inserted row count (should equal 1 if successful)
        '''

        row_count = 0

        # Get query from sql file
        sql_file = DEV_OUTPUT_TABLES_SQL_FILE_INSERT_INTO_PROJECT if self.dev else OUTPUT_TABLES_SQL_FILE_INSERT_INTO_PROJECT

        f = open(f'{self.sql_dir}/{sql_file}')
        insert_query = f.read()
        f.close()

        # Setup query arguments. IMPORTANT to be in same order as insert_into_project.sql query
        query_args = [project_info.project_number, project_info.company_name, project_info.salesperson, project_info.company_location, 
                      project_info.project_name, project_info.email, project_info.start_date, None, None, project_info.notes, False, 
                      None, None, None, None, None, None, None, None, None, None]

        # Connect and run query    
        with DatabaseConnection(dev=self.dev) as db_conn:
            cursor = db_conn.cursor()

            print(insert_query)
            print(query_args)
            cursor.execute(insert_query, query_args)
            row_count += cursor.rowcount
            db_conn.commit()

            cursor.close()

        return row_count
    
    def update_project_in_project_table(self, new_project_info: ExistingProjectProjectInfo) -> int:
        '''
        Updates the project's row in Project

        Return
        ------
        The updated row count (should equal 1 if successful)
        '''
        
        row_count = 0

        # Get query from sql file
        sql_file = DEV_OUTPUT_TABLES_SQL_FILE_UPDATE_PROJECT if self.dev else OUTPUT_TABLES_SQL_FILE_UPDATE_PROJECT

        f = open(f'{self.sql_dir}/{sql_file}')
        update_query = f.read()
        f.close()

        # Setup query arguments. IMPORTANT to be in same order as update_project.sql query
        query_args = [new_project_info.company_name, new_project_info.salesperson, new_project_info.company_location, 
                      new_project_info.project_name, new_project_info.email, new_project_info.start_date, 
                      new_project_info.transform_options.date_for_analysis, new_project_info.transform_options.weekend_date_rule, new_project_info.notes, 
                      new_project_info.data_uploaded, new_project_info.upload_date, new_project_info.uploaded_file_paths.item_master, 
                      new_project_info.uploaded_file_paths.inbound_header, new_project_info.uploaded_file_paths.inbound_details, 
                      new_project_info.uploaded_file_paths.inventory, new_project_info.uploaded_file_paths.order_header, new_project_info.uploaded_file_paths.order_details, 
                      new_project_info.transform_options.process_inbound_data, new_project_info.transform_options.process_inventory_data, new_project_info.transform_options.process_outbound_data,
                      new_project_info.project_number]

        # Connect and run query    
        with DatabaseConnection(dev=self.dev) as db_conn:
            cursor = db_conn.cursor()

            print(update_query)
            print(query_args)
            cursor.execute(update_query, query_args)
            row_count += cursor.rowcount
            db_conn.commit()

            cursor.close()

        return row_count

    def update_item_master(self, project_number: str, data_frame: pd.DataFrame) -> int:
        '''
        Updates Item Master for given SKUs

        Params
        ------
        project_number : str  
            the project number
        data_frame : pd.DataFrame  
            columns = ['SKU', ...]  
            Must only contain valid item master columns
        
        Return
        ------
        The number of SKUs affected by update
        '''

        # Make sure SKU is given (other columns have already been validated)
        if 'SKU' not in data_frame.columns:
            raise ValueError(f'SKU numbers not provided for item master update.')

        # Create update query
        schema = 'OutputTables_Dev' if self.dev else 'OutputTables_Prod'
        given_attributes = data_frame.columns.drop(labels='SKU').tolist()
        set_column_strings = [f'[{col}] = ?' for col in given_attributes]

        update_query = f'''
            UPDATE [{schema}].[ItemMaster]
            SET {", ".join(set_column_strings)}
            WHERE [ProjectNumber] = ? AND [SKU] = ?
        '''
        print(update_query)

        # Add ProjectNumber to data_frame and reorder columns to match update query
        data_frame['ProjectNumber'] = project_number
        data_frame = data_frame.reindex(columns=given_attributes + ['ProjectNumber', 'SKU'])

        # Get 2d list
        data_lst = data_frame.to_dict('split')['data']
        print(data_lst[0])

        # Connect and run query    
        row_count = 0
        with DatabaseConnection(dev=self.dev) as db_conn:
            cursor = db_conn.cursor()

            # Use fast execute many
            db_conn.autocommit = False                   # autocommit = True could force a DB transaction for each query, which would defeat the point
            cursor.fast_executemany = True

            batch_size = 1000                            # Update is real slow, so set a moderate batch size
            batch_num = 1

            batches = int(math.ceil(len(data_lst) / batch_size))
            for i in range(0, len(data_lst), batch_size):
                # Partition data into batch
                start_idx = i
                end_idx = i + batch_size
                batch_data = data_lst[start_idx:end_idx]

                # Execute query, all data at once
                print(f'Batch {batch_num} of {batches}: attempting to insert {len(batch_data)} rows into Item Master...')

                st = time()
                cursor.executemany(update_query, batch_data)
                db_conn.commit()
                et = time()

                print(f'Inserted {len(batch_data)} rows into Item Master in {timedelta(seconds=et-st)} seconds.')

                batch_num += 1

            # executemany can't return rowcount, so assuming the code has executed to this point, everything was successful, and the rowcount is the number of items given!
            row_count = len(data_lst)   

            # Turn off fast execute many
            db_conn.autocommit = True
            cursor.fast_executemany = False

            cursor.close()

        return row_count

    def delete_project_data(self, project_number: str, log_file: TextIOWrapper, update_progress_text_func: Callable[[str], None] = None) -> BaseDBResponse:
        '''
        Delete from OutputTables schema. Removes records from all relevant DB tables belonging to the given project number

        Return
        ------
        DeleteResponse
        '''

        response = BaseDBResponse(project_number=project_number)

        # Configure schema and sql file mapper
        tables = 'all'                          # NOTE - this is from old code, when RawData was still used. We no longer need to be able to delete one table at a time, but it could be a future requirement
        schema = ''
        sql_file_mapper = {}
        if self.dev:
            schema = 'OutputTables_Dev' 
            sql_file_mapper = DEV_OUTPUT_TABLES_DELETE_SQL_FILES_MAPPER
        else:
            schema = 'OutputTables_Prod'
            sql_file_mapper = OUTPUT_TABLES_DELETE_SQL_FILES_MAPPER
               
        # Loop through delete queries and execute them
        delete_st = time()
        print(f'Deleting records from {schema} table(s) "{tables}" belonging to project number: {project_number}')
        total_rows_deleted = 0
        errors_encountered = []
        response.success = True

        with DatabaseConnection(dev=self.dev) as db_conn:
            cursor = db_conn.cursor()

            # We want to delete one table at a time so it's easier to tell where failure happens
            i = 1
            for table,file in sql_file_mapper.items():

                # If a single table is passed to be deleted, skip if not the correct table
                if tables != 'all' and table != tables:
                    continue

                if table == 'Project':
                    break
                
                # Delete
                if update_progress_text_func: update_progress_text_func(f'Deleting from {table} ({i} / {len(sql_file_mapper.keys()) - 1})...')
                log_file.write(f'Deleting from {table} - ')
                log_file.flush()
                
                # Get delete query
                fd = open(f'{self.sql_dir}/{file}')
                delete_query = fd.read()
                fd.close()
                print(f'{delete_query} \n')

                try:
                                       
                    cursor.execute(delete_query, project_number)
                    rows_deleted = cursor.rowcount
                    total_rows_deleted += rows_deleted

                    print(f'{table} - rows deleted: {rows_deleted}')
                    log_file.write(f'rows deleted: {rows_deleted}\n')
                    log_file.flush()

                    db_conn.commit()

                except pyodbc.Error as e:
                    print(f'Error deleting by project number: {e}')
                    log_file.write(f'Error deleting by project number: {e}\n')
                    log_file.flush()

                    response.success = False
                    errors_encountered.append(e)

                i += 1

            cursor.close()  
            
        delete_et = time()
        print(f'Finished deleting. Took {timedelta(seconds=delete_et-delete_st)}.')
        print(f'{total_rows_deleted} rows deleted.')


        if response.success:
            log_file.write('\nSuccess!\n')
        else:
            log_file.write(f'\n{len(errors_encountered)} errors while deleting. Unsuccessful. Try again.\n') 
            errors_str = "\n".join(errors_encountered)
            response.message = f'{len(errors_encountered)} errors while deleting:\n\n{errors_str}'
        
        log_file.write(f'Finished deleting. Took {timedelta(seconds=delete_et-delete_st)}.\n\n')
        log_file.write(f'{total_rows_deleted} rows deleted.\n')
        log_file.flush()

        response.rows_affected = total_rows_deleted

        return response
    
    def delete_project(self, project_number: str) -> int:
        '''
        Deletes project number's row from Project

        Return
        ------
        The deleted row count (should equal 1 if successful)
        '''
        
        row_count = 0

        # Get query from sql file
        sql_file = DEV_OUTPUT_TABLES_SQL_FILE_DELETE_FROM_PROJECT if self.dev else OUTPUT_TABLES_SQL_FILE_DELETE_FROM_PROJECT

        f = open(f'{self.sql_dir}/{sql_file}')
        delete_query = f.read()
        f.close()

        # Connect and run query    
        with DatabaseConnection(dev=self.dev) as db_conn:
            cursor = db_conn.cursor()

            print(delete_query)
            cursor.execute(delete_query, project_number)
            row_count = cursor.rowcount
            db_conn.commit()

            cursor.close()

        return row_count