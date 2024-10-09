'''
Jack Miller
Apex Companies
January 2024
'''

# Python
from datetime import datetime, timedelta
from time import time
from io import TextIOWrapper
import pyodbc

# Data Profiler
from ..models.ProjectInfo import UploadedFilePaths, BaseProjectInfo, ExistingProjectProjectInfo
from ..models.TransformOptions import TransformOptions
from ..models.Responses import DeleteResponse

from ..database.database_manager import DatabaseConnection
from ..database.helpers.constants import DEV_OUTPUT_TABLES_SQL_FILE_SELECT_ALL_FROM_PROJECT, OUTPUT_TABLES_SQL_FILE_SELECT_ALL_FROM_PROJECT,\
    DEV_OUTPUT_TABLES_SQL_FILE_INSERT_INTO_PROJECT, OUTPUT_TABLES_SQL_FILE_INSERT_INTO_PROJECT, DEV_OUTPUT_TABLES_SQL_FILE_UPDATE_PROJECT,\
    OUTPUT_TABLES_SQL_FILE_UPDATE_PROJECT, SCHEMAS, DEV_OUTPUT_TABLES_DELETE_SQL_FILES_MAPPER, OUTPUT_TABLES_DELETE_SQL_FILES_MAPPER,\
    OUTPUT_TABLES_SQL_FILE_DELETE_FROM_PROJECT, DEV_OUTPUT_TABLES_SQL_FILE_DELETE_FROM_PROJECT


class OutputTablesService:

    def __init__(self, dev: bool = False):
        self.dev = dev

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

        f = open(sql_file)
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

        f = open(sql_file)
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

        f = open(sql_file)
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

    
    def delete_project_data(self, project_number: str, log_file: TextIOWrapper) -> DeleteResponse:
        '''
        Delete from OutputTables schema. Removes records from all relevant DB tables belonging to the given project number

        Return
        ------
        DeleteResponse
        '''

        response = DeleteResponse(project_number=project_number)

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
        
        with DatabaseConnection(dev=self.dev) as db_conn:
            cursor = db_conn.cursor()

            # We want to delete one table at a time so it's easier to tell where failure happens
            for table,file in sql_file_mapper.items():

                # If a single table is passed to be deleted, skip if not the correct table
                if tables != 'all' and table != tables:
                    continue

                if table == 'Project':
                    break
                
                # Get delete query
                fd = open(file)
                delete_query = fd.read()
                fd.close()
                print(f'{delete_query} \n')

                try:
                
                    cursor.execute(delete_query, project_number)
                    rows_deleted = cursor.rowcount
                    total_rows_deleted += rows_deleted

                    print(f'{table} - rows deleted: {rows_deleted}')
                    log_file.write(f'{table} - rows deleted: {rows_deleted}\n')
                        
                    db_conn.commit()

                except pyodbc.Error as e:
                    print(f'Error deleting by project number: {e}')
                    log_file.write(f'Error deleting by project number: {e}\n')

                    response.success = False
                    response.errors_encountered.append(e)

            cursor.close()  
            
        delete_et = time()
        print(f'Finished deleting. Took {timedelta(seconds=delete_et-delete_st)}.')
        print(f'{total_rows_deleted} rows deleted.')

        if response.success:
            log_file.write('\nSuccess!\n')
        else:
            log_file.write(f'\n{len(response.errors_encountered)} errors while deleting. Unsuccessful. Try again.\n') 
        
        log_file.write(f'Finished deleting. Took {timedelta(seconds=delete_et-delete_st)}.\n\n')
        log_file.write(f'{total_rows_deleted} rows deleted.\n')
                  
        response.rows_deleted = total_rows_deleted

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

        f = open(sql_file)
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