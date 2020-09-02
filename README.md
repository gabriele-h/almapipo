# About

## Scenario

A set of
[Alma](https://knowledge.exlibrisgroup.com/Alma/Product_Documentation/010Alma_Online_Help_%28English%29/010Getting_Started/010Alma_Introduction/010Alma_Overview)
records needs to be created, deleted, updated, or retrieved for analysis.

## Preparation

The Alma-IDs of the records are either part of a **set within Alma** or are
known and saved in a **semicolon or tab delimited file**.

Working with a set will currently work only for some kinds of sets.
Since some API calls require more than just the record's ID, but also those of
its ancestors, and only some of the sets will have a link to their members,
calls on the sets of e. g. electronic portfolios are
not supported until the missing link attribute is hopefully fixed by Ex Libris
(see case 00874282).

The first column of the csv/tsv file needs to be the Alma-ID
or a list of Alma-IDs (see below "Input data").

## What Does This Package Do?

In a **Postgres database** the **status of the api call** and - where applicable -
the input data used are saved on a per-line or per-record basis.
All records will be retrieved prior to deletion, update, or creation. A
**copy of each record before the action** will be saved to the database.
**Responses to PUT and POST** requests will be saved too.

Another module of the package will handle the actual **api calls**.
If the manipulation is successful, the status for that
record will be changed from *new* to *done* in the database table
`job_status_per_id`. If anything goes wrong, the status will be set to *error*.

**Note:** Currently all API-calls will be made with xml as the format. See 
how the format is set in the headers within `rest_setup.py`:
```
"accept": "application/xml"
"Content-Type": "application/xml"
```
This is necessary as not all APIs will support json and in general the
Alma APIs seem to be implemented xml-first.

## What Does This Package *Not* Do?

At the time I write this: A lot!

Currently I am not implementing all the APIs with some kind of grand
scheme, but as I need them. If you want and are able to contribute, I
will be happy to receive your pull requests. Or you can try using the
generic functions included in `rest_setup.py`. If both is not an option:
Get in touch!

## What Is *Not* Covered in This README
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
has just one entry referring to that.

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
export ALMA_REST_DB_URL=                  # url if your database is remote, set 'localhost' otherwise
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

### Alma Set

You can make use of a function that extracts the `link` attribute of all
members in a set. Please note - as mentioned above - that not all sets will
have the link attribute in their members. Without a link attribute, the function
`rest_conf.retrieve_set_member_alma_ids` will make use of the `id` element of
each member. If the path to the member is more complex and includes ancestors,
making use of such an Alma set (such as electronic portfolios) will not be possible.

#### Usage example

The following function will iterate trough the set by 100 at a time and
yield the `alma_id` of each record, making it a generator:

```python
from alma_rest import rest_conf
alma_ids = rest_conf.retrieve_set_member_alma_ids('1199999999123')
```

### CSV or TSV file

As of now only the first column of the CSV or TSV file are relevant for
this package. The first column should include one or more Alma-IDs of the
record you want to manipulate. There is a function for retrieving content of
any column in the `db_read_write` module.

Some operations require more than one ID to work, e. g. if you want to
operate on holdings, you will also need the MMS-ID. In such cases the
**first column is still just one string with all necessary IDs separated
by comma without blanks**. The IDs should be listed from **least specific
to most specific** (e. g. MMS-ID,holding-ID,item-ID).

#### Example Data
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

## `db_create_tables`

This script needs to be **run only once** when starting to
use the package, as it creates all necessary tables in the
database.

### Usage example

```bash
db_create_tables
```

## Make a Test Call to the API

Usually you will not need to directly access the module `rest_setup`.
You might find `test_calls_remaining_today` useful though, as it creates a message
with the number of remaining API calls. It's perfect for a first call to the API
as it requires no parameters at all and provides information you will need
in the future.

**Note:** The function itself makes a call to /bibs/test and will be counted as an API call.

```python
from alma_rest import rest_setup
rest_setup.test_calls_remaining_today()
```
Output should look something like this:
```text
API calls left for today: 54123
```
If it does not and there is no python error message, check the logfile.
There might be something missing and/or wrong in your configuration.

If it does look like that, you can find the same message in the logfile.

# `alma_rest.alma_rest`

Main part making use of most of the other modules.

## Actions on whole CSV lists

There are four functions for create, delete, retrieve, and update to
operate on whole CSV lists. These will
add CSV Lines to `source_csv` and `job_status_per_id` (see below)
and issue an Alma API request per alma-id. If successful,
job_status in `job_status_per_id` will be set from "new" to "done",
otherwise "error". For all calls other than GET a second request per
alma-id is done for the action specified, so there will be two
lines in `job_status_per_id` for those function calls per alma_id.

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

### Usage Examples Python Console

First parameter of the function is list of ids to make the calls for. Then
follow the API that needs to be called and what kind of record it
should be called for. Final parameter is the method.

#### Using a tsv File as Input

```python
from alma_rest import alma_rest
alma_id_list = alma_rest.csv_id_generator_and_import_source_csv('./test_hols.tsv')
alma_rest.call_api_for_list(alma_id_list, 'bibs', 'holdings', 'GET')
```

#### Using a Set as Input

```python
from alma_rest import alma_rest
from alma_rest import rest_conf
set_id = '123123123123123'
alma_id_list = rest_conf.retrieve_set_member_alma_ids(set_id)
alma_rest.call_api_for_list(alma_id_list, 'bibs', 'bibs', 'GET')
```

**Note:** As mentioned above this will not work for all kinds of sets.
Use `help(rest_conf.retrieve_set_member_alma_ids)` for more info.

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

# `alma_rest.input_read`

Read a CSV- or TSV-file and return information for further handling by other modules.

The **CSV- or TSV-file is expected to have a header**. There is no check
what the contents of the header are, but the import will not work correctly
if no header is given (meaning: the first line will be skipped and treated
as if it were a header).

**Note:** Be aware that only rows with valid Alma IDs in the first
column will be kept for further processing. Providing a correct value
in env var `ALMA_REST_ID_INSTITUTIONAL_SUFFIX` is crucial here.

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
alma-ids and one with the title for that record (see **Example Data** above).
The strings provided in the function correspond with the headings of those
columns.

```python
from alma_rest import db_read_write
from datetime import datetime, timezone
alma_id = "991234567890123,221234567890123"
job_timestamp = datetime(2020, 2, 20, 20, 00, 20, timezone.utc)
db_read_write.get_value_from_source_csv('alma-ids', alma_id, job_timestamp, 'title')
```

# Scripts Added to PATH

The following will only work after activating your venv, which adds the scripts
to your PATH variable.

## Extract MARC as TSV

This will work only for records that have prior been fetched via GET.

Currently work in progress, more documentation soon.

## Check File Validity From Commandline

When used from commandline with csv-path as argv1 the script will check file validity.
It will check if the first column is a valid Alma ID. For further information
on how the according regular expression came into existence have a look at SvG's very useful
[Alma record number cheat sheet][1].

[1]: https://knowledge.exlibrisgroup.com/Alma/Community_Knowledge/How_to_-_A_cheat_sheet_for_Alma_record_numbers

### Usage Example Bash

```bash
input_check ../input/testsample.csv
```

## Create All Necessary DB Tables

See above "Initial Setup" for information on this script. Should be used for initial setup of
the Postgres database only.

# So you want to query the database

There will be times when you need to have a look at the data that
is stored in the database. Here are some examples that might prove
useful.

## PUT/POST data does not equal response

The function `db_read_write.get_value_from_source_csv` will make
use of a similar query with the difference of creating and ID
consisting of a concatenation of `alma_id` and `job_timestamp`.

```sql
SELECT put_post_responses.alma_id
  FROM sent_records
  JOIN put_post_responses
	ON sent_records.job_timestamp = put_post_responses.job_timestamp
	AND sent_records.alma_id = put_post_responses.alma_id
  WHERE CAST(sent_records.alma_record AS VARCHAR) != cast(put_post_responses.alma_record AS VARCHAR);
```

## Contents of MARC holding category subfield

Similar queries can be built for tables `sent_records` and
`put_post_responses`.

```sql
SELECT xpath('//holding/record/datafield[@tag=245]/subfield', alma_record)
  FROM fetched_records
  WHERE job_timestamp = '2020-02-02 20:02:02.202002+00:00';
```

If you want to see only entries of records that match a specific xpath,
add a WHERE clause. For example the following will only list bib records:

```sql
WHERE cast(xpath('//bib', alma_record) as text[]) != '{}';
```

## Count number of records for `job_timestamp` and `job_action`

Good for comparing the number of lines in your CSV file to what
was saved in the `job_status_per_id` table. If you want to check
the status you might add another condition on `job_status`.

```sql
SELECT count(primary_key)
  FROM job_status_per_id
  WHERE job_timestamp = '2020-02-02 20:02:02.202002+00:00'
  AND job_action = 'GET';
```

## Get content of CSV by column heading for one `alma_id`

In this example you would have to replace 'MMS Id,HOL Id' by the
column heading of your first column and 'HOL 245' by the column
heading of the column you want to query.

```sql
SELECT csv_line -> 'MMS Id,HOL Id', csv_line -> 'HOL 245' as info
  FROM source_csv
  WHERE job_timestamp = '2020-02-02 20:02:02.202002+00:00'
  AND csv_line ->> 'MMS Id,HOL Id' = '990068822450203332,22337530320003332';
```

# Acknowledgements

I could not have written this package without meeting the following people:

Stefan Karner, who I worked with on the [ONB Labs](https://labs.onb.ac.at/en/).
With patience and empathy he taught me a lot about programming with Python
in general and OOP in special.

Christoph Schindler, who keeps telling me to write something that works first
and worry about everything else later. I might not have come far without
his constant and kind support.

The system librarian team of the Vienna University Library, who are a joy
to work with! They provided me with real life examples to test my code on
and helped me with some design decisions.

# Author

Gabriele Höfler
