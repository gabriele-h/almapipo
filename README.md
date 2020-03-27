# env Variables

The following env variables need to be set:
* ALMA\_REST\_LOGFILE\_DIR - where you want your logs saved
* ALMA\_REST\_ID\_INSTITUTIONAL\_SUFFIX - the last four digits of your Alma IDs
* ALMA\_REST\_DB - name of your psql database
* ALMA\_REST\_DB\_USER - name of your psql user
* ALMA\_REST\_DB\_PW - password of your psql user

# read\_input.py

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
Alma record number cheat sheet:
https://knowledge.exlibrisgroup.com/Alma/Community_Knowledge/How_to_-_A_cheat_sheet_for_Alma_record_numbers

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

# read\_write\_postgres.py

Will do the following:
* Insert lines from input CSV file into the table source\_csv
* Insert valid Alma IDs into table job\_status\_per\_id and set status to "new"

## Author
Gabriele Höfler
