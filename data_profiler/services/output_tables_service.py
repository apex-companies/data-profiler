'''
Jack Miller
Apex Companies
January 2024
'''

from datetime import datetime, timedelta
from time import time
import os
from io import TextIOWrapper

import pyodbc
# from pyodbc import DatabaseError, Row

from ..models.ProjectInfo import UploadedFilePaths, BaseProjectInfo, ExistingProjectProjectInfo
from ..models.TransformOptions import DateForAnalysis, WeekendDateRules, TransformOptions

from ..database.database_manager import DatabaseConnection
from ..database.helpers.constants import DEV_OUTPUT_TABLES_SQL_FILE_SELECT_ALL_FROM_PROJECT, OUTPUT_TABLES_SQL_FILE_SELECT_ALL_FROM_PROJECT,\
    DEV_OUTPUT_TABLES_SQL_FILE_INSERT_INTO_PROJECT, OUTPUT_TABLES_SQL_FILE_INSERT_INTO_PROJECT, DEV_OUTPUT_TABLES_SQL_FILE_UPDATE_PROJECT,\
    OUTPUT_TABLES_SQL_FILE_UPDATE_PROJECT, SCHEMAS, DEV_OUTPUT_TABLES_DELETE_SQL_FILES_MAPPER, OUTPUT_TABLES_DELETE_SQL_FILES_MAPPER

class OutputTablesService:

    def __init__(self, dev: bool = False):
        self.dev = dev

    def get_output_tables_project_numbers(self) -> list[str]:
        ''' Returns list of project numbers '''

        schema = 'OutputTables_Dev' if self.dev else 'OutputTables_Prod'
        query = f'''SELECT ProjectNumber FROM {schema}.Project'''
        results = []

        # try:
        #     db_conn = DatabaseConnection(dev=self.dev)
        # except pyodbc.InterfaceError as e:
        #     print(' - get projects - ')
        # else:
        try:
            with DatabaseConnection(dev=self.dev) as db_conn:
                # with db_conn:
                cursor = db_conn.cursor()

                cursor.execute(query)
                results = [result[0] for result in cursor.fetchall()]
                
                cursor.close()
        
        except pyodbc.InterfaceError as e:
            print(f' get projects. unsuccessful connect ')


        return results

# # Returns item master SKUs for project number
# def get_skus_in_item_master_for_project(project_number: str) -> list[Row]:
#     connection = create_server_connection()  
#     cursor = connection.cursor()
    
#     results = None
#     try:
#         query = ''' SELECT [SKU] FROM [OutputTables_Prod].[ItemMaster] WHERE [ProjectNumber] = ? '''
#         cursor.execute(query, project_number)
#         results = cursor.fetchall()
#     except DatabaseError as e:
#         print(f'Error getting SKUs for {project_number}: {e}')

#     cursor.close()
#     connection.close()

#     return results

# # Returns # of outbound lines for project number
# def get_lines_in_outbound_for_project(project_number: str) -> int:
#     connection = create_server_connection()
#     cursor = connection.cursor()

#     lines = None
#     try:
#         query = ''' SELECT Count(*) FROM [OutputTables_Prod].[OutboundData] WHERE [ProjectNumber_SKU] like CONCAT(?, '%'); '''
#         cursor.execute(query, project_number)
#         lines = cursor.fetchone()[0]
#     except DatabaseError as e:
#         print(f'Error getting lines in outbound for {project_number}: {e}')

#     cursor.close()
#     connection.close()

#     return lines

    
    def get_project_info(self, project_number: str) -> ExistingProjectProjectInfo:
        ''' Returns Project table row for project '''
        
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
            weekend_date_rule=results[8] if results[8] else None
        )
        # if results[7] and results[8]:
        #     transform_options = TransformOptions(
        #         date_for_analysis=DateForAnalysis(results[7]),
        #         weekend_date_rule=WeekendDateRules(results[8])
        #     )

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


    # Inserts a new row into CompanyTable
    # Returns inserted row count (should equal 1 if successful)
    # def insert_new_project_to_project_table(sql_file: str, project_number: str, company_name: str, salesman: str, location: str, project_name: str, email: str, start_date: str, 
    #                                         date_for_analysis: str, weekend_date_rule: str, notes: str) -> int:
    def insert_new_project_to_project_table(self, project_info: BaseProjectInfo) -> int:
        print(f'Attempting insert into company table with project number: {project_info.project_number}')
        
        row_count = 0

        # Get query from sql file
        sql_file = DEV_OUTPUT_TABLES_SQL_FILE_INSERT_INTO_PROJECT if self.dev else OUTPUT_TABLES_SQL_FILE_INSERT_INTO_PROJECT

        f = open(sql_file)
        insert_query = f.read()
        f.close()

        # Setup query arguments. IMPORTANT to be in same order as insert_into_project.sql query
        query_args = [project_info.project_number, project_info.company_name, project_info.salesperson, project_info.company_location, 
                      project_info.project_name, project_info.email, project_info.start_date, None, None, project_info.notes, False, 
                      None, None, None, None, None, None, None]

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
    
    # Updates the project's row in Project
    # Returns inserted row count (should equal 1 if successful)
    def update_project_in_project_table(self, new_project_info: ExistingProjectProjectInfo) -> int:
        print(f'Attempting insert into company table with project number: {new_project_info.project_number}')
        
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


# # Takes user input re: project info and calls insert_new_project_to_company_table to insert to DB
# # Returns the inserted row count
# def insert_new_project_to_project_table_from_user_input(project_number: str, sql_file: str) -> int:
#     print(f'Hello! Congratulations on this big decision to insert a new project into the database. Please enter some information: \n')
#     print(f'Project Number: {project_number}')
#     company_name = input('Company Name: ')
#     salesman = input('Sales Person: ')
#     location = input('Company Location: ')
#     project_name = input('Project Name: ')
#     email = input('Security Email: ')
#     start_date = input('Start Date (mm/dd/yyyy): ')
#     notes = input('Notes: ')
#     print(f'Thank you! Working on that now...')

#     row_count = insert_new_project_to_project_table(sql_file=sql_file, project_number=project_number, company_name=company_name, salesman=salesman, location=location, project_name=project_name, email=email, start_date=start_date, notes=notes)
    
#     print(f'All done. Thanks again!')

#     return row_count

    def delete_project(self, project_number: str):
        # get_project_info()
        # if project.has_uploaded_data == True:
        #       please delete project data before deleting project
        #
        # delete from Project
        pass

    # TODO - don't delete from Project. But update DataUploaded to False
    def delete_project_data(self, project_number: str, log_file: TextIOWrapper) -> int:
        '''
        Delete from OutputTables schema
        Removes records from all relevant DB tables belonging to the given project_number
        Optional param "tables": defaults to all, which deletes from all tables in schema. Pass a specific table to "tables" and this function will delete only from that table
        Returns total number of deleted rows or -1 if error
        '''

        # Create log file, if dev
        # log_file = None
        # if self.dev:
        #     log_file = open(f'logs/{project_number}-{datetime.now().strftime(format="%Y%m%d-%H.%M.%S")}_delete_from_output_tables.txt', 'w+')
        #     log_file.write(f'PROJECT NUMBER: {project_number}\n')
        
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

        # if log_file: 
        # log_file.write(f'Deleting records from {schema} table(s) "{tables}" belonging to project number: {project_number}\n')
        
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

                # if log_file: 
                # log_file.write(f'{delete_query} \n')
                # try:
                
                cursor.execute(delete_query, project_number)
                rows_deleted = cursor.rowcount
                total_rows_deleted += rows_deleted

                print(f'{table} - rows deleted: {rows_deleted}')
                # if log_file: 
                log_file.write(f'{table} - rows deleted: {rows_deleted}\n')
                    
                db_conn.commit()

                # except pyodbc.Error as e:
                #     print(f'Error deleting by project number: {e}')
                #     if log_file: log_file.write(f'Error deleting by project number: {e}\n')
                #     print(f'Query: {delete_query}')
                #     if log_file: log_file.write(f'Query: {delete_query}\n')
            
            cursor.close()  
            
        delete_et = time()
        print(f'Finished deleting. Took {timedelta(seconds=delete_et-delete_st)}.')
        print(f'{total_rows_deleted} rows deleted.')

        # if log_file: 
        log_file.write(f'Finished deleting. Took {timedelta(seconds=delete_et-delete_st)}.\n')
        log_file.write(f'{total_rows_deleted} rows deleted.\n')
            # log_file.close()
                  
        
        return total_rows_deleted