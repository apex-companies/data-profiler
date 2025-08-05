# *DataProfiler*


*DataProfiler* is the "home base" of data analysis for Apex Consulting. It is essentially a user interface (UI) for the AAS_Development database (see diagram below); its main function is to upload client data to the database, at which point the data can be used for a variety of purposes, the most notable of which being the Data Profile Report.

![DP Data Flow](./documentation/screenshots/DP%20Data%20Flow.png)

It's functionalities generally follow the CRUD pattern - Create, Read, Update, and Delete. 

#### Create
 - Create a new project in the database
 - Upload a new client dataset

#### Read
 - View an existing project
 - Download an existing project's data
 - Download pre-made SQL reports for an existing project

#### Update
 - Update "Subwarehouse" values for an existing project's SKUs

#### Delete
 - Delete data for an existing project (perhaps to re-upload)
 - Delete a project

<br>

> *DataProfiler* is NOT a data cleaning or validation tool - it expects data to be clean and in a certain format. When a dataset is uploaded, it simply extracts the data it's given, transforms it to the structure of the database, and loads it to the database (ETL).


## How to Use

See [DataProfiler SOP](./documentation/DataProfiler%20SOP.md). Available both as Markdown and Word file

## Development

For more info on Environment Setup, Workflow, Packing and Distribution, see [Apex Tool Development]()

### Running

run "app_main.py" from the root directory ("data-profiler") to run


## File Structure


## Key Classes and Functions

