'''
Jack Miller
Apex Companies
December 2023

Functions that create the different output tables
'''

# Python
import re
from datetime import timedelta
from time import time
from io import TextIOWrapper

import pandas as pd
import numpy as np
from pyodbc import Connection, InterfaceError, DatabaseError

# Data Profiler
from ..database.helpers.constants import OUTPUT_TABLES_COLS_MAPPER, OUTPUT_TABLES_INSERT_SQL_FILES_MAPPER, DEV_OUTPUT_TABLES_INSERT_SQL_FILES_MAPPER
from ..database.database_manager import DatabaseConnection

from ..helpers.models.TransformOptions import TransformOptions, DateForAnalysis, WeekendDateRules
from ..helpers.models.Responses import TransformRowsInserted, TransformResponse
from ..helpers.constants.app_constants import SQL_DIR, SQL_DIR_DEV


class TransformService:
    '''
    Service that provides data transformation functionality. It is meant for one-time use - meaning, a single call to `transform_and_persist_dataframes` per instance.  
    
    The main function takes a set of dataframes and creates data in the form of the OutputTables schema, and then inserts the data into the database.
    '''

    def __init__(self, project_number: str, transform_options: TransformOptions, dev: bool = False):
        self.project_number = project_number
        self.transform_options = transform_options
        self.dev = dev
        self.sql_dir = SQL_DIR_DEV if self.dev else SQL_DIR

    def __enter__(self):
        return self

    def __exit__(self, exception_type, exception_value, exception_traceback):
        # If there was an error in the with block, raise it
        if exception_type is not None:
            print(f'------ TRANSFORM EXCEPTION ------\n{exception_type = }\n{exception_value = }\n{exception_traceback = }\n')
            raise exception_value


    ''' Main Functions '''
    
    def transform_and_persist_dataframes(self, 
                                         item_master_df: pd.DataFrame, 
                                         inbound_header_df: pd.DataFrame, 
                                         inbound_details_df: pd.DataFrame,
                                         inventory_df: pd.DataFrame, 
                                         order_header_df: pd.DataFrame, 
                                         order_details_df: pd.DataFrame,
                                         log_file: TextIOWrapper) -> TransformResponse:
        '''
        Transforms the raw data dataframes and inserts into the OutputTables_Dev schema

        Return
        ------
        TransformResponse
        '''

        rows_inserted_obj = TransformRowsInserted()
        transform_response = TransformResponse(project_number=self.project_number)
        total_rows_inserted = 0

        '''STEP 1: Create output tables '''

        # Instantiate dataframe variables - one for each output table
        item_master_data = pd.DataFrame()
        inbound_header = pd.DataFrame()
        inbound_details = pd.DataFrame()
        outbound_data = pd.DataFrame()
        order_velocity_combinations = pd.DataFrame()
        inventory_data = pd.DataFrame()
        velocity_summary = pd.DataFrame()
        outbound_data_by_order = pd.DataFrame()
        daily_order_profile_by_velocity = pd.DataFrame()
        velocity_by_month = pd.DataFrame()
        project_number_velocity = pd.DataFrame()
        project_number_order_number = pd.DataFrame()
        velocity_ladder = pd.DataFrame()

        velocity_analysis = pd.DataFrame(columns=['SKU', 'Velocity'])
        order_nums = []

        st = time()
        log_file.write(f'2. CREATE OUTPUT TABLES\n')

        # Start with Item Master
        item_master_data = self.create_item_master(project_num=self.project_number, item_master=item_master_df)
        log_file.write(f'Item Master rows: {len(item_master_data)}\n')

        # Create outbound so we can determine velocities
        if self.transform_options.process_outbound_data:
            outbound_data = self.create_outbound_data(project_num=self.project_number, order_header_df=order_header_df, order_details_df=order_details_df, item_master_df=item_master_data)
            order_nums = outbound_data['OrderNumber'].unique().tolist()

            # Run velocity analysis, and add velocity to Item Master, Outbound Data
            velocity_analysis = self.run_velocity_analysis(outbound_df=outbound_data)

            outbound_data = outbound_data.merge(velocity_analysis[['SKU', 'Velocity']], on='SKU', how='left')
            outbound_data['Velocity'] = outbound_data['Velocity'].fillna('X')

            item_master_data = item_master_data.merge(velocity_analysis[['SKU', 'Velocity']], on='SKU', how='left')
            item_master_data['Velocity'] = item_master_data['Velocity'].fillna('X')

            log_file.write(f'Outbound Data rows: {len(outbound_data)}\n')
        else:
            # Fill velocity in with X
            item_master_data['Velocity'] = 'X'
        
        # Inbound
        inbound_skus = []
        if self.transform_options.process_inbound_data:
            inbound_header = self.create_inbound_header(project_num=self.project_number, inbound_header_df=inbound_header_df, inbound_details_df=inbound_details_df)
            inbound_details = self.create_inbound_details(project_num=self.project_number, inbound_details_df=inbound_details_df, item_master_df=item_master_data)

            log_file.write(f'Inbound Header rows: {len(inbound_header)}\n')
            log_file.write(f'Inbound Details rows: {len(inbound_details)}\n')

            inbound_skus = set(inbound_details['SKU'].unique().tolist())

        # Inventory
        if self.transform_options.process_inventory_data:
            inventory_data = self.create_inventory_data(project_num=self.project_number, inventory_df=inventory_df, velocity_analysis=velocity_analysis, inbound_skus=inbound_skus, item_master_df=item_master_data)
            
            log_file.write(f'Inventory Data rows: {len(inventory_data)}\n')

        # The rest - mostly outbound related
        if self.transform_options.process_outbound_data:
            order_velocity_combinations = self.create_order_velocity_combinations(project_num=self.project_number, outbound_df=outbound_data[['OrderNumber', 'Velocity']])
            velocity_summary = self.create_velocity_summary(project_num=self.project_number, velocity_analysis_df=velocity_analysis, inventory_df=inventory_data)
            outbound_data_by_order = self.create_outbound_data_by_order(project_num=self.project_number, outbound_df=outbound_data)
            daily_order_profile_by_velocity = self.create_daily_order_profile_by_velocity(project_num=self.project_number, outbound_df=outbound_data, velocity_summary=velocity_summary)    
            velocity_by_month = self.create_velocity_by_month(project_num=self.project_number, outbound_df=outbound_data, velocity_analysis=velocity_analysis)
            project_number_velocity = self.create_project_number_velocity(project_num=self.project_number)
            project_number_order_number = self.create_project_number_order_number(project_num=self.project_number, order_numbers=order_nums)
            velocity_ladder = self.create_velocity_ladder(project_num=self.project_number, velocity_analysis=velocity_analysis)

            log_file.write(f'Order Velocity Combinations rows: {len(order_velocity_combinations)}\n')
            log_file.write(f'Velocity Summary rows: {len(velocity_summary)}\n')
            log_file.write(f'Outbound Data by Order rows: {len(outbound_data_by_order)}\n')
            log_file.write(f'Daily Order Profile rows: {len(daily_order_profile_by_velocity)}\n')
            log_file.write(f'Velocity by Month rows: {len(velocity_by_month)}\n')
            log_file.write(f'Project Number - Velocity rows: {len(project_number_velocity)}\n')
            log_file.write(f'Project Number - Order Number rows: {len(project_number_order_number)}\n')
            log_file.write(f'Velocity Ladder rows: {len(velocity_ladder)}\n')

        # Reorder columns to match sql queries
        item_master_data = item_master_data.reindex(columns=OUTPUT_TABLES_COLS_MAPPER['ItemMaster'])
        inbound_header = inbound_header.reindex(columns=OUTPUT_TABLES_COLS_MAPPER['InboundHeader'])
        inbound_details = inbound_details.reindex(columns=OUTPUT_TABLES_COLS_MAPPER['InboundDetails'])
        outbound_data = outbound_data.reindex(columns=OUTPUT_TABLES_COLS_MAPPER['OutboundData'])
        order_velocity_combinations = order_velocity_combinations.reindex(columns=OUTPUT_TABLES_COLS_MAPPER['OrderVelocityCombinations'])
        inventory_data = inventory_data.reindex(columns=OUTPUT_TABLES_COLS_MAPPER['InventoryData'])
        velocity_summary = velocity_summary.reindex(columns=OUTPUT_TABLES_COLS_MAPPER['VelocitySummary'])
        outbound_data_by_order = outbound_data_by_order.reindex(columns=OUTPUT_TABLES_COLS_MAPPER['OutboundDataByOrder'])
        daily_order_profile_by_velocity = daily_order_profile_by_velocity.reindex(columns=OUTPUT_TABLES_COLS_MAPPER['DailyOrderProfileByVelocity'])
        velocity_by_month = velocity_by_month.reindex(columns=OUTPUT_TABLES_COLS_MAPPER['VelocityByMonth'])
        project_number_velocity = project_number_velocity.reindex(columns=OUTPUT_TABLES_COLS_MAPPER['ProjectNumber_Velocity'])
        project_number_order_number = project_number_order_number.reindex(columns=OUTPUT_TABLES_COLS_MAPPER['ProjectNumber_OrderNumber'])
        velocity_ladder = velocity_ladder.reindex(columns=OUTPUT_TABLES_COLS_MAPPER['VelocityLadder'])

        et = time()
        print(f'Output table creation time: {timedelta(seconds=et-st)}')
        log_file.write(f'Output table creation time: {timedelta(seconds=et-st)}\n\n')
        

        ''' STEP 2: Insert into database '''

        log_file.write(f'3. INSERT TO DATABASE\n')
        insert_st = time()

        # Get SQL file mapper
        SQL_FILE_MAPPER = DEV_OUTPUT_TABLES_INSERT_SQL_FILES_MAPPER if self.dev else OUTPUT_TABLES_INSERT_SQL_FILES_MAPPER

        # IDEA - keep track, in data_profiler, of tables that have been inserted. so, if there's an error halfway thru, it could
            # pick up where it left off. For now, just delete
        try:
            with DatabaseConnection(dev=self.dev) as db_conn:
                # FIRST - primary key tables
                rows = self.insert_table_to_db(log_file=log_file, connection=db_conn, table_name='ItemMaster', data_frame=item_master_data, sql_file_path=SQL_FILE_MAPPER['ItemMaster'])
                total_rows_inserted += rows
                rows_inserted_obj.skus = rows
                                        
                rows = self.insert_table_to_db(log_file=log_file, connection=db_conn, table_name='InboundHeader', data_frame=inbound_header, sql_file_path=SQL_FILE_MAPPER['InboundHeader'])
                total_rows_inserted += rows
                rows_inserted_obj.inbound_pos = rows

                total_rows_inserted += self.insert_table_to_db(log_file=log_file, connection=db_conn, table_name='ProjectNumber_Velocity', data_frame=project_number_velocity, sql_file_path=SQL_FILE_MAPPER['ProjectNumber_Velocity'])

                rows = self.insert_table_to_db(log_file=log_file, connection=db_conn, table_name='ProjectNumber_OrderNumber', data_frame=project_number_order_number, sql_file_path=SQL_FILE_MAPPER['ProjectNumber_OrderNumber'])
                total_rows_inserted += rows
                rows_inserted_obj.outbound_orders = rows
                
                # THEN - the rest
                rows = self.insert_table_to_db(log_file=log_file, connection=db_conn, table_name='InboundDetails', data_frame=inbound_details, sql_file_path=SQL_FILE_MAPPER['InboundDetails'])
                total_rows_inserted += rows
                rows_inserted_obj.inbound_lines = rows

                rows = self.insert_table_to_db(log_file=log_file, connection=db_conn, table_name='InventoryData', data_frame=inventory_data, sql_file_path=SQL_FILE_MAPPER['InventoryData'])
                total_rows_inserted += rows
                rows_inserted_obj.inventory_lines = rows

                rows = self.insert_table_to_db(log_file=log_file, connection=db_conn, table_name='OutboundData', data_frame=outbound_data, sql_file_path=SQL_FILE_MAPPER['OutboundData'])
                total_rows_inserted += rows
                rows_inserted_obj.outbound_lines = rows

                total_rows_inserted += self.insert_table_to_db(log_file=log_file, connection=db_conn, table_name='OutboundDataByOrder', data_frame=outbound_data_by_order, sql_file_path=SQL_FILE_MAPPER['OutboundDataByOrder'])
                total_rows_inserted += self.insert_table_to_db(log_file=log_file, connection=db_conn, table_name='OrderVelocityCombinations', data_frame=order_velocity_combinations, sql_file_path=SQL_FILE_MAPPER['OrderVelocityCombinations'])
                total_rows_inserted += self.insert_table_to_db(log_file=log_file, connection=db_conn, table_name='VelocitySummary', data_frame=velocity_summary, sql_file_path=SQL_FILE_MAPPER['VelocitySummary'])
                total_rows_inserted += self.insert_table_to_db(log_file=log_file, connection=db_conn, table_name='VelocityLadder', data_frame=velocity_ladder, sql_file_path=SQL_FILE_MAPPER['VelocityLadder'])
                total_rows_inserted += self.insert_table_to_db(log_file=log_file, connection=db_conn, table_name='VelocityByMonth', data_frame=velocity_by_month, sql_file_path=SQL_FILE_MAPPER['VelocityByMonth'])
                total_rows_inserted += self.insert_table_to_db(log_file=log_file, connection=db_conn, table_name='DailyOrderProfileByVelocity', data_frame=daily_order_profile_by_velocity, sql_file_path=SQL_FILE_MAPPER['DailyOrderProfileByVelocity'])

        # https://peps.python.org/pep-0249/#exceptions
        except InterfaceError as e:
            # Base error class for interfacing (e.g., connecting) to database
            print(e)
            log_file.write(f'ERROR - Could not connect to database. Quitting.\n\n')
            transform_response.success = False
            transform_response.message = 'Could not connect to database.'
        except DatabaseError as e:
            # Base error class for database related errors
            print(e)
            log_file.write(f'ERROR - {e}\n\n')
            transform_response.success = False
            transform_response.message = 'Something went wrong when inserting data to database. Check log.'
        else:
            rows_inserted_obj.total_rows_inserted = total_rows_inserted

            transform_response.success = True
            transform_response.message = 'Successful transform and insertion.'
            transform_response.rows_inserted = rows_inserted_obj

            insert_et = time()
            log_file.write(f'Success! Inserted {total_rows_inserted} rows in {timedelta(seconds=insert_et-insert_st)}\n\n')

        return transform_response

    # NOTE - this maybe should exist somewhere else in future
    def insert_table_to_db(self, connection: Connection, table_name: str, data_frame: pd.DataFrame, sql_file_path: str, log_file: TextIOWrapper) -> int:
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
        fd = open(f'{self.sql_dir}/{sql_file_path}')
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


    ''' Create Table Functions '''

    def create_item_master(self, project_num: str, item_master: pd.DataFrame) -> pd.DataFrame:
        print(f'creating item master...')

        item_master_return = item_master.copy(deep=True)
        item_master_return['Subwarehouse'] = item_master['Subwarehouse'].astype(str)
        item_master_return['ProjectNumber_SKU'] = project_num + '-' + item_master_return['SKU'].astype(str)
        item_master_return['ProjectNumber'] = project_num

        # Strip description of some characters
        item_master_return['SKUDescription'] = item_master_return['SKUDescription'].astype(str)
        bad_characters = [r'"',r"'",r'\t',r'\n',r'<',r'>']
        for c in bad_characters:
            rgx = re.compile(pattern=c, flags=re.IGNORECASE)
            item_master_return['SKUDescription'] = item_master_return['SKUDescription'].str.replace(pat=rgx, repl='', regex=True)

        item_master_return['EachCube'] = round((item_master_return['EachLength'].astype(float) * item_master_return['EachWidth'].astype(float) * item_master_return['EachHeight'].astype(float))/(12*12*12),2)
        item_master_return['InnerCube'] = round((item_master_return['InnerLength'].astype(float) * item_master_return['InnerWidth'].astype(float) * item_master_return['InnerHeight'].astype(float))/(12*12*12),2)
        item_master_return['CartonCube'] = round((item_master_return['CartonLength'].astype(float) * item_master_return['CartonWidth'].astype(float) * item_master_return['CartonHeight'].astype(float))/(12*12*12),2)
        item_master_return['PalletCube'] = round((item_master_return['PalletLength'].astype(float) * item_master_return['PalletWidth'].astype(float) * item_master_return['PalletHeight'].astype(float))/(12*12*12),2)
        
        # Fill in any nulls cells with empty string
        item_master_return.replace(to_replace=pd.NA, value='', inplace=True)

        return item_master_return

    def create_inbound_header(self, project_num: str, inbound_header_df: pd.DataFrame, inbound_details_df: pd.DataFrame) -> pd.DataFrame:
        if len(inbound_header_df) == 0:
            print(f'No inbound data. Skipping inbound header')
            return inbound_header_df
        
        print(f'creating inbound header...')
        '''ProjectNumber PO_Number ArrivalDate ArrivalTime ExpectedDate ExpectedTime Carrier  Mode'''
        
        inbound_header = inbound_header_df.copy(deep=True)
        
        # Aggregate InboundDetails
        inbound_by_receipt = inbound_details_df.groupby('PO_Number').aggregate(
            Lines=('PO_Number', 'size'), 
            Units=('Quantity', 'sum'),
            SKUs=('SKU', 'nunique')
        ).reset_index()

        inbound_header = inbound_header.merge(inbound_by_receipt, on='PO_Number', how='left')

        # Adjust weekend dates
        inbound_header = self.adjust_weekend_dates(inbound_header, 'ArrivalDate')

        # Add ProjectNumber_SKU, ProjectNumber_PO_Number
        inbound_header['ProjectNumber'] = project_num
        inbound_header['ProjectNumber_PO_Number'] = project_num + '-' + inbound_header['PO_Number'].astype(str)

        return inbound_header

    def create_inbound_details(self, project_num: str, inbound_details_df: pd.DataFrame, item_master_df: pd.DataFrame) -> pd.DataFrame: # , transform_options: TransformOptions) -> pd.DataFrame:
        if len(inbound_details_df) == 0:
            print(f'No inbound data. Skipping inbound details')
            return inbound_details_df
        
        print(f'creating inbound details...')
        '''ProjectNumber PO_Number   SKU UnitOfMeasure  Quantity VendorID SourcePoint'''
        
        inbound_details = inbound_details_df.copy(deep=True)

        # Apply line cube and weight
        inbound_details = inbound_details.merge(item_master_df[['SKU', 'EachCube', 'InnerCube', 'CartonCube', 'PalletCube', 
                                                            'EachWeight', 'InnerWeight', 'CartonWeight', 'PalletWeight']],
                                                    how='left',
                                                    on='SKU')
        
        inbound_details['LineCube'] = inbound_details.apply(lambda x: self.calc_line_cube(row=x), axis=1)
        inbound_details['LineWeight'] = inbound_details.apply(lambda x: self.calc_line_weight(row=x), axis=1)

        # Add ProjectNumber_SKU, ProjectNumber_PO_Number
        inbound_details['ProjectNumber_SKU'] = project_num + '-' + inbound_details['SKU'].astype(str)
        inbound_details['ProjectNumber_PO_Number'] = project_num + '-' + inbound_details['PO_Number'].astype(str)

        return inbound_details

    def create_outbound_data(self, project_num: str, order_header_df: pd.DataFrame, order_details_df: pd.DataFrame, item_master_df: pd.DataFrame) -> pd.DataFrame: #, transform_options: TransformOptions)         
        print(f'creating outbound data...')

        # Join Order Details and Order Header to form Outbound Data
        outbound_data = order_details_df.merge(order_header_df, on='OrderNumber', how='left')

        if len(outbound_data) == 0:
            print(f'No order data. Skipping outbound data')
            return outbound_data

        # Make sure dates are actually dates
        outbound_data['ShipDate'] = pd.to_datetime(outbound_data['ShipDate'], dayfirst=True, format='mixed')
        outbound_data['PickDate'] = pd.to_datetime(outbound_data['PickDate'], dayfirst=True, format='mixed')
        outbound_data['ReceivedDate'] = pd.to_datetime(outbound_data['ReceivedDate'], dayfirst=True, format='mixed')

        # Set Date = chosen date for analysis
        if self.transform_options.date_for_analysis == DateForAnalysis.RECEIVED_DATE:
            outbound_data['Date'] = outbound_data[DateForAnalysis.RECEIVED_DATE]
        elif self.transform_options.date_for_analysis == DateForAnalysis.PICK_DATE:
            outbound_data['Date'] = outbound_data[DateForAnalysis.PICK_DATE]
        elif self.transform_options.date_for_analysis == DateForAnalysis.SHIP_DATE:
            outbound_data['Date'] = outbound_data[DateForAnalysis.SHIP_DATE]

        # Adjust weekend dates
        outbound_data = self.adjust_weekend_dates(outbound_data, 'Date')

        # Add weekday
        outbound_data['Weekday'] = outbound_data['Date'].dt.day_name()
        weekday_sort = self.get_weekday_sort_df()
        outbound_data = outbound_data.merge(weekday_sort, on='Weekday', how='left')

        # Add week
        outbound_data['Week_Number'] = outbound_data['Date'].dt.isocalendar().week
        outbound_data['Week'] = outbound_data['Date'] - pd.to_timedelta(outbound_data['Date'].dt.dayofweek, unit='d')

        # Add Units per Line range to Outbound Data
        upl_ranges = [(0,1), (1,2), (2,5), (5,10),(10,'max')]
        outbound_data['UnitsPerLineRange'] = outbound_data['Quantity'].apply(lambda x: self.find_range(x, upl_ranges))

        # Add ProjectNumber_SKU, ProjectNumber_OrderNumber
        outbound_data['ProjectNumber_SKU'] = project_num + '-' + outbound_data['SKU'].astype(str)
        outbound_data['ProjectNumber_OrderNumber'] = project_num + '-' + outbound_data['OrderNumber'].astype(str)

        ''' Add LineCube and LineWeight '''
        # Add cube and weight info to outbound
        outbound_data = outbound_data.merge(item_master_df[['SKU', 'EachCube', 'InnerCube', 'CartonCube', 'PalletCube', 
                                                            'EachWeight', 'InnerWeight', 'CartonWeight', 'PalletWeight']],
                                            how='left',
                                            on='SKU')

        # Add line weight and cube using appropriate info from item master
        outbound_data['LineCube'] = outbound_data.apply(lambda x: self.calc_line_cube(row=x), axis=1)
        outbound_data['LineWeight'] = outbound_data.apply(lambda x: self.calc_line_weight(row=x), axis=1)
        
        # Fill in any nulls cells with empty string
        outbound_data.replace(to_replace=pd.NA, value='', inplace=True)

        return outbound_data

    def create_order_velocity_combinations(self, project_num: str, outbound_df: pd.DataFrame) -> pd.DataFrame:
        if len(outbound_df) == 0:
            print(f'No order data. Skipping order velocity combinations')
            return outbound_df

        print(f'creating order velocity combinations...')

        order_velocity_combos = outbound_df.groupby('OrderNumber').agg(velocity_set=('Velocity', 'unique')).reset_index()
        order_velocity_combos['VelocityCombination'] = order_velocity_combos['velocity_set'].apply(lambda x: ''.join(sorted(x)))

        # Add ProjectNumber_OrderNumber
        order_velocity_combos['ProjectNumber_OrderNumber'] = project_num + '-' + order_velocity_combos['OrderNumber'].astype(str)

        # Fill in any nulls cells with empty string
        order_velocity_combos.replace(to_replace=pd.NA, value='', inplace=True)
        
        return order_velocity_combos[['ProjectNumber_OrderNumber', 'OrderNumber', 'VelocityCombination']]

    def create_inventory_data(self, project_num: str, inventory_df: pd.DataFrame, velocity_analysis: pd.DataFrame, inbound_skus: set, item_master_df: pd.DataFrame) -> pd.DataFrame:
        if len(inventory_df) == 0:
            print(f'No inventory data. Skipping inventory')
            return inventory_df
        
        print(f'creating inventory...')

        # Add velocity. Fill in any inactive SKUs with "X" for velocity
        inventory_data = inventory_df.merge(velocity_analysis[['SKU', 'Velocity']], on='SKU', how='left')
        inventory_data['Velocity'] = inventory_data['Velocity'].fillna(value='X')

        # TODO - this will eventually be "ExistsInInbound"
        inventory_data['ExistsInInbound'] = np.where(inventory_data['SKU'].isin(inbound_skus), True, False)
        inventory_data['Period'] = pd.to_datetime(inventory_data['Period'], dayfirst=True, format='mixed')

        # Add ProjectNumber_SKU
        inventory_data['ProjectNumber_SKU'] = project_num + '-' + inventory_data['SKU'].astype(str)

        ''' Add LineCube and LineWeight '''
        # Add cube and weight info to outbound
        inventory_data = inventory_data.merge(item_master_df[['SKU', 'EachCube', 'InnerCube', 'CartonCube', 'PalletCube', 
                                                            'EachWeight', 'InnerWeight', 'CartonWeight', 'PalletWeight']],
                                            how='left',
                                            on='SKU')

        # Add line weight and cube using appropriate info from item master
        inventory_data['LineCube'] = inventory_data.apply(lambda x: self.calc_line_cube(row=x), axis=1)
        inventory_data['LineWeight'] = inventory_data.apply(lambda x: self.calc_line_weight(row=x), axis=1)

        # Fill in any nulls cells with empty string
        inventory_data.replace(to_replace=pd.NA, value='', inplace=True)

        return inventory_data

    def create_velocity_summary(self, project_num: str, velocity_analysis_df: pd.DataFrame, inventory_df: pd.DataFrame) -> pd.DataFrame:
        if len(velocity_analysis_df) == 0:
            print(f'No order data. Skipping velocity summary')
            return pd.DataFrame()
        
        print(f'creating velocity summary...')

        # Group velocity analysis to summarize by velocity
        velocity_summary = velocity_analysis_df.groupby('Velocity').agg(ActiveSKUs=('SKU', 'nunique'), Lines=('Lines', 'sum'), Units=('Units', 'sum')).reset_index()
        
        # If processing inventory, summarize inventory by velocity and add it back
        if self.transform_options.process_inventory_data:
            inventory_by_velocity = inventory_df.groupby('Velocity').agg(OnHandSKUs=('SKU', 'nunique'), QtyOnHand=('Quantity', 'sum')).reset_index()   
            velocity_summary = velocity_summary.merge(inventory_by_velocity, on='Velocity', how='left').fillna(value=0)

        # Velocity -> ProjectNumber_Velocity
        velocity_summary['ProjectNumber_Velocity'] = project_num + '-' + velocity_summary['Velocity'].astype(str)

        # Fill in any nulls cells with empty string
        velocity_summary.replace(to_replace=pd.NA, value='', inplace=True)

        return velocity_summary

    def create_outbound_data_by_order(self, project_num: str, outbound_df: pd.DataFrame) -> pd.DataFrame:
        if len(outbound_df) == 0:
            print(f'No order data. Skipping outbound by order')
            return pd.DataFrame()
        
        print(f'creating outbound data by order...')

        outbound_by_order = outbound_df.groupby('OrderNumber').agg(Date=('Date', 'first'), Lines=('Date', 'size'),\
                                                                Units=('Quantity', 'sum'), SKUs=('SKU', 'nunique')).reset_index()

        # Add ranges
        lpo_ranges = [(0,1), (1,2), (2,5), (5,10),(10,20),(20,50),(50,'max')]
        upo_ranges = [(0,1), (1,5), (5,10), (10,20),(20,50),(50,100),(100,'max')]
        outbound_by_order['LinesPerOrderRange'] = outbound_by_order['Lines'].apply(lambda x: self.find_range(x, lpo_ranges))
        outbound_by_order['UnitsPerOrderRange'] = outbound_by_order['Units'].apply(lambda x: self.find_range(x, upo_ranges))

        # Ensure correct date format
        outbound_by_order['Date'] = pd.to_datetime(outbound_by_order['Date'], dayfirst=True, format='mixed')

        # Add weekday
        outbound_by_order['Weekday'] = outbound_by_order['Date'].dt.day_name()
        weekday_sort = self.get_weekday_sort_df()
        outbound_by_order = outbound_by_order.merge(weekday_sort, on='Weekday', how='left')

        # Add ProjectNumber_OrderNumber
        outbound_by_order['ProjectNumber_OrderNumber'] = project_num + '-' + outbound_by_order['OrderNumber'].astype(str)

        # Fill in any nulls cells with empty string
        outbound_by_order.replace(to_replace=pd.NA, value='', inplace=True)

        return outbound_by_order

    def create_daily_order_profile_by_velocity(self, project_num: str, outbound_df: pd.DataFrame, velocity_summary: pd.DataFrame) -> pd.DataFrame:
        if len(outbound_df) == 0:
            print(f'No order data. Skipping daily order profile')
            return pd.DataFrame()
        
        print(f'creating daily order profile...')

        outbound_by_day_velocity = outbound_df.groupby(by=['Date', 'Velocity']).agg(Orders=('OrderNumber', 'nunique'), Lines=('Date', 'size'),
                                                            Units=('Quantity', 'sum'), SKUs=('SKU', 'nunique')).reset_index()

        daily_order_profile = outbound_by_day_velocity.groupby('Velocity').agg(AvgDailySKUs=('SKUs', 'mean'), AvgDailyOrders=('Orders', 'mean'), \
                                                                            AvgDailyLines=('Lines', 'mean'), AvgDailyUnits=('Units', 'mean'), \
                                                                                DailySKUsSD=pd.NamedAgg('SKUs', lambda x: x.std(ddof=0)), \
                                                                                DailyOrdersSD=pd.NamedAgg('Orders', lambda x: x.std(ddof=0)), \
                                                                                DailyLinesSD=pd.NamedAgg('Lines', lambda x: x.std(ddof=0)), \
                                                                                DailyUnitsSD=pd.NamedAgg('Units', lambda x: x.std(ddof=0))).reset_index()

        # Add "+1SD" columns
        for field in ['SKUs', 'Orders', 'Lines', 'Units']:
            avg_col = f'AvgDaily{field}'
            std_col = f'Daily{field}SD'
            new_col = f'+1StDev{field}'

            daily_order_profile[new_col] = daily_order_profile[avg_col] + daily_order_profile[std_col]

        # Add totals from Velocity Summary
        # TODO - can delete (redundant). Can add back in BI
        daily_order_profile = daily_order_profile.merge(velocity_summary[['Velocity', 'ActiveSKUs', 'OnHandSKUs', 'QtyOnHand']], on='Velocity', how='left').fillna(value=0)

        # Add ProjectNumber_Velocity
        daily_order_profile['ProjectNumber_Velocity'] = project_num + '-' + daily_order_profile['Velocity'].astype(str)

        # Fill in any nulls cells with empty string
        daily_order_profile.replace(to_replace=pd.NA, value='', inplace=True)

        return daily_order_profile.round(decimals=2)

    def create_velocity_by_month(self, project_num: str, outbound_df: pd.DataFrame, velocity_analysis: pd.DataFrame) -> pd.DataFrame:
        if len(outbound_df) == 0:
            print(f'No order data. Skipping velocity by month')
            return pd.DataFrame()
        
        print(f'creating velocity by month...')
        
        OUTBOUND_SKUS = set(outbound_df['SKU'].unique().tolist())
        
        # Months
        outbound_df.sort_values('Date', inplace=True)
        outbound_df['Month-Year'] = outbound_df['Date'].dt.month_name() + '-' + outbound_df['Date'].dt.year.astype(str)
        months_in_data = outbound_df['Month-Year'].unique().tolist()

        # Create DF
        velocity_by_month = pd.DataFrame()

        # Run velocity analysis for each month
        skus = []
        month_list = []
        velocities = []
        for month in months_in_data:

            month_data = outbound_df.loc[outbound_df['Month-Year'] == month,:]
            month_velocity_df = self.run_velocity_analysis(month_data)
            skus_list = month_velocity_df['SKU'].tolist()
            month_skus_set = set(skus_list)
            velocities_list = month_velocity_df['Velocity'].tolist()

            # add skus that weren't active this month
            for sku in OUTBOUND_SKUS:
                if sku not in month_skus_set:
                    skus_list.append(sku)
                    velocities_list.append('X')

            skus.extend(skus_list)
            month_list.extend([month for i in range(len(OUTBOUND_SKUS))])
            velocities.extend(velocities_list)

        velocity_by_month['SKU'] = skus
        velocity_by_month['Month'] = month_list
        velocity_by_month['Velocity'] = velocities

        # Add Overall Velocity
        velocity_by_month = velocity_by_month.merge(velocity_analysis[['SKU', 'Velocity']].rename(columns={
                                    'Velocity': 'Velocity_Overall'}), on='SKU', how='left')
        velocity_by_month['EqualsOverall'] = np.where(velocity_by_month['Velocity'] == velocity_by_month['Velocity_Overall'], 1, 0)

        # Add ProjectNumber_SKU
        velocity_by_month['ProjectNumber_SKU'] = project_num + '-' + velocity_by_month['SKU'].astype(str)

        # Fill in any nulls cells with empty string
        velocity_by_month.replace(to_replace=pd.NA, value='', inplace=True)

        return velocity_by_month

    def create_project_number_velocity(self, project_num: str) -> pd.DataFrame:       
        print(f'creating project number velocity...')

        projectnum_velocity = pd.DataFrame(columns=['ProjectNumber_Velocity', 'ProjectNumber', 'Velocity'])
        projectnum_velocity['Velocity'] = ['A', 'B', 'C', 'D', 'E']
        projectnum_velocity['ProjectNumber'] = project_num
        projectnum_velocity['ProjectNumber_Velocity'] = project_num + '-' + projectnum_velocity['Velocity'].astype(str)

        # Fill in any nulls cells with empty string
        projectnum_velocity.replace(to_replace=pd.NA, value='', inplace=True)

        return projectnum_velocity

    def create_project_number_order_number(self, project_num: str, order_numbers: list) -> pd.DataFrame:
        if len(order_numbers) == 0:
            print(f'No order data. Skipping project number order number')
            return pd.DataFrame()
        
        print(f'creating project number order number...')

        projectnum_ordernum = pd.DataFrame(columns=['ProjectNumber_OrderNumber', 'ProjectNumber', 'OrderNumber'])
        projectnum_ordernum['OrderNumber'] = order_numbers
        projectnum_ordernum['ProjectNumber'] = project_num
        projectnum_ordernum['ProjectNumber_OrderNumber'] = project_num + '-' + projectnum_ordernum['OrderNumber'].astype(str)

        # Fill in any nulls cells with empty string
        projectnum_ordernum.replace(to_replace=pd.NA, value='', inplace=True)

        return projectnum_ordernum

    def create_velocity_ladder(self, project_num: str, velocity_analysis: pd.DataFrame) -> pd.DataFrame:
        if len(velocity_analysis) == 0:
            print(f'No order data. Skipping velocity ladder')
            return pd.DataFrame()

        print(f'creating velocity ladder...')

        velocity_ladder = velocity_analysis.copy(deep=True)

        # Find %Lines groups
        velocity_ladder['pct lines'] = velocity_ladder['Lines_RunningSum'] / velocity_ladder['Lines'].sum() 
        velocity_ladder['%Lines'] = np.ceil(velocity_ladder['pct lines'] / 0.05) * 0.05

        # Group by %Lines and aggregate
        velocity_ladder = velocity_ladder.groupby('%Lines').agg(SKUs=('SKU', 'nunique'), Lines=('Lines', 'sum'), Units=('Units', 'sum'),
                                                                Velocity=('Velocity', 'first')).reset_index()
        velocity_ladder['SKUs_RunningSum'] = velocity_ladder['SKUs'].cumsum()
        velocity_ladder['Lines_RunningSum'] = velocity_ladder['Lines'].cumsum()
        velocity_ladder['Units_RunningSum'] = velocity_ladder['Units'].cumsum()

        # Add percentages
        velocity_ladder['%SKUs'] = velocity_ladder['SKUs_RunningSum'] / velocity_ladder['SKUs'].sum()
        velocity_ladder['%Units'] = velocity_ladder['Units_RunningSum'] / velocity_ladder['Units'].sum()
        velocity_ladder = velocity_ladder.round(2)

        # Add ProjectNumber_Velocity
        velocity_ladder['ProjectNumber_Velocity'] = project_num + '-' + velocity_ladder['Velocity']

        # Fill in any nulls cells with empty string
        velocity_ladder.replace(to_replace=pd.NA, value='', inplace=True)

        return velocity_ladder


    ''' Helpers '''

    # Given a number n, find the range it belongs to
    # Range in Tuple form: (range min, range max)
    def find_range(self, n, rng) -> str:
        for r in rng:
            range_str = ''
            if r[1] == 'max': 
                range_str = f'>{r[0]}'
                if n > r[0]:
                    return range_str
            else:
                if r[0]+1 == r[1]: 
                    range_str = f'{r[1]}'
                else: 
                    range_str = f'{r[0]+1}-{r[1]}'
                if n > r[0] and n <= r[1]:
                    return range_str
        return ''

    # Return velocity of SKU by dividing its running sum of lines by total lines
    def find_velocity(self, rsum_lines, total_lines) -> str:
        percent_lines = rsum_lines / total_lines
        if percent_lines <= 0.25:
            return 'A'
        elif percent_lines <= 0.8:
            return 'B'
        elif percent_lines <= 0.95:
            return 'C'
        elif percent_lines <= 0.99:
            return 'D'
        else: 
            return 'E'
        
    # Run velocity analysis on outbound data set
    # @Params: 
    #       outbound_df: pd.DataFrame    required columns: SKU, Quantity
    # @Return: 
    #       pd.DataFrame, columns: SKU, Velocity
    def run_velocity_analysis(self, outbound_df: pd.DataFrame) -> pd.DataFrame:
        total_lines = len(outbound_df)

        velocity_analysis = outbound_df.groupby('SKU').agg(Lines=('SKU', 'size'), Units=('Quantity', 'sum')).sort_values(by='Lines', ascending=False).reset_index()
        velocity_analysis['Lines_RunningSum'] = velocity_analysis['Lines'].cumsum()
        velocity_analysis['Velocity'] = velocity_analysis['Lines_RunningSum'].apply(lambda x: self.find_velocity(x, total_lines))
        
        return velocity_analysis

    # Returns dataframe with indices for weekdays
    def get_weekday_sort_df(self) -> pd.DataFrame:
        return pd.DataFrame({'Weekday': ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'],
                            'Weekday_Idx': [1,2,3,4,5,6,7]})

    def calc_line_cube(self, row):
        uom = row['UnitOfMeasure']
        quantity = row['Quantity']

        return row[f'{uom}Cube'] * quantity
        
    def calc_line_weight(self, row):
        uom = row['UnitOfMeasure']
        quantity = row['Quantity']

        return row[f'{uom}Weight'] * quantity

    def adjust_weekend_dates(self, df: pd.DataFrame, date_col: str):
        # Adjust weekend dates
        if self.transform_options.weekend_date_rule == WeekendDateRules.NEAREST_WEEKDAY:
            df[date_col] = np.where(df[date_col].dt.day_name() == 'Saturday', df[date_col] - timedelta(days=1), df[date_col])   # to friday
            df[date_col] = np.where(df[date_col].dt.day_name() == 'Sunday', df[date_col] + timedelta(days=1), df[date_col])     # to monday
        elif self.transform_options.weekend_date_rule == WeekendDateRules.ALL_TO_MONDAY:
            df[date_col] = np.where(df[date_col].dt.day_name() == 'Saturday', df[date_col] + timedelta(days=2), df[date_col])
            df[date_col] = np.where(df[date_col].dt.day_name() == 'Sunday', df[date_col] + timedelta(days=1), df[date_col])
        elif self.transform_options.weekend_date_rule == WeekendDateRules.ALL_TO_FRIDAY:
            df[date_col] = np.where(df[date_col].dt.day_name() == 'Saturday', df[date_col] - timedelta(days=1), df[date_col])
            df[date_col] = np.where(df[date_col].dt.day_name() == 'Sunday', df[date_col] - timedelta(days=2), df[date_col])
        elif self.transform_options.weekend_date_rule == WeekendDateRules.AS_IS:
            pass

        return df