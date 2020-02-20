# env Variables

The following env variables need to be set:
* ALMA\_REST\_LOGFILE\_DIR - where you want your logs saved
* ALMA\_REST\_ID\_INSTUTIONAL\_SUFFIX - the last four digits of your Alma IDs
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

## Author
Gabriele Höfler
