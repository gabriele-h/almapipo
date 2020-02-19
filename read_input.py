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

# Logfile
logfile_dir_path = environ['ALMA_REST_LOGFILE_DIR']
logfile_path = logfile_dir_path + 'alma_rest.log'
logger_read_input = logging.getLogger('read_input')
logfile_handler = logging.FileHandler(logfile_path)
log_format_string = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
log_formatter = logging.Formatter(log_format_string)
logfile_handler.setFormatter(log_formatter)
logger_read_input.addHandler(logfile_handler)

# Pattern for Alma ID check
alma_id_suffix = environ['ALMA_REST_ID_INSTUTIONAL_SUFFIX']
alma_id_pattern_str = r"^(22|23|53|61|62|81|99)\d{2,}"+alma_id_suffix+"$"
pattern = re.compile(alma_id_pattern_str)

def main():
   # Duplicate log to stdout if called from commandline
   log_console = logging.StreamHandler()
   log_console.setFormatter(log_formatter)
   logger_read_input.addHandler(log_console)

   print("Use as commandline-tool only to test a given list of IDs.")
   print("---")
   csv_path = set_csv_path_from_argv1()
   generator_from_csv = read_csv_contents(csv_path)
   first_row = next(generator_from_csv)
   print("---")
   print(f"First valid row of csv-file: {first_row}")


def set_csv_path_from_argv1() -> str:
   try:
      argv1 = sys.argv[1]
   except IndexError:
      logger_read_input.error('Please provide CSV-file as argument.')
   else:
      if check_file_path(argv1):
         return sys.argv[1]
      else:
         sys.exit('Exiting: Check for file-path failed.')


def check_file_path(pathstring) -> bool:
   if not path.exists(pathstring):
      logger_read_input.error(f'File {pathstring} does not exist.')
   elif not access(pathstring, R_OK):
      logger_read_input.error(f'File {pathstring} is not readable.')
   elif pathstring[-4:] != '.csv' and pathstring[-4:] != '.tsv':
      logger_read_input.error(f'File {pathstring} does not seem to be a csv- or tsv-file?')
   else:
      return True


def read_csv_contents(csv_path) -> Iterable[str]:
   logger_read_input.info(f"Reading file {csv_path} into generator.")
   if csv_path[-4:] == '.csv':
      delimit = ';'
   elif csv_path[-4:] == '.tsv':
      delimit = '\t'
   with open(csv_path, newline="") as csv_file:
      csv_reader = DictReader(csv_file, delimiter=delimit)
      for row in csv_reader:
         first_column_value = list(row.values())[0]
         if is_this_an_alma_id(first_column_value):
            yield row
         else:
            pass


def is_this_an_alma_id(identifier) -> bool:
   if type(identifier) != str:
      is_alma_id = False
      logger_read_input.warn("Please provide ID as a string.")
   elif not pattern.fullmatch(identifier):
      is_alma_id = False
      logger_read_input.warn(f"Identifier is not a valid Alma ID: '{identifier}'")
   elif not identifier:
      is_alma_id = False
      logger_read_input.error("No identifier given.")
   elif pattern.fullmatch(identifier):
      is_alma_id = True
   return is_alma_id


if __name__=="__main__":
   main()
