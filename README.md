# About
The scenario which is addressed in this package is the following:
A set of Alma-records needs to be manipulated (created, deleted, updated).

The Alma-IDs of the records are known and saved in a **semicolon or tab
delimited file**. The first column of that file needs to be the Alma-ID.
All other columns may (as of now) contain whatever content the person
doing the manipulation deems necessary.

In a **database** both the input used as well as the
status of the manipulation are saved on a per-line or per-record basis.

Another module of the package will handle the actual manipulation of
records in Alma via API. If the manipulation is successful, the status for that
record will be changed from "new" to "done" in the database. If anything
goes wrong, the status will be set to "error".

# Requirements
* Python 3.7 or higher, see requirements.txt for Python packages
* A PostgreSQL, MySQL or SQLite database with read and write access
* An Alma API-key with the necessary permissions for your operations

# env Variables

The following env variables need to be set:

```bash
export ALMA_REST_LOGFILE_DIR=             # where you want your logs saved
export ALMA_REST_ID_INSTITUTIONAL_SUFFIX= # the last four digits of your Alma IDs
export ALMA_REST_DB=                      # name of your database
export ALMA_REST_DB_USER=                 # name of your user, not needed for sqlite
export ALMA_REST_DB_PW=                   # password of your user, not needed for sqlite
export ALMA_REST_DB_DIALECT=              # supported values 'postgresql', 'mysql' or 'sqlite'
export ALMA_REST_API_KEY=                 # API key as per developmers.exlibrisgroup.com
export ALMA_REST_API_BASE_URL=            # Base URL for your Alma instance
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

```
$ python3 input_read.py ../input/testsample.csv
Use as commandline-tool only to test a given list of IDs.
---
2020-02-25 15:38:59,136 - __main__ - INFO - Reading file ../input/testsample.csv into generator.
2020-02-25 15:38:59,136 - __main__ - WARNING - Identifier is not a valid Alma ID: 'value1'
2020-02-25 15:38:59,136 - __main__ - WARNING - The following row was discarded: OrderedDict([('header1', 'value1'), ('header2', 'value2')])
---
First valid row of csv-file: OrderedDict([('header1', '990024144550201234'), ('header2', 'foobar')])
```

# `read_write_db.py`

Will do the following:

* Insert lines from input CSV file into the table `source_csv`
* Insert valid Alma IDs into table `job_status_per_id` and set status to "new"

Please note that this script uses **SQLAlchemy** which will **log every interaction
with the database, including all SQL-statements**. This might lead to huge
log files, but it also makes the actual interactions with the database
more transparent.

## Read CSV File Into Tables `source_csv` and `job_status_per_id`

A convenience function makes it possible to read a whole CSV-file into
both relevant database tables. It takes two parameters:
* Path to the CSV- or TSV-file
* Intended action for the records listed ('POST', 'GET', 'PUT' or 'DELETE'). **Note:** If none is provided
this will default to 'GET'.

### Usage Example Python Console

The following example prepares a simple 'GET' action for one record with additional
information provided in the CSV-file.

```
>>> import db_read_write
>>> db_read_write.import_csv_to_db_tables('./input/test.csv', 'GET')
2020-05-07 08:47:18,380 INFO sqlalchemy.engine.base.Engine SELECT CAST('test plain returns' AS VARCHAR(60)) AS anon_1
2020-05-07 08:47:18,380 INFO sqlalchemy.engine.base.Engine ()
2020-05-07 08:47:18,380 INFO sqlalchemy.engine.base.Engine SELECT CAST('test unicode returns' AS VARCHAR(60)) AS anon_1
2020-05-07 08:47:18,381 INFO sqlalchemy.engine.base.Engine ()
2020-05-07 08:47:18,381 INFO sqlalchemy.engine.base.Engine BEGIN (implicit)
2020-05-07 08:47:18,382 INFO sqlalchemy.engine.base.Engine INSERT INTO source_csv (job_timestamp, csv_line) VALUES (?, ?)
2020-05-07 08:47:18,382 INFO sqlalchemy.engine.base.Engine ('2020-05-07 08:46:41.724602', '{"Item Id": "221234567890123", "Inventory Number": "I-1234", "Inventory Date": "2020-05-07", "Stat
istics Note 1": "My test"}')
2020-05-07 08:47:18,390 INFO sqlalchemy.engine.base.Engine INSERT INTO job_status_per_id (job_timestamp, alma_id, job_status, job_action) VALUES (?, ?, ?, ?)
2020-05-07 08:47:18,390 INFO sqlalchemy.engine.base.Engine ('2020-05-07 08:46:41.724602', '221234567890123', 'new', 'GET')
2020-05-07 08:47:18,391 INFO sqlalchemy.engine.base.Engine COMMIT
```

## Check DB Connectivity From Commandline

When used from commandline without any arguments this script will simply make a check
whether the database is reachable. This is done via SQLAlchemy and will
not give any custom feedback. Also it will be included in the logfile.

### Usage Example Bash

```
$ python3 db_read_write.py
2020-05-07 08:19:23,628 INFO sqlalchemy.engine.base.Engine SELECT CAST('test plain returns' AS VARCHAR(60)) AS anon_1
2020-05-07 08:19:23,628 INFO sqlalchemy.engine.base.Engine ()
2020-05-07 08:19:23,631 INFO sqlalchemy.engine.base.Engine SELECT CAST('test unicode returns' AS VARCHAR(60)) AS anon_1
2020-05-07 08:19:23,632 INFO sqlalchemy.engine.base.Engine ()
```

## Author

Gabriele Höfler
