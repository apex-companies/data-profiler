'''
Jack Miller
Apex Companies
Oct 2024

Main Python class for DataProfiler app logic
'''

from typing import Annotated

from .models.ProjectInfo import ProjectInfoInputs, UploadedFilePaths, ProjectInfoExistingProject
from .models.TransformOptions import TransformOptions

from .services.output_tables_service import OutputTablesService


class DataProfiler:

    def __init__(self, project_number: Annotated[str, 'Apex Project Number'], dev: bool = False):
        self.project_number = project_number
        self.dev = dev

        self.OutputTablesService = OutputTablesService(dev=self.dev)
        pass

    def get_output_tables_projects(self) -> list[str]:
        return self.OutputTablesService.get_output_tables_project_numbers()

    def get_project_number_info(self): # -> ProjectInfo:
        return self.OutputTablesService.get_project_info_for_project(self.project_number)

        # info = { }
        # print(project_number)

        # project_numbers = get_output_tables_project_numbers()
        # if project_number not in project_numbers:
        #     response.status_code = status.HTTP_400_BAD_REQUEST
        #     return { "Error": "Project Number not found" }
        
        # company_table_records = get_company_table_row_for_project(project_number=project_number)
        # item_master_skus = get_skus_in_item_master_for_project(project_number=project_number)
        # lines_in_outbound = get_lines_in_outbound_for_project(project_number=project_number)

        # info['ProjectNumber'] = company_table_records[0][0]
        # info['Client'] = company_table_records[0][1]
        # info['Project Name'] = company_table_records[0][4]
        # info['Client Location'] = company_table_records[0][3]
        # info['Salesman'] = company_table_records[0][2]
        # info['SKUs'] = len(item_master_skus)
        # info['Lines in Outbound'] = lines_in_outbound

        # return info

    def create_new_project(self, project_info: ProjectInfoInputs): #-> Response
        return self.OutputTablesService.insert_new_project_to_project_table(project_info=project_info)

    def update_project_info(self, new_project_info: ProjectInfoInputs): #-> Response:
        pass

    def validate_uploaded_data_files(self, file_paths: UploadedFilePaths) -> bool:
        pass

    def transform_and_upload_data(self, file_paths: UploadedFilePaths, transform_options: Annotated[TransformOptions, 'Some options for analysis']): #-> Response
        pass

        # response_obj = BaseDBInteractionResponse()

        # # check to make sure data exists in RawData schema
        # raw_data_project_numbers = get_raw_data_project_numbers()
        # if project_number not in raw_data_project_numbers:
        #     response.status_code = status.HTTP_400_BAD_REQUEST
        #     response_obj.rows_affected = 0
        #     response_obj.message = "Project # has no raw data. Please upload raw data to database before continuing."
        #     return response_obj

        # # Check if Project # is already in OutputTables
        # output_tables_project_numbers = get_output_tables_project_numbers()
        # if project_number in output_tables_project_numbers:
        #     response.status_code = status.HTTP_400_BAD_REQUEST
        #     response_obj.rows_affected = 0
        #     response_obj.message = "Project # already has output table data. Please wipe data from output tables before starting afresh, if desired."
        #     return response_obj

        # # Transform and persist data
        # print('Transforming...')
        # rows_inserted = transform_by_project_number(project_number=project_number, project_info=project_info, variables_and_switches=variables_and_switches)
        
        # response_obj.rows_affected = rows_inserted
        # response_obj.message = "Insert seems to have been successful. Check logs to ensure."
        # return response_obj 

    def delete_project_data(self): # -> Response:
        pass

        # response_obj = BaseDBInteractionResponse()
        
        # project_nums = get_output_tables_project_numbers()
        # if project_number not in project_nums:
        #     response.status_code = status.HTTP_400_BAD_REQUEST
        #     response_obj.rows_affected = 0
        #     response_obj.message = f"Project Number {project_number} does not exist."
        #     return response_obj

        # # Delete
        # rows_affected = delete_from_output_tables_by_project_number(project_number=project_number)
        
        # response_obj.rows_affected = rows_affected
        # response_obj.message = "Delete seems to have been successful. Check logs to ensure."
        # return response_obj
