'''
Jack Miller
Apex Companies
Oct 2024

Transform options models
'''

from enum import Enum
from pydantic import BaseModel


class DateForAnalysis(str, Enum):
    RECEIVED_DATE = 'ReceivedDate'
    PICK_DATE = 'PickDate'
    SHIP_DATE = 'ShipDate'


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
