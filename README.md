# FIRST AND FINAL VERSION - please fork!

This package was created during my employment at the Vienna Universtiy
Library and *will not be maintained by me personally*. It is open
source though, so please fork the project if you are interested
in amending and/or changing the code!

Remember when forking that, since this code is licensed under GPL3,
you will need to publish any forks under GPL3 as well.

# About *almapipo*

almapipo is short for "ALMa API client with POstgres".

The intention of having an implementation with a Postgres database is to store
the following information:
* List of IDs for which an API call was made
* Were the calls successful?
* Response contents for all successful calls (except DELETE, as there are no contents)
* Request content sent to the API for successful PUT/POST calls
* CSV files that were used as an input for the API calls

This way it should be easy to determine which API calls need to be
analyzed and/or sent another time. All data is sent and requested as XML
as this is the only format supported for all API calls. This also makes
it possible to query the database by xpath.

All calls that were done without success will log the content of
the API's response to the logfile.

## Scenario

A set of
[Alma](https://knowledge.exlibrisgroup.com/Alma/Product_Documentation/010Alma_Online_Help_%28English%29/010Getting_Started/010Alma_Introduction/010Alma_Overview)
records needs to be created, deleted, updated, or retrieved for analysis.

## Preparation

The Alma-IDs of the records are either part of a **set within Alma** or are
known and saved in a **semicolon or tab delimited file**.

Working with a set will currently work only for some kinds of sets.
Since some API calls require more than just the record's ID, but also those of
its ancestors and not all sets include that information (e.g. electronic 
portfolios).

The first column of the csv/tsv file needs to be the Alma-ID
or a list of Alma-IDs (see below "Input data").

## What Does This Package Do?

In a **Postgres database** the **status of the api call** and - where applicable -
the input data used are saved on a per-line or per-record basis.
Records will be retrieved before any change to have both the possibility to do
a before and after analysis and to possibly do a rollback. A
**copy of each record before changing actions** (retrieved via GET) will be saved to the database.
**Responses to PUT and POST** requests will be saved too.

Another module of the package will handle the actual **api calls**.
If the manipulation is successful, the status for that
record will be changed from *new* to *done* in the database table
`job_status_per_id`. If anything goes wrong, the status will be set to *error*.

**Note:** Currently all API-calls will be made with xml as the format. See 
how the format is set in the headers within `setup_rest.py`:
```
"accept": "application/xml"
"Content-Type": "application/xml"
```
This is necessary as not all APIs will support json and in general the
Alma APIs seem to be implemented xml-first.

## What Does This Package *Not* Do?

At the time I write this: A lot!

I am not implementing all the APIs with some kind of grand
scheme, but as I need them. If you want and are able <s>to contribute, I
will be happy to receive your pull requests</s> please fork the project or
see if there is already a well-maintained fork to contribute to. Or you can try using the
generic functions included in `setup_rest.py`.

## What Is *Not* Covered in This README
Modules that are not meant for day-to-day use will not be covered by
this README. They should include doc-strings though, so if you are
curious make use of python's `help`-function.

# Requirements

* Python 3.8.5 or higher, see setup.py for Python Packages
* A PostgreSQL database with read and write access
* An Alma API-key with the necessary permissions for your operations

# Initial Setup

## Set up `venv`

Please make use of a virtual environment.
See https://docs.python.org/3/library/venv.html for further info.

The venv should be inside a folder where you intend to write
scripts making use of the almapipo package.

## Install almapipo

The requirements are defined within `setup.py`. Currently this package
is not listed on https://pypi.org/, as this is the first and final version.

After activating the venv within the folder where you want to put your according scripts,
you can do `pip install` followed by the path where you put the git download of the
almapipo package (workaround as long as almapipo is not public on pypi).

**Note:**
* psycopg2 is among the requirements. See
[Build prerequisites](
https://www.psycopg.org/docs/install.html#build-prerequisites
)
for further info or refer to
[Quick Install](https://www.psycopg.org/docs/install.html#quick-install)
on the same page.
* Python's standard xml package has some [XML vulnerabilities](
https://docs.python.org/3/library/xml.html#xml-vulnerabilities
), so make sure to only use trusted data as input.

## env Variables

The following env variables need to be set:

```bash
export ALMA_REST_LOGFILE_DIR=             # where you want your logs saved
export ALMA_REST_ID_INSTITUTIONAL_SUFFIX= # the last four digits of your Alma IDs
export ALMA_REST_DB=                      # name of your database
export ALMA_REST_DB_USER=                 # name of your database user
export ALMA_REST_DB_PW=                   # password of your database user
export ALMA_REST_DB_URL=                  # url if your database is remote, set 'localhost' otherwise
export ALMA_REST_DB_VERBOSE=              # enable (1) or suppress (0) logging of SQLAlchemy, suppressed by default
export ALMA_REST_API_KEY=                 # API key as per developers.exlibrisgroup.com
export ALMA_REST_API_BASE_URL=            # base URL for your Alma API calls, usually ending with 'v1'
```

**Note:** It is strongly recommended using two separate api-keys, databases
and log files for your sandbox and production environment as this package
will and can not make this differentiation for you. Make sure that you default
to the env file for the sandbox environment, e.g. by giving the file for
production an all-caps prefix.

## Input Data

### Alma Set

You can make use of a function that extracts the `link` attribute of all
members in a set. Please note - as mentioned above - that not all sets will
have the link attribute in their members. Without a link attribute, the function
`rest_conf.retrieve_set_member_almaids` will make use of the `id` element of
each member. If the path to the member is more complex and includes ancestors,
making use of such an Alma set (e.g. electronic portfolios) will not be possible.

#### Usage example

The following function will iterate through the set by 100 at a time and
yield the `almaid` of each record:

```python
from almapipo import rest_conf
almaids = rest_conf.retrieve_set_member_almaids('1199999999123')
```

### CSV or TSV file

As of now only the first column of the CSV or TSV file is relevant for
this package. The first column should include one or more Alma-IDs of the
record you want to manipulate. There is a function for retrieving content of
any column in the `db_read` module.

Some operations require more than one ID to work, e.g. if you want to
operate on holdings, you will also need the MMS-ID. In such cases the
**first column is still just one string with all necessary IDs separated
by commas without blanks**. The IDs should be listed from **least specific
to most specific** (e.g. MMS-ID,holding-ID,item-ID).

#### Example Data
The example below shows the IDs necessary for querying a holding record in
the first column. All other columns may contain any data that is necessary
for understanding when analyzed intellectually or for defining contents of
data updates via `db_read.get_value_from_source_csv`.

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

To get an idea of which tables will be created and what contents they have,
take a look at the module `setup_db`.

### Usage example

```bash
db_create_tables
```

## Make a Test Call to the API

Usually you will not need to directly access the module `setup_rest`.
You might find `test_calls_remaining_today` useful though, as it creates a message
with the number of remaining API calls. It's perfect for a first call to the API
as it requires no parameters at all and provides information you will need
in the future. It returns the number of left calls and adds info to a logger.

**Note:** The function itself makes a call to /bibs/test and will be counted as an API call,
possibly triggering your threshold-limits.

```python
from almapipo import setup_rest

num_calls = setup_rest.test_calls_remaining_today()
print(num_calls)
```
Output should look something like this:
```text
54123
```
If it does not and there is no python error message, check the logfile.
There might be something missing and/or wrong in your configuration.

If it does look like that, you can find the same message in the logfile.

# `almapipo.almapipo`

Main part making use of most of the other modules.

## Actions on lists of Alma-IDs

There is one function to issue an Alma API request per alma-id. If successful,
job\_status in `job_status_per_id` will be set from "new" to "done",
otherwise "error". For all calls other than GET a second request per
alma-id is done for the action specified, so there will be two
lines in `job_status_per_id` for those function calls per alma\_id.

**Note:**  Currently there are no GET calls before POST calls.

The successfully retrieved records will be saved to the table
`fetched_records`, where the whole API response content is saved
in the xml column `alma_record`. Records sent to the API for
PUT and POST calls will additionally be saved to `sent_records`.
Responses to PUT and POST calls are saved to `put_post_responses`.

**Note:** If you call the api for a record multiple times there will be a
separate row for each call in all mentioned tables. These
rows can be distinguished by the `job_timestamp` set when the `almapipo`
module is imported.

### Usage Examples Python Console

First parameter of the function is a list of ids to make the calls for. Then
follow the API that needs to be called and what kind of record it
should be called for. The final parameter is the method.

#### Using a csv File as Input: call\_api\_for\_list

The following will import the CSV lines to the table `source_csv` and
create a generator of alma\_ids. If you want to make sure you are handling
valid alma\_ids only, set `validation` to true in CsvHelper, which checks 
whether the first column contained a valid `almaid`. It defaults to false.

```python
from almapipo import almapipo, config, db_connect, input_helpers

with db_connect.DBSession() as dbsession:

    csv_helper = input_helpers.CsvHelper('./test_hols.tsv')
    csv_helper.add_to_source_csv_table(config.job_timestamp, dbsession)
    
    almapipo.call_api_for_list(csv_helper.extract_almaids(), 'bibs', 'holdings', 'GET', dbsession)
```

#### Using a Set as Input: call\_api\_for\_set

The function `call_api_for_set` will add a line to `job_status_per_id` for
the given `set_id`. If the function `rest_conf.retrieve_set_member_almaids`
does not return the expected Iterable, the status within
`job_status_per_id` will be updated to `error`. This will
happen if the set is empty or does not exist, otherwise the status for the
`set_id` will be set to `done`.

**Note:** `call_api_for_set` makes use of `call_api_for_list`.

```python
from almapipo import almapipo, db_connect

with db_connect.DBSession() as dbsession:
    set_id = '123123123123123'
    almapipo.call_api_for_alma_set(set_id, 'bibs', 'bibs', 'GET', dbsession)
```

**Note:** As mentioned above this will not work for all kinds of sets.
Use `help(rest_conf.retrieve_set_member_almaids)` for more info.

# `almapipo.xml_extract`

For records retrieved via GET, extract the record's API response or XML
record from the table `fetched_records`.

### Usage Example Python Console

The following extracts the XML of the most recent version of one holding
record and returns it as an xml.etree Element:

```python
from almapipo import db_connect, xml_extract

with db_connect.DBSession() as dbsession:
    xml_extract.extract_response_from_fetched_records('991234567890123,221234567890123', dbsession)
```

# `almapipo.xml_modify`

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
from almapipo import xml_modify
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

# `almapipo.input_read`

Read a CSV- or TSV-file and return information for further handling by other modules.

The **CSV- or TSV-file is expected to have a header**. There is no check
what the contents of the header are, but the import will not work correctly
if no header is given (meaning: the first line will be skipped and treated
as if it were a header).

**Note:** Be aware that only rows with valid Alma IDs in the first
column will be kept for further processing. Providing a correct value
in env var `ALMA_REST_ID_INSTITUTIONAL_SUFFIX` is crucial here.

# `almapipo.db_read`

Can be used to do the following:

* Get a list of IDs for a specific `action` (e.g. 'GET'), `job_timestamp` and `job_status`
* Retrieve information from CSV columns
* Extract xml from table `fetched\_records`
* Check if data sent equals data received for PUT and POST

Please note that this script uses **SQLAlchemy**. If the env variable
`ALMA_REST_DB_VERBOSE` is set to 1, this will **log every interaction
with the database, including all SQL-statements**. This might lead to huge
log files, but it also makes the actual interactions with the database
more transparent.

## Retrieve Information from CSV-Column

If you need to make an update with the information from a specific column of
the CSV/TSV file, you can make use of the function `get_value_from_source_csv`.

### Usage Example Python

In the following example we have a CSV/TSV file with a column that contains the
alma-ids and one with the title for that record (see **Example Data** above).
The strings provided in the function correspond with the headings of those
columns.

```python
from almapipo import db_connect, db_read
from datetime import datetime, timezone

almaid = "991234567890123,221234567890123"
job_timestamp = datetime(2020, 2, 20, 20, 00, 20, timezone.utc)

with db_connect.DBSession() as dbsession:
    db_read.get_value_from_source_csv('alma-ids', almaid, job_timestamp, 'title', dbsession)
```

# `almapipo.db_write`

Can be used to do the following:

* Insert lines from input CSV file into the table `source_csv`
* Insert valid Alma IDs into table `job_status_per_id` and set `job_status` (new, done, error)
* Add xml of sent records to `sent_records` table
* Add responses from the API to `put_post_responses` table

# Scripts Added to PATH

The following will only work after activating your venv, which adds the scripts
to your PATH variable.

## Create DB tables: `db_create_tables`

This is only necessary for the initial Setup of a newly defined database. You
will have to run this for both databases you use for production and sandbox
API calls - it is highly recommended keeping these in separate databases!

## Delete Holdings: `delete_hol`

For a CSV file containing a list of "MMSID,HOLID", delete the corresponding
holdings. The CSV file needs to have a heading.

The holdings will be fetched first to have a backup in the database in
case of erroneous deletions.

## Check File Validity From Commandline: `input_check`

When used from commandline with csv-path as argv1 the script will check file validity.
It will check if the first column is a valid Alma ID. For further information
on how the according regular expression came into existence have a look at the
[Knowledge Center documentation on Alma Record Numbers][1].

[1]: https://knowledge.exlibrisgroup.com/Alma/Product_Documentation/010Alma_Online_Help_(English)/Metadata_Management/005Introduction_to_Metadata_Management/020Record_Numbers

### Usage Example Bash

```bash
input_check ../input/testsample.csv
```

## Export Locations: `locations_export`

For all libraries of an institution retrieve all locations and build an XML file
that contains the retrieved information. The resulting XML file
can be opened in Excel.

It has one required and one kind of optional argument: the path to the output file and
the language(s) to make the export for. en_US will always be exported and any further
language(s) provided will be appended.

### Usage Example Bash

```bash
locations_export output_of_almapipo_locations_export.xml --addLang=de_DE --addLang=fr_FR
```

## Update by CSV-contents: `update_by_csv`

This script will take a CSV-file with a specific layout, try to interpret
its contents and make API-updates accordingly - USE WITH CARE.
For example with the following CSV:

```csv
"bibs,holdings,items";"item_data/description"
991234000003123,221234000003123,231234000003123;"2nd Edition"
994321000003123,224321000003123,234321000003123;"1.2020"
```

The script will assume the following things:
* Update the record ("PUT") - this is always standard
* API is "bibs", record type is "items" - set in the heading of the first column
* Element to update has the X-path "item\_data/description" - set in the heading of the second column
* First column contains necessary Alma-IDs for the update
* Second column contains contents to **replace** the text of the x-path element by, if neither --append nor --prepend were set
* **Optional:** Provide --append or --prepend to change existing text instead of replacing it

## Update Element by XPATH in a set of records: `update_record_element`

For a given Alma set, update one record element's text.

### Usage Example Bash
```bash
update_record_element 123123123 'bibs' 'items' 'item/data_description' 'New description'
```

# So you want to query the database

There will be times when you need to have a look at the data that
is stored in the database. Here are some examples that might prove
useful.

## PUT/POST data does not equal response

The function `db_read.get_value_from_source_csv` will make
use of a similar query with the difference of creating and ID
consisting of a concatenation of `almaid` and `job_timestamp`.

```sql
SELECT put_post_responses.almaid
  FROM sent_records
  JOIN put_post_responses
	ON sent_records.job_timestamp = put_post_responses.job_timestamp
	AND sent_records.almaid = put_post_responses.almaid
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

## Get content of CSV by column heading for one `almaid`

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
