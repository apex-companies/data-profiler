'''
Jack Miller
Apex Companies
Oct 2024

Entry point for DataProfiler app
'''

import os
import sys
from importlib.metadata import version

from data_profiler.data_profiler import DataProfiler

# Make sure host computer can see Y drive, if not it's an invalid host
if not os.path.exists("Y:\\DataProfiler\\version.txt"):
    print('INVALID HOST')

    # error_dialog = StartUpErrorDialog(text='INVALID HOST')
    # error_dialog.mainloop()

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
    # error_dialog = StartUpErrorDialog(text=message)
    # error_dialog.mainloop()

    sys.exit(-1)

dp = DataProfiler(project_number='CJPROSPECTIVE', dev=True)

print(dp.get_output_tables_projects())
print(dp.get_project_number_info())