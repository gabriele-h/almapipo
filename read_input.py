"""Read and check IDs from CSV and return as list

The expected input for this is a csv file of
Alma IDs in the first column and potentially information
on required manipulations in the following columns.

The output contains a list of both IDs and required
manipulations.
"""

import sys
from os import path, access, R_OK
from csv import reader


def main():
   csv_path = set_csv_path_from_argv1();
   id_list = read_csv_contents_to_list(csv_path);
   print(id_list)


def set_csv_path_from_argv1() -> str:
   try:
      csv_file_path = sys.argv[1]
   except IndexError:
      print('Please provide the path to a CSV-file as argument.')
   if not path.exists(csv_file_path):
      print('File ' + csv_file_path + ' does not exist.')
   elif not access(csv_file_path, R_OK):
      print('File ' + csv_file_path + ' is not readable.')
   elif csv_file_path[:4] != '.csv':
      print('File ' + csv_file_path + ' does not seem to be a csv-file.')

#with open(csv_file_path, newline="") as csv_file:
#   csv_reader = csv.reader(csv_file, delimiter=' ', quotechar='"')
#   for row in csv_reader:
#      print(', '.join(row))


if __name__=="__main__":
   main()
