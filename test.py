
import pandas as pd
from data_profiler.helpers.functions.functions import file_path_is_valid_data_frame, data_frame_is_empty

file_path = 'test data sets/MDLZ Tatamy - no ib/OrderDetails.csv'

order_details = pd.read_csv(file_path)
order_details['BusinessUnit'] = ''
order_details['Carrier'] = ''
order_details['SpecialHandlingCodes'] = ''
order_details['ShipContainerType'] = ''

print(order_details.shape)
print(order_details.head())

order_details.to_csv(file_path, index=False)