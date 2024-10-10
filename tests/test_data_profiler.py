'''
Jack Miller
Apex Companies
Oct 2024

File meant to test DataProfiler class without using GUI
'''

from data_profiler.helpers.models.ProjectInfo import BaseProjectInfo
from data_profiler.helpers.models.TransformOptions import TransformOptions, WeekendDateRules, DateForAnalysis

from data_profiler.data_profiler import DataProfiler


dp = DataProfiler(project_number='TESTNATIVE', dev=True)
# dp = DataProfiler(project_number='12345', dev=True)

# print(dp.get_output_tables_projects())
print(dp.get_project_info())

# print(dp.transform_and_upload_data(data_directory="C:\\Users\\jack.miller\\Documents\\Apex\\Consulting\\Client Studies\\CJ Logistics\\data\\clean - only pallet pick",
# print(dp.transform_and_upload_data(data_directory="C:\\Users\\jack.miller\\Documents\\Apex\\Consulting\\Client Studies\\Mondelez\\data\\Kent - AAS24-018539\\clean",
print(dp.transform_and_upload_data(data_directory="test data sets/MDLZ Kent - no ib",
                                   transform_options=TransformOptions(date_for_analysis=DateForAnalysis.SHIP_DATE, weekend_date_rule=WeekendDateRules.AS_IS,
                                                                      process_inbound_data=False, process_outbound_data=False)))

# print(dp.delete_project_data())


info = BaseProjectInfo(
    project_number='TESTNATIVE',
    company_name='DAN\'S STORE',
    salesperson='DAN DOIT',
    company_location='BUCKTOWN',
    project_name='NEW DONUT STORAGE',
    email='dan.email@aol.com',
    start_date='',
    notes='opportunity'
)

print(dp.create_new_project(project_info=info))