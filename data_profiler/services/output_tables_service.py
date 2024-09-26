'''
Jack Miller
Apex Companies
January 2024
'''

from datetime import datetime
import os

import pyodbc
# from pyodbc import DatabaseError, Row



# Returns list of project numbers
def get_output_tables_project_numbers(dev: bool = False) -> list[str]:
    connection = create_server_connection()
    cursor = connection.cursor()
    
    schema = 'OutputTables_Dev' if dev else 'OutputTables_Prod'
    query = f'''SELECT ProjectNumber FROM {schema}.Project'''

    results = None
    try:
        cursor.execute(query)
        results = cursor.fetchall()
    except DatabaseError as e:
        print(f'Error getting project numbers: {e}')
    
    results = [result[0] for result in results]

    cursor.close()
    connection.close()

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

# # Returns company table row for project number
# def get_company_table_row_for_project(project_number: str) -> list[Row]:
#     connection = create_server_connection()
#     cursor = connection.cursor()
    
#     results = None
#     try:
#         query = ''' SELECT ProjectNumber, Company, Salesman, [Company Location], [Project Name] FROM OutputTables_Prod.Project WHERE ProjectNumber = ? '''
#         cursor.execute(query, project_number)
#         results = cursor.fetchall()
#     except DatabaseError as e:
#         print(f'Error getting outbound info for {project_number}: {e}')

#     cursor.close()
#     connection.close()

#     return results


# # Inserts a new row into CompanyTable
# # Returns inserted row count (should equal 1 if successful)
# def insert_new_project_to_project_table(sql_file: str, project_number: str, company_name: str, salesman: str, location: str, project_name: str, email: str, start_date: str, 
#                                         date_for_analysis: str, weekend_date_rule: str, notes: str) -> int:
#     print(f'Attempting insert into company table with project number: {project_number}')
    
#     connection = create_server_connection()
#     cursor = connection.cursor()

#     # Open query
#     fd = open(sql_file)
#     insert_query = fd.read()
#     fd.close()

#     row_count = 0
#     try:
#         cursor.execute(insert_query, [project_number,company_name,salesman,location,project_name,email,start_date, date_for_analysis, weekend_date_rule, notes])
#         row_count += cursor.rowcount
#         connection.commit()
#     except pyodbc.DatabaseError as e:
#         print(f'Error inserting new project: {e}')
#     else:
#         print('Successful insert.')

#     cursor.close()
#     connection.close()

#     return row_count


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