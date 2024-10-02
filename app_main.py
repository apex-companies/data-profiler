'''
Jack Miller
Apex Companies
Oct 2024

Entry point for DataProfiler app
'''

import os
import sys
from importlib.metadata import version

from apex_gui.frames.notification_dialogs import StartUpErrorDialog

from data_profiler.models.ProjectInfo import BaseProjectInfo
from data_profiler.models.TransformOptions import TransformOptions, WeekendDateRules, DateForAnalysis

from data_profiler.data_profiler import DataProfiler
from data_profiler.data_profiler_gui import DataProfilerGUI

# Make sure host computer can see Y drive, if not it's an invalid host
if not os.path.exists("Y:\\DataProfiler\\version.txt"):
    print('INVALID HOST')

    error_dialog = StartUpErrorDialog(text='INVALID HOST')
    error_dialog.mainloop()

    sys.exit(-1)

# Make sure current install version matches latest version
current_version = version('data-profiler')
master_version = ''
with open("Y:\\DataProfiler\\version.txt", "r+") as f:
    master_version = f.read()

print(f'Master version: {master_version}')
print(f'Current version: {current_version}')

if master_version != current_version:
    print('UPDATE TO LATEST VERSION')

    message = f'UPDATE TO LATEST VERSION\n\nThis version: {current_version}\nLatest version: {master_version} '
    error_dialog = StartUpErrorDialog(text=message)
    error_dialog.mainloop()

    sys.exit(-1)


''' GUI '''

app = DataProfilerGUI(dev=True)
app.mainloop()



''' Data Profiler '''

# dp = DataProfiler(project_number='TESTNATIVE', dev=True)
# # dp = DataProfiler(project_number='12345', dev=True)

# # print(dp.get_output_tables_projects())
# print(dp.get_project_info())

# # print(dp.transform_and_upload_data(data_directory="C:\\Users\\jack.miller\\Documents\\Apex\\Consulting\\Client Studies\\CJ Logistics\\data\\clean - only pallet pick",
# # print(dp.transform_and_upload_data(data_directory="C:\\Users\\jack.miller\\Documents\\Apex\\Consulting\\Client Studies\\Mondelez\\data\\Kent - AAS24-018539\\clean",
# print(dp.transform_and_upload_data(data_directory="test data sets/MDLZ Kent - no ib",
#                                    transform_options=TransformOptions(date_for_analysis=DateForAnalysis.SHIP_DATE, weekend_date_rule=WeekendDateRules.AS_IS,
#                                                                       process_inbound_data=False)))

# # print(dp.delete_project_data())

# 9:45:00 AM   2550000010     395703

# info = BaseProjectInfo(
#     project_number='TESTNATIVE',
#     company_name='DAN\'S STORE',
#     salesperson='DAN DOIT',
#     company_location='BUCKTOWN',
#     project_name='NEW DONUT STORAGE',
#     email='dan.email@aol.com',
#     start_date='',
#     notes='opportunity'
# )

# print(dp.create_new_project(project_info=info))