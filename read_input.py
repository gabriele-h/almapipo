"""Read info from CSV and return as list

The expected input for this is a csv file of
Alma IDs in the first column and potentially information
on required manipulations in the following columns.

The output contains a list of both IDs and required
manipulations.
"""

import re
import sys
from os import path, access, R_OK
from csv import reader

alma_id_pattern_str = r"^(22|23|53|61|62|81|99)\d{2,}3332$"
pattern = re.compile(alma_id_pattern_str)


def main():
   print("Use as commandline-tool only to test a given list of IDs.")
   print("Provide the csv-file you want to test as ARGV1.")
   print("---")
   csv_path = set_csv_path_from_argv1()
   id_list = read_csv_contents_to_list(csv_path)


def set_csv_path_from_argv1() -> str:
   try:
      argv1 = sys.argv[1]
   except IndexError:
      print('Please provide CSV-file as argument.')
   else:
      if not path.exists(argv1):
         print(f'File {argv} does not exist.')
      elif not access(argv1, R_OK):
         print(f'File {argv1} is not readable.')
      elif argv1[-4:] != '.csv':
         print(f'File {argv1} does not seem to be a csv-file?')
      else:
         return sys.argv[1]


def read_csv_contents_to_list(csv_path) -> list:
   id_list = []
   with open(csv_path, newline="") as csv_file:
      csv_reader = reader(csv_file, delimiter=';', quotechar='"')
      for row in csv_reader:
         id_list.append(row[0])
   return id_list


def is_this_an_alma_id(identifier) -> bool:
   if not pattern.fullmatch(identifier):
      is_alma_id = False
      print(f"String found in list that is not an ID: {identifier}.")
   elif not identifier:
      is_alma_id = False
      print("No identifier given.")
   elif pattern.fullmatch(identifier):
      is_alma_id = True
   else:
      print("Something went utterly wrong.")
   return is_alma_id


if __name__=="__main__":
   main()
