'''
Jack Miller
Apex Companies
Oct 2024

Database constants. File paths/mappers for queries and column names for tables 
'''

###########
### ALL ###
###########

SCHEMAS = {
    'OutputTables_Dev': {
        'tables':  ['Project', 'ItemMaster', 'InboundHeader', 'ProjectNumber_Velocity', 'ProjectNumber_OrderNumber', 'InboundDetails', 'InventoryData',
                    'OutboundData', 'OutboundDataByOrder', 'OrderVelocityCombinations', 'VelocitySummary', 'VelocityLadder',
                    'VelocityByMonth', 'DailyOrderProfileByVelocity']
    },
    'OutputTables_Prod': {
        'tables': ['Project', 'ItemMaster', 'InboundHeader', 'ProjectNumber_Velocity', 'ProjectNumber_OrderNumber', 'InboundDetails', 'InventoryData',
                    'OutboundData', 'OutboundDataByOrder', 'OrderVelocityCombinations', 'VelocitySummary', 'VelocityLadder',
                    'VelocityByMonth', 'DailyOrderProfileByVelocity']
    }
}


#####################
### OUTPUT_TABLES ###
#####################

OUTPUT_TABLES_ITEM_MASTER_COLS = ['ProjectNumber_SKU','ProjectNumber','SKU','SKUDescription','SKUClass','UnitOfMeasure','Velocity','EachLength','EachWidth','EachHeight','EachWeight',
                                  'InnerQuantity','InnerLength','InnerWidth','InnerHeight','InnerWeight','CartonQuantity','CartonLength','CartonWidth','CartonHeight',
                                  'CartonWeight','CartonsPerPallet','PalletTie','PalletHigh','MaxPalletStack','PalletLength','PalletWidth','PalletHeight','PalletWeight','Subwarehouse']
OUTPUT_TABLES_OUTBOUND_DATA_COLS = ['ProjectNumber_SKU','Quantity','ReceivedDate','PickDate','ShipDate','Channel','Velocity','UnitsPerLineRange','Weekday','Week','Weekday_Idx','ProjectNumber_OrderNumber','Date','Week_Number', 'LineCube', 'LineWeight', 'UnitOfMeasure', 'BusinessUnit', 'ShipContainerType', 'SpecialHandlingCodes', 'Carrier']
OUTPUT_TABLES_ORDER_VELOCITY_COMBINATIONS_COLS = ['ProjectNumber_OrderNumber','VelocityCombination']
OUTPUT_TABLES_INBOUND_HEADER_COLS = ['ProjectNumber_ReceiptNumber','ProjectNumber','ReceiptNumber','ArrivalDate','ArrivalTime','ExpectedDate','ExpectedTime','Carrier','Mode','Lines','Units','SKUs']
OUTPUT_TABLES_INBOUND_DETAILS_COLS = ['ProjectNumber_ReceiptNumber','ProjectNumber_SKU','UnitOfMeasure','Quantity','VendorID','SourcePoint','LineCube','LineWeight']
OUTPUT_TABLES_INVENTORY_DATA_COLS = ['Period','ProjectNumber_SKU','UnitOfMeasure','Quantity','Subwarehouse','Velocity','ExistsInOutbound','Location','Lot','LineCube','LineWeight']
OUTPUT_TABLES_VELOCITY_SUMMARY_COLS = ['ProjectNumber_Velocity','ActiveSKUs','Lines','Units','OnHandSKUs','QtyOnHand']
OUTPUT_TABLES_OUTBOUND_DATA_BY_ORDER_COLS = ['Date','Lines','Units','SKUs','LinesPerOrderRange','UnitsPerOrderRange','Weekday','Weekday_Idx','ProjectNumber_OrderNumber']
OUTPUT_TABLES_DAILY_ORDER_PROFILE_BY_VELOCITY_COLS = ['ProjectNumber_Velocity','AvgDailySKUs','AvgDailyOrders','AvgDailyLines','AvgDailyUnits','DailySKUsSD','DailyOrdersSD','DailyLinesSD','DailyUnitsSD','ActiveSKUs','OnHandSKUs','QtyOnHand','+1StDevSKUs','+1StDevOrders','+1StDevLines','+1StDevUnits']
OUTPUT_TABLES_VELOCITY_BY_MONTH_COLS = ['ProjectNumber_SKU','Month','Velocity','Velocity_Overall','EqualsOverall']
OUTPUT_TABLES_PROJECT_NUMBER_VELOCITY_COLS = ['ProjectNumber_Velocity','ProjectNumber','Velocity']
OUTPUT_TABLES_PROJECT_NUMBER_ORDER_NUMBER_COLS = ['ProjectNumber_OrderNumber','ProjectNumber','OrderNumber']
OUTPUT_TABLES_VELOCITY_LADDER_COLS = ['%Lines','SKUs_RunningSum','Lines_RunningSum','Units_RunningSum','ProjectNumber_Velocity','%SKUs','Lines','Units','SKUs','%Units']

OUTPUT_TABLES_COLS_MAPPER = {
    # 'Project': OUTPUT_TABLES_SQL_FILE_INSERT_INTO_PROJECT,
    'ItemMaster': OUTPUT_TABLES_ITEM_MASTER_COLS,
    'InboundHeader': OUTPUT_TABLES_INBOUND_HEADER_COLS,
    'ProjectNumber_Velocity': OUTPUT_TABLES_PROJECT_NUMBER_VELOCITY_COLS,
    'ProjectNumber_OrderNumber': OUTPUT_TABLES_PROJECT_NUMBER_ORDER_NUMBER_COLS,
    'InboundDetails': OUTPUT_TABLES_INBOUND_DETAILS_COLS,
    'InventoryData': OUTPUT_TABLES_INVENTORY_DATA_COLS,
    'OutboundData': OUTPUT_TABLES_OUTBOUND_DATA_COLS,
    'OutboundDataByOrder': OUTPUT_TABLES_OUTBOUND_DATA_BY_ORDER_COLS,
    'OrderVelocityCombinations': OUTPUT_TABLES_ORDER_VELOCITY_COMBINATIONS_COLS,
    'VelocitySummary': OUTPUT_TABLES_VELOCITY_SUMMARY_COLS,
    'VelocityLadder': OUTPUT_TABLES_VELOCITY_LADDER_COLS,
    'VelocityByMonth': OUTPUT_TABLES_VELOCITY_BY_MONTH_COLS,
    'DailyOrderProfileByVelocity': OUTPUT_TABLES_DAILY_ORDER_PROFILE_BY_VELOCITY_COLS,
}


## Insert queries
OUTPUT_TABLES_SQL_FILE_INSERT_INTO_PROJECT = 'data_profiler/database/sql/PROD/insert/insert_into_project.sql'
OUTPUT_TABLES_SQL_FILE_INSERT_INTO_ITEM_MASTER = 'data_profiler/database/sql/PROD/insert/insert_into_item_master.sql'
OUTPUT_TABLES_SQL_FILE_INSERT_INTO_INBOUND_HEADER = 'data_profiler/database/sql/PROD/insert/insert_into_inbound_header.sql'
OUTPUT_TABLES_SQL_FILE_INSERT_INTO_PROJECT_NUMBER_VELOCITY = 'data_profiler/database/sql/PROD/insert/insert_into_project_number_velocity.sql'
OUTPUT_TABLES_SQL_FILE_INSERT_INTO_PROJECT_NUMBER_ORDER_NUMBER = 'data_profiler/database/sql/PROD/insert/insert_into_project_number_order_number.sql'
OUTPUT_TABLES_SQL_FILE_INSERT_INTO_INBOUND_DETAILS = 'data_profiler/database/sql/PROD/insert/insert_into_inbound_details.sql'
OUTPUT_TABLES_SQL_FILE_INSERT_INTO_INVENTORY_DATA = 'data_profiler/database/sql/PROD/insert/insert_into_inventory_data.sql'
OUTPUT_TABLES_SQL_FILE_INSERT_INTO_OUTBOUND_DATA = 'data_profiler/database/sql/PROD/insert/insert_into_outbound_data.sql'
OUTPUT_TABLES_SQL_FILE_INSERT_INTO_OUTBOUND_DATA_BY_ORDER = 'data_profiler/database/sql/PROD/insert/insert_into_outbound_data_by_order.sql'
OUTPUT_TABLES_SQL_FILE_INSERT_INTO_ORDER_VELOCITY_COMBINATIONS = 'data_profiler/database/sql/PROD/insert/insert_into_order_velocity_combinations.sql'
OUTPUT_TABLES_SQL_FILE_INSERT_INTO_VELOCITY_SUMMARY = 'data_profiler/database/sql/PROD/insert/insert_into_velocity_summary.sql'
OUTPUT_TABLES_SQL_FILE_INSERT_INTO_VELOCITY_LADDER = 'data_profiler/database/sql/PROD/insert/insert_into_velocity_ladder.sql'
OUTPUT_TABLES_SQL_FILE_INSERT_INTO_VELOCITY_BY_MONTH = 'data_profiler/database/sql/PROD/insert/insert_into_velocity_by_month.sql'
OUTPUT_TABLES_SQL_FILE_INSERT_INTO_DAILY_ORDER_PROFILE_BY_VELOCITY = 'data_profiler/database/sql/PROD/insert/insert_into_daily_order_profile_by_velocity.sql'


# IMPORTANT: these need to stay in INSERTION order. that is, PK tables first, then FK tables.
OUTPUT_TABLES_INSERT_SQL_FILES_MAPPER = {
    'Project': OUTPUT_TABLES_SQL_FILE_INSERT_INTO_PROJECT,
    'ItemMaster': OUTPUT_TABLES_SQL_FILE_INSERT_INTO_ITEM_MASTER,
    'InboundHeader': OUTPUT_TABLES_SQL_FILE_INSERT_INTO_INBOUND_HEADER,
    'ProjectNumber_Velocity': OUTPUT_TABLES_SQL_FILE_INSERT_INTO_PROJECT_NUMBER_VELOCITY,
    'ProjectNumber_OrderNumber': OUTPUT_TABLES_SQL_FILE_INSERT_INTO_PROJECT_NUMBER_ORDER_NUMBER,
    'InboundDetails': OUTPUT_TABLES_SQL_FILE_INSERT_INTO_INBOUND_DETAILS,
    'InventoryData': OUTPUT_TABLES_SQL_FILE_INSERT_INTO_INVENTORY_DATA,
    'OutboundData': OUTPUT_TABLES_SQL_FILE_INSERT_INTO_OUTBOUND_DATA,
    'OutboundDataByOrder': OUTPUT_TABLES_SQL_FILE_INSERT_INTO_OUTBOUND_DATA_BY_ORDER,
    'OrderVelocityCombinations': OUTPUT_TABLES_SQL_FILE_INSERT_INTO_ORDER_VELOCITY_COMBINATIONS,
    'VelocitySummary': OUTPUT_TABLES_SQL_FILE_INSERT_INTO_VELOCITY_SUMMARY,
    'VelocityLadder': OUTPUT_TABLES_SQL_FILE_INSERT_INTO_VELOCITY_LADDER,
    'VelocityByMonth': OUTPUT_TABLES_SQL_FILE_INSERT_INTO_VELOCITY_BY_MONTH,
    'DailyOrderProfileByVelocity': OUTPUT_TABLES_SQL_FILE_INSERT_INTO_DAILY_ORDER_PROFILE_BY_VELOCITY,
}

## Select queries
OUTPUT_TABLES_SQL_FILE_SELECT_ALL_FROM_PROJECT = 'data_profiler/database/sql/PROD/select/select_all_from_project.sql'

## Update queries
OUTPUT_TABLES_SQL_FILE_UPDATE_PROJECT = 'data_profiler/database/sql/PROD/update/update_project.sql'

## Delete queries
OUTPUT_TABLES_SQL_FILE_DELETE_FROM_TABLES_BY_PROJECT_NUMBER = 'data_profiler/database/sql/PROD/delete/delete_from_tables_by_project_number.sql'
OUTPUT_TABLES_SQL_FILE_DELETE_FROM_PROJECT = 'data_profiler/database/sql/PROD/delete/delete_from_project.sql'
OUTPUT_TABLES_SQL_FILE_DELETE_FROM_ITEM_MASTER = 'data_profiler/database/sql/PROD/delete/delete_from_item_master.sql'
OUTPUT_TABLES_SQL_FILE_DELETE_FROM_INBOUND_HEADER = 'data_profiler/database/sql/PROD/delete/delete_from_inbound_header.sql'
OUTPUT_TABLES_SQL_FILE_DELETE_FROM_PROJECT_NUMBER_VELOCITY = 'data_profiler/database/sql/PROD/delete/delete_from_project_number_velocity.sql'
OUTPUT_TABLES_SQL_FILE_DELETE_FROM_PROJECT_NUMBER_ORDER_NUMBER = 'data_profiler/database/sql/PROD/delete/delete_from_project_number_order_number.sql'
OUTPUT_TABLES_SQL_FILE_DELETE_FROM_INBOUND_DETAILS = 'data_profiler/database/sql/PROD/delete/delete_from_inbound_details.sql'
OUTPUT_TABLES_SQL_FILE_DELETE_FROM_INVENTORY_DATA = 'data_profiler/database/sql/PROD/delete/delete_from_inventory_data.sql'
OUTPUT_TABLES_SQL_FILE_DELETE_FROM_OUTBOUND_DATA = 'data_profiler/database/sql/PROD/delete/delete_from_outbound_data.sql'
OUTPUT_TABLES_SQL_FILE_DELETE_FROM_OUTBOUND_DATA_BY_ORDER = 'data_profiler/database/sql/PROD/delete/delete_from_outbound_data_by_order.sql'
OUTPUT_TABLES_SQL_FILE_DELETE_FROM_ORDER_VELOCITY_COMBINATIONS = 'data_profiler/database/sql/PROD/delete/delete_from_order_velocity_combinations.sql'
OUTPUT_TABLES_SQL_FILE_DELETE_FROM_VELOCITY_SUMMARY = 'data_profiler/database/sql/PROD/delete/delete_from_velocity_summary.sql'
OUTPUT_TABLES_SQL_FILE_DELETE_FROM_VELOCITY_LADDER = 'data_profiler/database/sql/PROD/delete/delete_from_velocity_ladder.sql'
OUTPUT_TABLES_SQL_FILE_DELETE_FROM_VELOCITY_BY_MONTH = 'data_profiler/database/sql/PROD/delete/delete_from_velocity_by_month.sql'
OUTPUT_TABLES_SQL_FILE_DELETE_FROM_DAILY_ORDER_PROFILE_BY_VELOCITY = 'data_profiler/database/sql/PROD/delete/delete_from_daily_order_profile_by_velocity.sql'

# IMPORTANT: these need to stay in DELETION order. that is, delete from non-PK tables first, then PK tables
OUTPUT_TABLES_DELETE_SQL_FILES_MAPPER = {
    'DailyOrderProfileByVelocity': OUTPUT_TABLES_SQL_FILE_DELETE_FROM_DAILY_ORDER_PROFILE_BY_VELOCITY,
    'VelocityByMonth': OUTPUT_TABLES_SQL_FILE_DELETE_FROM_VELOCITY_BY_MONTH,
    'VelocityLadder': OUTPUT_TABLES_SQL_FILE_DELETE_FROM_VELOCITY_LADDER,
    'VelocitySummary': OUTPUT_TABLES_SQL_FILE_DELETE_FROM_VELOCITY_SUMMARY,
    'OrderVelocityCombinations': OUTPUT_TABLES_SQL_FILE_DELETE_FROM_ORDER_VELOCITY_COMBINATIONS,
    'OutboundDataByOrder': OUTPUT_TABLES_SQL_FILE_DELETE_FROM_OUTBOUND_DATA_BY_ORDER,
    'OutboundData': OUTPUT_TABLES_SQL_FILE_DELETE_FROM_OUTBOUND_DATA,
    'InventoryData': OUTPUT_TABLES_SQL_FILE_DELETE_FROM_INVENTORY_DATA,
    'InboundDetails': OUTPUT_TABLES_SQL_FILE_DELETE_FROM_INBOUND_DETAILS,
    'ProjectNumber_OrderNumber': OUTPUT_TABLES_SQL_FILE_DELETE_FROM_PROJECT_NUMBER_ORDER_NUMBER,
    'ProjectNumber_Velocity': OUTPUT_TABLES_SQL_FILE_DELETE_FROM_PROJECT_NUMBER_VELOCITY,
    'InboundHeader': OUTPUT_TABLES_SQL_FILE_DELETE_FROM_INBOUND_HEADER,
    'ItemMaster': OUTPUT_TABLES_SQL_FILE_DELETE_FROM_ITEM_MASTER,
    'Project': OUTPUT_TABLES_SQL_FILE_DELETE_FROM_PROJECT
}



#####################
### DEV SQL FILES ###
#####################

## Insert quries
DEV_OUTPUT_TABLES_SQL_FILE_INSERT_INTO_PROJECT = 'data_profiler/database/sql/DEV/insert/insert_into_project.sql'
DEV_OUTPUT_TABLES_SQL_FILE_INSERT_INTO_ITEM_MASTER = 'data_profiler/database/sql/DEV/insert/insert_into_item_master.sql'
DEV_OUTPUT_TABLES_SQL_FILE_INSERT_INTO_INBOUND_HEADER = 'data_profiler/database/sql/DEV/insert/insert_into_inbound_header.sql'
DEV_OUTPUT_TABLES_SQL_FILE_INSERT_INTO_PROJECT_NUMBER_VELOCITY = 'data_profiler/database/sql/DEV/insert/insert_into_project_number_velocity.sql'
DEV_OUTPUT_TABLES_SQL_FILE_INSERT_INTO_PROJECT_NUMBER_ORDER_NUMBER = 'data_profiler/database/sql/DEV/insert/insert_into_project_number_order_number.sql'
DEV_OUTPUT_TABLES_SQL_FILE_INSERT_INTO_INBOUND_DETAILS = 'data_profiler/database/sql/DEV/insert/insert_into_inbound_details.sql'
DEV_OUTPUT_TABLES_SQL_FILE_INSERT_INTO_INVENTORY_DATA = 'data_profiler/database/sql/DEV/insert/insert_into_inventory_data.sql'
DEV_OUTPUT_TABLES_SQL_FILE_INSERT_INTO_OUTBOUND_DATA = 'data_profiler/database/sql/DEV/insert/insert_into_outbound_data.sql'
DEV_OUTPUT_TABLES_SQL_FILE_INSERT_INTO_OUTBOUND_DATA_BY_ORDER = 'data_profiler/database/sql/DEV/insert/insert_into_outbound_data_by_order.sql'
DEV_OUTPUT_TABLES_SQL_FILE_INSERT_INTO_ORDER_VELOCITY_COMBINATIONS = 'data_profiler/database/sql/DEV/insert/insert_into_order_velocity_combinations.sql'
DEV_OUTPUT_TABLES_SQL_FILE_INSERT_INTO_VELOCITY_SUMMARY = 'data_profiler/database/sql/DEV/insert/insert_into_velocity_summary.sql'
DEV_OUTPUT_TABLES_SQL_FILE_INSERT_INTO_VELOCITY_LADDER = 'data_profiler/database/sql/DEV/insert/insert_into_velocity_ladder.sql'
DEV_OUTPUT_TABLES_SQL_FILE_INSERT_INTO_VELOCITY_BY_MONTH = 'data_profiler/database/sql/DEV/insert/insert_into_velocity_by_month.sql'
DEV_OUTPUT_TABLES_SQL_FILE_INSERT_INTO_DAILY_ORDER_PROFILE_BY_VELOCITY = 'data_profiler/database/sql/DEV/insert/insert_into_daily_order_profile_by_velocity.sql'

DEV_OUTPUT_TABLES_INSERT_SQL_FILES_MAPPER = {
    'Project': DEV_OUTPUT_TABLES_SQL_FILE_INSERT_INTO_PROJECT,
    'ItemMaster': DEV_OUTPUT_TABLES_SQL_FILE_INSERT_INTO_ITEM_MASTER,
    'InboundHeader': DEV_OUTPUT_TABLES_SQL_FILE_INSERT_INTO_INBOUND_HEADER,
    'ProjectNumber_Velocity': DEV_OUTPUT_TABLES_SQL_FILE_INSERT_INTO_PROJECT_NUMBER_VELOCITY,
    'ProjectNumber_OrderNumber': DEV_OUTPUT_TABLES_SQL_FILE_INSERT_INTO_PROJECT_NUMBER_ORDER_NUMBER,
    'InboundDetails': DEV_OUTPUT_TABLES_SQL_FILE_INSERT_INTO_INBOUND_DETAILS,
    'InventoryData': DEV_OUTPUT_TABLES_SQL_FILE_INSERT_INTO_INVENTORY_DATA,
    'OutboundData': DEV_OUTPUT_TABLES_SQL_FILE_INSERT_INTO_OUTBOUND_DATA,
    'OutboundDataByOrder': DEV_OUTPUT_TABLES_SQL_FILE_INSERT_INTO_OUTBOUND_DATA_BY_ORDER,
    'OrderVelocityCombinations': DEV_OUTPUT_TABLES_SQL_FILE_INSERT_INTO_ORDER_VELOCITY_COMBINATIONS,
    'VelocitySummary': DEV_OUTPUT_TABLES_SQL_FILE_INSERT_INTO_VELOCITY_SUMMARY,
    'VelocityLadder': DEV_OUTPUT_TABLES_SQL_FILE_INSERT_INTO_VELOCITY_LADDER,
    'VelocityByMonth': DEV_OUTPUT_TABLES_SQL_FILE_INSERT_INTO_VELOCITY_BY_MONTH,
    'DailyOrderProfileByVelocity': DEV_OUTPUT_TABLES_SQL_FILE_INSERT_INTO_DAILY_ORDER_PROFILE_BY_VELOCITY,
}


## Select queries
DEV_OUTPUT_TABLES_SQL_FILE_SELECT_ALL_FROM_PROJECT = 'data_profiler/database/sql/DEV/select/select_all_from_project.sql'

## Update queries
DEV_OUTPUT_TABLES_SQL_FILE_UPDATE_PROJECT = 'data_profiler/database/sql/DEV/update/update_project.sql'

## Delete queries
DEV_OUTPUT_TABLES_SQL_FILE_DELETE_FROM_TABLES_BY_PROJECT_NUMBER = 'data_profiler/database/sql/DEV/delete/delete_from_tables_by_project_number.sql'

DEV_OUTPUT_TABLES_SQL_FILE_DELETE_FROM_PROJECT = 'data_profiler/database/sql/DEV/delete/delete_from_project.sql'
DEV_OUTPUT_TABLES_SQL_FILE_DELETE_FROM_ITEM_MASTER = 'data_profiler/database/sql/DEV/delete/delete_from_item_master.sql'
DEV_OUTPUT_TABLES_SQL_FILE_DELETE_FROM_INBOUND_HEADER = 'data_profiler/database/sql/DEV/delete/delete_from_inbound_header.sql'
DEV_OUTPUT_TABLES_SQL_FILE_DELETE_FROM_PROJECT_NUMBER_VELOCITY = 'data_profiler/database/sql/DEV/delete/delete_from_project_number_velocity.sql'
DEV_OUTPUT_TABLES_SQL_FILE_DELETE_FROM_PROJECT_NUMBER_ORDER_NUMBER = 'data_profiler/database/sql/DEV/delete/delete_from_project_number_order_number.sql'
DEV_OUTPUT_TABLES_SQL_FILE_DELETE_FROM_INBOUND_DETAILS = 'data_profiler/database/sql/DEV/delete/delete_from_inbound_details.sql'
DEV_OUTPUT_TABLES_SQL_FILE_DELETE_FROM_INVENTORY_DATA = 'data_profiler/database/sql/DEV/delete/delete_from_inventory_data.sql'
DEV_OUTPUT_TABLES_SQL_FILE_DELETE_FROM_OUTBOUND_DATA = 'data_profiler/database/sql/DEV/delete/delete_from_outbound_data.sql'
DEV_OUTPUT_TABLES_SQL_FILE_DELETE_FROM_OUTBOUND_DATA_BY_ORDER = 'data_profiler/database/sql/DEV/delete/delete_from_outbound_data_by_order.sql'
DEV_OUTPUT_TABLES_SQL_FILE_DELETE_FROM_ORDER_VELOCITY_COMBINATIONS = 'data_profiler/database/sql/DEV/delete/delete_from_order_velocity_combinations.sql'
DEV_OUTPUT_TABLES_SQL_FILE_DELETE_FROM_VELOCITY_SUMMARY = 'data_profiler/database/sql/DEV/delete/delete_from_velocity_summary.sql'
DEV_OUTPUT_TABLES_SQL_FILE_DELETE_FROM_VELOCITY_LADDER = 'data_profiler/database/sql/DEV/delete/delete_from_velocity_ladder.sql'
DEV_OUTPUT_TABLES_SQL_FILE_DELETE_FROM_VELOCITY_BY_MONTH = 'data_profiler/database/sql/DEV/delete/delete_from_velocity_by_month.sql'
DEV_OUTPUT_TABLES_SQL_FILE_DELETE_FROM_DAILY_ORDER_PROFILE_BY_VELOCITY = 'data_profiler/database/sql/DEV/delete/delete_from_daily_order_profile_by_velocity.sql'

# IMPORTANT: these need to stay in DELETION order. that is, delete from non-PK tables first, then PK tables
DEV_OUTPUT_TABLES_DELETE_SQL_FILES_MAPPER = {
    'DailyOrderProfileByVelocity': DEV_OUTPUT_TABLES_SQL_FILE_DELETE_FROM_DAILY_ORDER_PROFILE_BY_VELOCITY,
    'VelocityByMonth': DEV_OUTPUT_TABLES_SQL_FILE_DELETE_FROM_VELOCITY_BY_MONTH,
    'VelocityLadder': DEV_OUTPUT_TABLES_SQL_FILE_DELETE_FROM_VELOCITY_LADDER,
    'VelocitySummary': DEV_OUTPUT_TABLES_SQL_FILE_DELETE_FROM_VELOCITY_SUMMARY,
    'OrderVelocityCombinations': DEV_OUTPUT_TABLES_SQL_FILE_DELETE_FROM_ORDER_VELOCITY_COMBINATIONS,
    'OutboundDataByOrder': DEV_OUTPUT_TABLES_SQL_FILE_DELETE_FROM_OUTBOUND_DATA_BY_ORDER,
    'OutboundData': DEV_OUTPUT_TABLES_SQL_FILE_DELETE_FROM_OUTBOUND_DATA,
    'InventoryData': DEV_OUTPUT_TABLES_SQL_FILE_DELETE_FROM_INVENTORY_DATA,
    'InboundDetails': DEV_OUTPUT_TABLES_SQL_FILE_DELETE_FROM_INBOUND_DETAILS,
    'ProjectNumber_OrderNumber': DEV_OUTPUT_TABLES_SQL_FILE_DELETE_FROM_PROJECT_NUMBER_ORDER_NUMBER,
    'ProjectNumber_Velocity': DEV_OUTPUT_TABLES_SQL_FILE_DELETE_FROM_PROJECT_NUMBER_VELOCITY,
    'InboundHeader': DEV_OUTPUT_TABLES_SQL_FILE_DELETE_FROM_INBOUND_HEADER,
    'ItemMaster': DEV_OUTPUT_TABLES_SQL_FILE_DELETE_FROM_ITEM_MASTER,
    'Project': DEV_OUTPUT_TABLES_SQL_FILE_DELETE_FROM_PROJECT
}
