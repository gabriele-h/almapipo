# About

## Scenario
A set of Alma-records needs to be manipulated (created, deleted, updated).

## Preparation

The Alma-IDs of the records are known and saved in a **semicolon or tab
delimited file**. The first column of that file needs to be the Alma-ID.

**Some operations require more than one ID** to work, e. g. if you want to
operate on holdings, you will also need the MMS-ID. In such cases the
**first column is still just one string**, with all necessary IDs **separated
by a comma** without any blanks. The IDs should be listed from least specific
(e. g. MMS-ID) to most specific (e. g. item-ID).

### Example Data
The example below shows the IDs necessary for querying a holding record in
the first column. All other columns as of now are not relevant and may
contain any data that is necessary for understanding when analyzed intellectually.

In case of a holding record the first column should include one string with both
the MMS-ID and the holding-ID, where the MMS-ID is listed before the holding-ID.
Note how there are no blanks before and after the comma in the first column.
```text
alma-ids;title;author
991234567890123,221234567890123;How to make things up;Yours Truly
```

## What Does This Package Do?

In a **database** both the **input** used as well as the
**status of the manipulation** are saved on a per-line or per-record basis.
All records will be fetched prior to the manipulation and a
**copy of each record before and after the manipulation** will
be kept as a backup.

Another module of the package will handle the actual **manipulation of
records in Alma via API**. If the manipulation is successful, the status for that
record will be changed from "new" to "done" in the database. If anything
goes wrong, the status will be set to "error".

# Requirements

* Python 3.7 or higher, see requirements.txt for Python packages
* A PostgreSQL, MySQL or SQLite database with read and write access
* An Alma API-key with the necessary permissions for your operations

# Initial Setup

## Set up `venv`

Please make use of a virtual environment.
See https://docs.python.org/3/library/venv.html for further info.

## Install All From `requirements.txt`

```bash
pip install -r requirements.txt
```

## env Variables

The following env variables need to be set:

```bash
export ALMA_REST_LOGFILE_DIR=             # where you want your logs saved
export ALMA_REST_ID_INSTITUTIONAL_SUFFIX= # the last four digits of your Alma IDs
export ALMA_REST_DB=                      # name of your database
export ALMA_REST_DB_USER=                 # name of your user, not needed for sqlite
export ALMA_REST_DB_PW=                   # password of your user, not needed for sqlite
export ALMA_REST_DB_DIALECT=              # supported values 'postgresql', 'mysql' or 'sqlite'
export ALMA_REST_API_KEY=                 # API key as per developmers.exlibrisgroup.com
export ALMA_REST_API_BASE_URL=            # Base URL for your Alma API calls, usually ending with 'v1'
```

## `db_create_tables.py`

This script needs to be **run only once** when starting to
use the package, as it creates all necessary tables in the
database.

# `alma_rest.py`

Main part making use of most of the other modules.

## Get BIB Records and Save in `fetched_records`

Adds CSV Lines to `source_csv` and `job_status_per_id` (see below)
and issues an Alma BIB API GET request per mms_id. If successful,
job_status in `job_status_per_id` will be set to "done", otherwise
"error".

### Usage Example Python Console

```python
import alma_rest
alma_rest.get_records_via_api_for_csv_list('./input/test.tsv')
```

## Add CSV Lines to `source_csv` and `job_status_per_id`

A convenience function makes it possible to read a whole CSV-file into
both relevant database tables. It takes two parameters:
* Path to the CSV- or TSV-file
* Intended action for the records listed ('POST', 'GET', 'PUT' or 'DELETE'). **Note:** If none is provided
this will default to 'GET'.

### Usage Example Python Console

The following example prepares a simple 'GET' action for one record with additional
information provided in the CSV-file.

```python
import alma_rest
alma_rest.import_csv_to_db_tables('./input/test.csv', 'GET')
```

# `input_read.py`

Read a CSV- or TSV-file and return information for further handling by other modules.

The **CSV- or TSV-file is expected to have a header**. There is no check what the contents
of the header are, but the import will not work correctly if no header is given (meaning: the first
line will be skipped and treated as if it were a header).

Also be aware that
**only rows with valid Alma IDs in the first column will be kept for further processing!**

## Check File Validity From Commandline

When used from commandline with csv-path as argv1 the script will check file validity.
It will check if the first column is a valid Alma ID. For further information
on how the according regular expression came into existence have a look at SvG's very useful
[Alma record number cheat sheet][1].

[1]: https://knowledge.exlibrisgroup.com/Alma/Community_Knowledge/How_to_-_A_cheat_sheet_for_Alma_record_numbers

### Usage Example Bash

```bash
python3 input_read.py ../input/testsample.csv
```

# `read_write_db.py`

Will do the following:

* Insert lines from input CSV file into the table `source_csv`
* Insert valid Alma IDs into table `job_status_per_id` and set status to "new"

Please note that this script uses **SQLAlchemy** which will **log every interaction
with the database, including all SQL-statements**. This might lead to huge
log files, but it also makes the actual interactions with the database
more transparent.

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
