
import pandas as pd
from data_profiler.helpers.functions.functions import file_path_is_valid_data_frame, data_frame_is_empty

file_path = 'item.csv'

print(f'Data frame opens: {file_path_is_valid_data_frame(file_path)}')

print(f'Data frame is empty: {data_frame_is_empty(file_path)}')