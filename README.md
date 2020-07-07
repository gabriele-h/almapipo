# About

## Scenario
A set of
[Alma](https://knowledge.exlibrisgroup.com/Alma/Product_Documentation/010Alma_Online_Help_(English)/010Getting_Started/010Alma_Introduction/010Alma_Overview)
records needs to be created, deleted, updated, or fetched for analysis.

## Preparation

The Alma-IDs of the records are known and saved in a **semicolon or tab
delimited file**. The first column of that file needs to be the Alma-ID
or a list of Alma-IDs (see below "Input data").

## What Does This Package Do?

In a **database** both the **input** used as well as the
**status of the api call** are saved on a per-line or per-record basis.
All records will be fetched prior to deletion, update, or creation and a
**copy of each record before the action** (plus where applicable the
according response received) will be kept as a backup.

Another module of the package will handle the actual **api calls**.
If the manipulation is successful, the status for that
record will be changed from "new" to "done" in the database table
`job_status_per_id`. If anything goes wrong, the status will be set to "error".

**Note:** Currently all API-calls will be made with xml as the format. See 
how the format is set in the headers within `rest_call_api.py`:
```
"accept": "application/xml"
"Content-Type": "application/xml"
```
This is necessary as not all APIs will support json and in general the
Alma APIs seem to be implemented xml-first.

## What is *not* covered in this README
Modules that are not meant for day-to-day use will not be covered by
this README. They should include doc-strings though, so if you are
curious make use of python's `help`-function.

# Requirements

* Python 3.6.9 or higher, see requirements.txt for Python packages
* A PostgreSQL database with read and write access
* An Alma API-key with the necessary permissions for your operations

# Initial Setup

## Set up `venv`

Please make use of a virtual environment.
See https://docs.python.org/3/library/venv.html for further info.

## Install All From `requirements.txt`

The requirements are actually defined within `setup.py` and `requirements.txt`
has actually just one entry referring to that.

```bash
pip install -r requirements.txt
```

## env Variables

The following env variables need to be set:

```bash
export ALMA_REST_LOGFILE_DIR=             # where you want your logs saved
export ALMA_REST_ID_INSTITUTIONAL_SUFFIX= # the last four digits of your Alma IDs
export ALMA_REST_DB=                      # name of your database
export ALMA_REST_DB_USER=                 # name of your user
export ALMA_REST_DB_PW=                   # password of your user
export ALMA_REST_DB_VERBOSE=              # enable (1) or suppress (0) logging of SQLAlchemy
export ALMA_REST_API_KEY=                 # API key as per developers.exlibrisgroup.com
export ALMA_REST_API_BASE_URL=            # base URL for your Alma API calls, usually ending with 'v1'
```

**Note:** It is strongly recommended to have two separate api-keys, databases
and log files for your Sandbox and Production environment as this package
will and can not make this differentiation for you. Make sure that you default
to the env file for the Sandbox environment, e. g. by giving the file for
production an all-caps prefix.

## Input Data

As of now only the first column of the CSV- or TSV-file are relevant for
this package. The first column should include one or more Alma-IDs of the
record you want to manipulate. There is a function for retrieving content of
any column in the `db_read_write` module.

Some operations require more than one ID to work, e. g. if you want to
operate on holdings, you will also need the MMS-ID. In such cases the
**first column is still just one string with all necessary IDs separated
by comma without blanks**. The IDs should be listed from **least specific
to most specific** (e. g. MMS-ID,holding-ID,item-ID).

### Example Data
The example below shows the IDs necessary for querying a holding record in
the first column. All other columns may contain any data that is necessary
for understanding when analyzed intellectually or for defining contents of
data updates via `db_read_write.get_value_from_csv_json`.

In case of a holding record the first column should include one string with both
the MMS-ID and the holding-ID, where the MMS-ID is listed before the holding-ID.
Note how there are no blanks before and after the comma in the first column.
```text
alma-ids;title;author
991234567890123,221234567890123;How to make things up;Yours Truly
```

## `alma_rest.db_create_tables`

This script needs to be **run only once** when starting to
use the package, as it creates all necessary tables in the
database.

### Usage example

```bash
python3 -m alma_rest.db_create_tables
```

# `alma_rest.alma_rest`

Main part making use of most of the other modules.

## Actions on whole CSV lists

Adds CSV Lines to `source_csv` and `job_status_per_id` (see below)
and issues an Alma BIB API GET request per alma-id. If successful,
job_status in `job_status_per_id` will be set from "new" to "done",
otherwise "error". For all calls other than GET a second request per
alma-id is done for the action specified.

The successfully retrieved records will be saved to the table
`fetched_records`, where the whole API response content is saved
in the xml column `alma_record`. Records sent to the API for
PUT and POST calls will additionally be saved to `sent_records`.
Responses to PUT and POST calls are saved to `put_post_responses`.

When a record is updated, data in `sent_records` will be compared
to `put_post_responses`. If this comparison fails it produces
an ERROR log entry, but will do nothing else, as these cases will
need to be analyzed intellectually anyways.

**Note:** If you call the api for a record multiple times there will be a
separate row for each call in all of the aforementioned tables. These
rows can be distinguished by the `job_timestamp` set when the `alma_rest`
module is used.

### Usage Example Python Console

First parameter of the function is the path to the csv-file. Then
follow the API that needs to be called and what kind of record it
should be called for. Besides `get` there are also functions for
`update` (PUT), `create` (POST) and `delete`.

```python
from alma_rest import alma_rest
alma_rest.get_records_via_api_for_csv_list('./input/test.tsv', 'bibs', 'holdings')
```

# `alma_rest.xml_extract`

For records retrieved via GET, extract the record's API response or XML
record from the table `fetched_records`.

### Usage Example Python Console

The following extracts the XML of one holding record and returns it
as an xml.etree Element:

```python
from alma_rest import xml_extract
xml_extract.extract_record_from_fetched_records('991234567890123,221234567890123')
```

# `alma_rest.xml_modify`

For a given ElementTree object a copy is created for the manipulation.
This is to say that one should keep in mind that the returned ElementTree
differs from the one given as input.

Available operations include:
* Add a newly created Element to the root of the xml document
* Add a newly created Element to all children of root with a given path
* Remove all direct children of the root that have a given path

### Usage Example Python Console

The following appends a new Element to all children that match a specific
path:

```python
from alma_rest import xml_modify
from xml.etree.ElementTree import fromstring, tostring
my_xml_string = '<parent><child></child><child></child></parent>'
my_xml = fromstring(my_xml_string)
my_xml_modified = xml_modify.add_element_to_child(my_xml, "child", "grandchild", {"appended": "yes"}, "text")
print(tostring(my_xml_modified))
```
Gives the Output:
```python
b'<parent><child><grandchild appended="yes">text</grandchild></child><child><grandchild appended="yes">text</grandchild></child></parent>'
```

# `alma_read.input_read`

Read a CSV- or TSV-file and return information for further handling by other modules.

The **CSV- or TSV-file is expected to have a header**. There is no check
what the contents of the header are, but the import will not work correctly
if no header is given (meaning: the first line will be skipped and treated
as if it were a header).

**Note:** Be aware that only rows with valid Alma IDs in the first
column will be kept for further processing. Providing a correct value
in env var `ALMA_REST_ID_INSTITUTIONAL_SUFFIX` is crucial here.

## Check File Validity From Commandline

When used from commandline with csv-path as argv1 the script will check file validity.
It will check if the first column is a valid Alma ID. For further information
on how the according regular expression came into existence have a look at SvG's very useful
[Alma record number cheat sheet][1].

[1]: https://knowledge.exlibrisgroup.com/Alma/Community_Knowledge/How_to_-_A_cheat_sheet_for_Alma_record_numbers

### Usage Example Bash

```bash
python3 -m alma_rest.input_read ../input/testsample.csv
```

# `alma_rest.db_read_write`

Can be used to do the following:

* Create a DB session
* Insert lines from input CSV file into the table `source_csv`
* Insert valid Alma IDs into table `job_status_per_id` and set `job_status` (new, done, error)
* Get a list of IDs for a specific `action` (e. g. 'GET'), `job_timestamp` and `job_status`
* Retrieve information from CSV columns
* Extract xml from `fetched records`
* Add xml of sent records to `sent_records` table
* Add responses from the API to `put_post_responses` table
* Check if data sent equals data received for PUT and POST

Please note that this script uses **SQLAlchemy**. If the env variable
`ALMA_REST_DB_VERBOSE` is set to 1, this will **log every interaction
with the database, including all SQL-statements**. This might lead to huge
log files, but it also makes the actual interactions with the database
more transparent.

## Retrieve Information from CSV-Column

If you need to make an update with the information from a specific column of
the CSV/TSV file, you can make use of the function `get_value_from_csv_json`.

### Usage Example Python

In the following example we have a CSV/TSV file with a column that contains the
alma-ids ('IDs') and one with the desired Input for a specific MARC category.
The strings provided in the function correspond with the headings of those
columns.

```python
from alma_rest import db_read_write
db_read_write.get_value_from_source_csv('IDs', alma_id, job_timestamp, 'MARC 100')
```

## Check DB Connectivity From Commandline

When used from commandline without any arguments this script will simply make a check
whether the database is reachable. This is done via SQLAlchemy and will
not give any custom feedback. Also it will be included in the logfile.

### Usage Example Bash

```bash
python3 db_read_write.py
```

## Author

Gabriele Höfler
