'''
Jack Miller
Apex Companies
January 2024
'''

from datetime import datetime
import os

import pyodbc
# from pyodbc import DatabaseError, Row

from ..models.ProjectInfo import UploadedFilePaths, ProjectInfoInputs, ProjectInfoExistingProject
from ..models.TransformOptions import DateForAnalysis, WeekendDateRules, TransformOptions

from ..database.database_manager import DatabaseConnection
from ..database.helpers.constants import DEV_OUTPUT_TABLES_SQL_FILE_SELECT_ALL_FROM_PROJECT, OUTPUT_TABLES_SQL_FILE_SELECT_ALL_FROM_PROJECT,\
    DEV_OUTPUT_TABLES_SQL_FILE_INSERT_INTO_PROJECT, OUTPUT_TABLES_SQL_FILE_INSERT_INTO_PROJECT

class OutputTablesService:

    def __init__(self, dev: bool = False):
        self.dev = dev

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

    
    def get_project_info_for_project(self, project_number: str) -> ProjectInfoExistingProject:
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
        transform_options = None
        if results[7] and results[8]:
            transform_options = TransformOptions(
                date_for_analysis=DateForAnalysis(results[7]),
                weekend_date_rule=WeekendDateRules(results[8])
            )

        upload_paths = UploadedFilePaths(
            item_master=results[12] if results[12] else '',
            inbound_header=results[13] if results[13] else '',
            inbound_details=results[14] if results[14] else '',
            inventory=results[15] if results[15] else '',
            order_header=results[16] if results[16] else '',
            order_details=results[17] if results[17] else '',
        )

        project_info = ProjectInfoExistingProject(
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
    def insert_new_project_to_project_table(self, project_info: ProjectInfoInputs) -> int:
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

    
# # Delete from OutputTables schema by project number (call func from database_functions)
# # Returns total number of affected rows or -1 if error
# def delete_from_output_tables_by_project_number(project_number: str) -> int:
#     connection = create_server_connection()

#     log_file = None
#     if os.environ['DEV'] == 'true':
#         log_file = open(f'logs/{project_number}-{datetime.now().strftime(format="%Y%m%d-%H.%M.%S")}_delete_from_output_tables.txt', 'w+')
#         log_file.write(f'PROJECT NUMBER: {project_number}\n')
    
#     # Delete
#     rows_deleted = delete_from_db_by_project_number(log_file=log_file, connection=connection, project_number=project_number, schema='OutputTables_Prod')
    
#     if log_file: log_file.close()
#     connection.close()
    
#     return rows_deleted