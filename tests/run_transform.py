'''
Jack Miller
Apex Companies
Oct. 2025

Code to run TransformService without using GUI
'''

from datetime import datetime

from data_profiler.helpers.data_directory import DataDirectory, DataDirectoryType
from data_profiler.helpers.models.TransformOptions import TransformOptions, DateForAnalysis, WeekendDateRules

from data_profiler.services.transform_service import TransformService
from data_profiler.data_profiler import DataProfiler


def run_transform(project_number: str, data_dir: str, transform_options: TransformOptions):

    # Init dataprofiler
    DataProfilerObj = DataProfiler(
        project_number=project_number,
        dev=True
    )

    # Run
    response = DataProfilerObj.transform_and_upload_data(
        data_directory=data_dir,
        transform_options=transform_options
    )

    ## Post results
    print(f'\n\n\nDONE.')
    print(f'Log file:')
    print(response.log_file_path)

    print(f'Success: {response.success}')
    if not response.success:
        print(f'Error:')
        print(response.message)

    else:
        print(response.rows_inserted.model_dump())


def transform_pactiv():
    # PN
    project_number = 'P01A'
    
    # Data Directory
    data_path = "C:/Users/jack.miller/Documents/Apex/Consulting/3 - Source Folders/data-profiler/test data sets/Pactiv Salisbury"

    # Transform Options
    transform_options = TransformOptions(
        date_for_analysis=DateForAnalysis.SHIP_DATE,
        weekend_date_rule=WeekendDateRules.AS_IS,
        data_directory_type=DataDirectoryType.REGULAR,
        process_inbound_data=True,
        process_inventory_data=True,
        process_outbound_data=True
    )

    # Transform
    run_transform(project_number=project_number, data_dir=data_path, transform_options=transform_options)

def transform_medline_c54():
    # PN
    project_number = 'AAS24-10SKU'
    
    # Data Directory
    data_path = "C:/Users/jack.miller/Documents/Apex/Consulting/3 - Source Folders/data-profiler/test data sets/Medline C54 Cooler"

    # Transform Options
    transform_options = TransformOptions(
        date_for_analysis=DateForAnalysis.PICK_DATE,
        weekend_date_rule=WeekendDateRules.AS_IS,
        data_directory_type=DataDirectoryType.HEADERS,
        process_inbound_data=False,
        process_inventory_data=True,
        process_outbound_data=True
    )

    # Transform
    run_transform(project_number=project_number, data_dir=data_path, transform_options=transform_options)


# transform_pactiv()
# transform_medline_c54()

