# read\_input.py

Read a CSV- or TSV-file and return information for further handling by other modules.

The **CSV- or TSV-file is expected to have a header**. There is no check what the contents
of the header are, but will not work correctly if no header is given (meaning: the first
line will be skipped and treated as if it were a header).

When used from commandline with csv-path as argv1 the script will check file validity, though it will
actually only check if the first column is a valid Alma ID. For further information
on how the according regular expression came into existence have a look at SvG's very useful
Alma record number cheat sheet:
https://knowledge.exlibrisgroup.com/Alma/Community_Knowledge/How_to_-_A_cheat_sheet_for_Alma_record_numbers

Be aware that **only rows with valid Alma IDs in the first column will be kept for further processing!*

## Author
Gabriele Höfler
