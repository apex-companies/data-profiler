![Apex Logo](./resources/Apex-Companies-Logo.gif)

# *DataProfiler*

*DataProfiler* is the "home base" of data analysis for Apex Consulting. It is essentially a user interface (UI) for the AAS_Development database; its main function is to upload client data to the database, at which point the data can be used for a variety of purposes, the most notable of which being the Data Profile Report.

![Start Screen](./documentation/screenshots/start%20screen.png)
![Dashboard](./documentation/screenshots/home%20page.png)
![Upload Page](./documentation/screenshots/upload%20page.png)
![More Actions Page](./documentation/screenshots/more%20actions%20page%20steelite.png)


## Contents
1. [About](#about)
1. [How to Use](#how-to-use)
1. [Development](#development)
1. [Testing](#testing)
1. [File Structure](#file-structure)
1. [Appendix A: Solution Architecture](#appendix-a-solution-architecture)
1. [Appendix B: customtkinter](#appendix-b-customtkinter)

## About
As mentioned above, *DataProfiler* is essentially a UI for the AAS_Development database, which makes client data accessible to the full suite of Apex Consulting Tools.

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

See [DataProfiler SOP](./documentation/DataProfiler%20SOP.md). Available both as Markdown and PDF


## Development

For more info on Environment Setup, Workflow, Packing and Distribution, see [Apex Tool Development](https://github.com/apex-companies/consulting-documentation/blob/main/APEX%20Python%20Tool%20Development.md).

### Running *DataProfiler* locally

There are two modes in which to run *DataProfiler* locally - dev mode or production mode.

#### dev
Interacts with the `OutputTables_Dev` schema in the AAS_Development database. Recommended for development activities. 

```python
app = DataProfilerGUI(dev=True)
app.mainloop()
```

#### production
Interacts with the `OutputTables_Prod` schema in the AAS_Development database. NOT recommended for development activities. Reserve usage for select testing activities, when testing cannot be done sufficiently in dev mode. 

```python
app = DataProfilerGUI(dev=False)
app.mainloop()
```


#### Steps to Run Locally
1. Connect to Apex Azure VPN, if not in office  

1. Activate virtual environment  
    ```bash
    ~$ source .venv/Scripts/activate
    ```

    Verify environment is activated  
    ```bash
    ~$ poetry env list
    .venv (Activated)
    ```

1. Navigate to the the root directory ("data-profiler")   
    ```bash
    ~$ cd /path/to/folder/data-profiler
    ```

1. Run the app  
    ```bash
    ~$ py -m app_main.py
    ```


## Testing

Some [rudimentary testing code](./tests/test_data_profiler.py) has been created, but this is an area to develop.



## File Structure


### ./data_profiler

Root contains the two main classes - `DataProfiler` and `DataProfilerGUI`

#### database

***constants.py*** This application doesn't use an ORM (object-relational mapper) so these constants basically play that role. Super important that the lists of tables / columns are accurate to the database.

***database_manager.py*** Contains `DatabaseConnection`, which connects grabs our connection string and connects to our database and returns a `Connection` object. Also very important. 

#### frames

***custom_widgets.py*** Contains various custom frames for the GUI

#### helpers

What it sounds like

***constants/data_file_constants.py*** Plays the other half of the ORM role. Makes sure incoming data files are structured with the correct columns and data types.

***constants/app_constants.py*** Relatively few app-level constants, but you're gonna want to make sure that the file path constants are correct.

***models/*** Contains the pydantic models that `DataProfiler` and `DataProfilerGUI` use to talk with each other.

#### services

Contain the services. See [below](#database-interaction)

### ./resources

#### SQL
Two (almost) identical subfolders: DEV and PROD. DEV queries are used in development mode and interact with `OutputTables_Dev`. PROD queries are used in production mode and interact with `OutputTables_Prod`.

> *IMPORTANT: When creating a new SQL file - such as a pre-made report - or updating an existing file, BE SURE to make the same change to both the DEV and PROD versions.*

SQL folders are organized by query type: select, insert, update, and delete. Pre-made SQL reports read existing data, so they're under the select folder.

#### Icons
Find other Windows 10-styled icons here  
https://icons8.com/icons/windows  

Icons in use:   
https://icons8.com/icon/14910/back-arrow  
https://icons8.com/icon/16142/add-new  
https://icons8.com/icon/14098/done  
https://icons8.com/icon/16255/save  
https://icons8.com/icon/14237/trash  
https://icons8.com/icon/14090/upload  



## Appendix A: Solution Architecture

![DP Solution Architecture](./documentation/Data%20Profile%20Tool%20-%20Solution%20Architecture%208.8.25.png)


### DataProfilerGUI
File Location: [data_profiler_gui.py](./data_profiler/data_profiler_gui.py)

As the graphical user interface (GUI) of the application, `DataProfilerGUI` provides service to the user (aka client). Taking input from the user, it interprets their requests and presents them to the backend server (business logic, database, etc.) on their behalf, returning any pertinent information.

`DataProfilerGUI` is built on customtkinter, which you can read more about [below](#appendix-b-customtkinter). It often communicates with the "server" (`DataProfiler`) using pydantic data models, which essentially let you create your own data types. Learn about pydantic [here](https://docs.pydantic.dev/latest/).  


### DataProfiler
File Location: [data_profiler.py](./data_profiler/data_profiler.py)

As the "API Layer" of the application, `DataProfiler` takes requests from the client, delegates tasks to further layers, such as the database services or other logic hubs, and returns a response. Since this is not a web application, its "APIs" are not http routes but simply Python class methods.

`DataProfiler` responds to requests of the CRUD order - create, read, update, and delete. It also contains some miscellaneous logic - such as "Data Describer", which it also contains the endpoint for - as well as some internal helper functions.


### Database Interaction

Two main hubs make up the application layer of *DataProfiler*, and both provide interaction (service) with database. 

#### OutputTables Service
File Location: [output_tables_service.py](./data_profiler/services/output_tables_service.py)  

`OutputTablesService` provides general service to the *OutputTables* schema of the AAS_Development database. Get info for a project, a list of project numbers, download a pre-made SQL report, and more with this service.


#### Transform Service
File Location: [transform_service.py](./data_profiler/services/transform_service.py)  

`TransformService` exists specifically to handle the upload (insert) of a new client dataset into the database. It contains class methods which create each of the tables in the *OutputTables* schema, a method which inserts a dataframe given a SQL insert query, and one main method which orchestrates the whole process. 

#### Usage
Due to the API-like nature of `DataProfiler`, both `OutputTablesService` and `TransformService` are designed for one-time use and are thus work well inside the Python "with" clause. The below example shows an optimal pattern for using these services. 

```python
project_info = BaseProjectInfo()
with OutputTablesService(dev=self.dev) as service:
    result = service.insert_new_project_to_project_table(project_info=project_info)

```

### Azure SQL Database

Check out [this lucid](https://lucid.app/lucidchart/1f2f04c0-6471-45e9-b123-f90a8523b9ba/edit?invitationId=inv_4aea5ff1-27ba-4e32-a10e-73449b3db657&page=u_SS~BOWu2-C#).



## Appendix B: customtkinter

This app - like other Apex apps - makes heavy use of the Python UI library customtkinter. Based on the classic library Tkinter, customtkinter provides more modern and customizable widgets.

It is critical to be familiar with this package before doing any UI-related development work for this application. Below are some resources for learning customtkinter. The first two beginner tutorials ("Grid System" and "Using Frames") are especially useful, as they introduce concepts used throughput *DataProfiler*.


| Resource | Link |
| :------- | :------ |
| GitHub Repo | https://github.com/TomSchimansky/CustomTkinter/tree/master  |
| Examples  | https://github.com/TomSchimansky/CustomTkinter/tree/master/examples  |
| Documentation | https://customtkinter.tomschimansky.com/documentation/ |
| Tutorials | https://customtkinter.tomschimansky.com/tutorial/ | 


### Key Concepts

#### Classes
We've structured the entire UI portion of the application into a class. The main app `DataProfilerGUI` is a custom class that inherits from the main customtkinter window `CTk` (through `ApexApp`; see section on apex-gui). And, many of the widgets within it are also custom classes that inherit from other customtkinter widgets (CTkFrame, CTkTopLevel, etc.).

Structuring the app in this way makes the codebase clear and concise and also makes the application easily extendable. Adding pages and sections is especially simple in this structure.

The "Using Frames" chapter of the customtkinter beginner tutorial expounds on this concept, especially the start of the page through "Multiple Instances" section.

#### Pages and "Grid"
To accomplish a multi-page application, *DataProfile*  organizes widgets into pages, and makes use of the "grid" geometry manager to manage state.

Take the home frame, for example ("Data Profile Dashboard"). The following function, which belongs to the main application class `DataProfilerGUI`, creates a frame (`self.home_frame = Page()`) for the home page as well as all the widgets and subframes that make up the home page.

![Home Page Func](./documentation/screenshots/technical/create%20frame%20func.png)

The home frame has a separate app-level function which actually places the page in the app window and places its widgets within the page.

![Home Page Grid Func](./documentation/screenshots/technical/grid%20frame%20func.png)

Since all the widgets for the home page belong within the one frame `self.home_frame`, that page can easily be made active or inactive by simply "gridding" or "ungridding" that one variable.

![Toggle Grid](./documentation/screenshots/technical/toggle%20grid%20func.png)

All other *DataProfile* pages are structured and manipulated using this general strategy.


