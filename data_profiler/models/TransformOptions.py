'''
Jack Miller
Apex Companies
Oct 2024

Transform options models
'''

from enum import Enum
from typing import Literal
from pydantic import BaseModel

# DATE_FOR_ANALYSIS = Literal['ReceivedDate', 'PickDate', 'ShipDate']
class DateForAnalysis(str, Enum):
    RECEIVED_DATE = 'ReceivedDate'
    PICK_DATE = 'PickDate'
    SHIP_DATE = 'ShipDate'

# WEEKEND_DATE_RULES = Literal['nearest_weekday', 'all_to_monday', 'all_to_friday', 'As is']
class WeekendDateRules(str, Enum):
    NEAREST_WEEKDAY = 'Nearest Weekday'
    ALL_TO_MONDAY = 'All to Monday'
    ALL_TO_FRIDAY = 'All to Friday'
    AS_IS = "As Is"

class TransformOptions(BaseModel):
    date_for_analysis: DateForAnalysis | None = None
    weekend_date_rule: WeekendDateRules | None = None
    process_inbound_data: bool = True
    process_inventory_data: bool = True
    process_outbound_data: bool = True
