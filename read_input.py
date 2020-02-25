"""Read info from CSV and return as list

The expected input for this is a csv file of
Alma IDs in the first column and potentially information
on required manipulations in the following columns.

The output contains a list of both IDs and required
manipulations.
"""

import logging
import re
import sys
from os import access, environ, path, R_OK
from csv import DictReader
from typing import Iterable

import logfile_setup

# Logfile
logger = logging.getLogger(__name__)

# Pattern for Alma ID check
alma_id_suffix = environ['ALMA_REST_ID_INSTUTIONAL_SUFFIX']
alma_id_pattern_str = r"^(22|23|53|61|62|81|99)\d{2,}"+alma_id_suffix+"$"
pattern = re.compile(alma_id_pattern_str)

def main():
   """When used from commandline, the read_input will only validate
   the contents of the file provided via arg1 and output some information
   in that regard."""
   logfile_setup.log_to_stdout(logger)

   print("Use as commandline-tool only to test a given list of IDs.")
   print("---")
   csv_path = set_csv_path_from_argv1()
   generator_from_csv = read_csv_contents(csv_path)
   first_row = next(generator_from_csv)
   print("---")
   print(f"First valid row of csv-file: {first_row}")


def set_csv_path_from_argv1() -> str:
   """Only relevant if read_input is run from commandline."""
   try:
      argv1 = sys.argv[1]
   except IndexError:
      logger.error('Please provide CSV-file as argument.')
   else:
      if check_file_path(argv1):
         return sys.argv[1]
      else:
         sys.exit('Exiting: Check for file-path failed.')


def check_file_path(path: str) -> bool:
   """Checks filepath for existence, readability and whether the file is
   ending with either .csv or .tsv"""
   if not path.exists(pathstring):
      logger.error(f'File {pathstring} does not exist.')
   elif not access(pathstring, R_OK):
      logger.error(f'File {pathstring} is not readable.')
   elif pathstring[-4:] != '.csv' and pathstring[-4:] != '.tsv':
      logger.error(f'File {pathstring} does not seem to be a csv- or tsv-file?')
   else:
      return True


def read_csv_contents(csv_path: str, validation: bool) -> Iterable[str]:
   """Feeds the contents of a CSV file into a generator via DictReader.
   If the first column does not match an Alma ID, the whole row
   will be discarded."""
   logger.info(f"Reading file {csv_path} into generator.")
   if csv_path[-4:] == '.csv':
      delimit = ';'
   elif csv_path[-4:] == '.tsv':
      delimit = '\t'
   with open(csv_path, newline="") as csv_file:
      csv_reader = DictReader(csv_file, delimiter=delimit)
      for row in csv_reader:
         first_column_value = list(row.values())[0]
         if is_this_an_alma_id(first_column_value) \
                 or validation == False:
            yield row
         else:
            logger.warn(f"The following row was discarded: {row}")


def is_this_an_alma_id(identifier: str) -> bool:
   """Expected input is a string of an identifier. This function checks
   if the ID provided matches the expected pattern of Alma IDs."""
   if type(identifier) != str:
      is_alma_id = False
      logger.warn("Please provide ID as a string.")
   elif not pattern.fullmatch(identifier):
      is_alma_id = False
      logger.warn(f"Identifier is not a valid Alma ID: '{identifier}'")
   elif not identifier:
      is_alma_id = False
      logger.error("No identifier given.")
   elif pattern.fullmatch(identifier):
      is_alma_id = True
   return is_alma_id


if __name__=="__main__":
   main()
