'''
Jack Miller
Apex Companies
Oct 2024

Pydantic models to represent the Project table and related information
'''


from pydantic import BaseModel

from .TransformOptions import TransformOptions, DateForAnalysis, WeekendDateRules

class ProjectInfoInputs(BaseModel):
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


class UploadedFilePaths(BaseModel):
    item_master: str = ''
    inbound_header: str = ''
    inbound_details: str = ''
    inventory: str = ''
    order_header: str = ''
    order_details: str = ''


class ProjectInfoExistingProject(ProjectInfoInputs):
    data_uploaded: bool = False
    upload_date: str = ''
    transform_options: TransformOptions | None = None
    uploaded_file_paths: UploadedFilePaths = UploadedFilePaths()