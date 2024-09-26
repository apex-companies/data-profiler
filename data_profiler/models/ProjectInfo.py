'''
Jack Miller
Apex Companies
Oct 2024

Pydantic models to represent the Project table and related information
'''


from pydantic import BaseModel

from .TransformOptions import TransformOptions

class ProjectInfoInputs(BaseModel):
    project_name: str
    company_name: str
    company_location: str
    salesperson: str
    email: str
    start_date: str
    notes: str

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
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
    item_master: str
    inbound_header: str
    inbound_details: str
    inventory: str
    order_header: str
    order_details: str


class ProjectInfoExistingProject(ProjectInfoInputs):
    project_number: str
    data_uploaded: bool
    transform_options: TransformOptions
    uploaded_file_paths: UploadedFilePaths