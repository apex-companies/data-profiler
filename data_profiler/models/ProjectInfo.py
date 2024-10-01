'''
Jack Miller
Apex Companies
Oct 2024

Pydantic models to represent the Project table and related information
'''

from pydantic import BaseModel

from .TransformOptions import TransformOptions, DateForAnalysis, WeekendDateRules
from ..helpers.constants import UploadFileTypes


class BaseProjectInfo(BaseModel):
    project_number: str
    company_name: str
    salesperson: str
    company_location: str
    project_name: str
    email: str
    start_date: str
    notes: str

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "project_name": 'AAS24-010101',
                    "project_name": 'Conveyor System',
                    "company_name": 'Nike',
                    "company_location": 'Eugene, OR',
                    "salesperson": 'Guy Gentleman',
                    "email": 'guy.gentleman@apex-cos.com',
                    "start_date": '02/01/2023',
                    "notes": 'Only case data. Filtered out discontinued shoe line.'
                }
            ]
        }
    }


class UploadedFile(BaseModel):
    file_type: UploadFileTypes
    file_path: str

class UploadedFilePaths(BaseModel):
    item_master: str = ''
    inbound_header: str = ''
    inbound_details: str = ''
    inventory: str = ''
    order_header: str = ''
    order_details: str = ''
    # item_master: UploadedFile               # Item Master is always required
    # inbound_header: UploadedFile = UploadedFile(file_type=UploadFileTypes.INBOUND_HEADER, file_path='')
    # inbound_details: UploadedFile = UploadedFile(file_type=UploadFileTypes.INBOUND_DETAILS, file_path='')
    # inventory: UploadedFile = UploadedFile(file_type=UploadFileTypes.INVENTORY, file_path='')
    # order_header: UploadedFile = UploadedFile(file_type=UploadFileTypes.ORDER_HEADER, file_path='')
    # order_details: UploadedFile = UploadedFile(file_type=UploadFileTypes.ORDER_DETAILS, file_path='')


class ExistingProjectProjectInfo(BaseProjectInfo):
    data_uploaded: bool = False
    upload_date: str | None = None
    transform_options: TransformOptions
    uploaded_file_paths: UploadedFilePaths = UploadedFilePaths()