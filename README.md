# About
The scenario which is addressed in this package is the following:
A set of Alma-records needs to be manipulated (created, deleted, updated).

The Alma-IDs of the records are known and saved in a **semicolon or tab
delimited file**. The first column of that file needs to be the Alma-ID.
All other columns may (as of now) contain whatever content the person
doing the manipulation deems necessary.

In a **PostgreSQL database** both the input used as well as the
status of the manipulation are saved on a per-line or per-record basis.

Another module of the package will handle the actual manipulation of
records in Alma via API. If the manipulation is successful, the status for that
record will be changed from "new" to "done" in the database. If anything
goes wrong, the status will be set to "error".

# Requirements
* Python 3.7 or higher, see requirements.txt for Python packages
* A PostgreSQL database with read and write access
* Ability to set environment variables

# env Variables

The following env variables need to be set:

```bash
export ALMA_REST_LOGFILE_DIR=             # where you want your logs saved
export ALMA_REST_ID_INSTITUTIONAL_SUFFIX= # the last four digits of your Alma IDs
export ALMA_REST_DB=                      # name of your psql database
export ALMA_REST_DB_USER=                 # name of your psql user
export ALMA_REST_DB_PW=                   # password of your psql user
```

# `read_input.py`

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

### Usage example

```
$ python3 read_input.py ../input/testsample.csv
Use as commandline-tool only to test a given list of IDs.
---
2020-02-25 15:38:59,136 - __main__ - INFO - Reading file ../input/testsample.csv into generator.
2020-02-25 15:38:59,136 - __main__ - WARNING - Identifier is not a valid Alma ID: 'value1'
2020-02-25 15:38:59,136 - __main__ - WARNING - The following row was discarded: OrderedDict([('header1', 'value1'), ('header2', 'value2')])
---
First valid row of csv-file: OrderedDict([('header1', '990024144550201234'), ('header2', 'foobar')])
```

# `read_write_postgres.py`

Will do the following:

* Insert lines from input CSV file into the table `source_csv`
* Insert valid Alma IDs into table `job_status_per_id` and set status to "new"

## Author

Gabriele Höfler
