"""Read info from CSV/TSV and return as list

The expected input for this is a csv or tsv file with
Alma IDs in the first column and potentially information
on required manipulations in the following columns. The
file needs to have a header, csv needs to be
semicolon-delimited.

The output contains a list of both IDs and required
manipulations.
"""

import re
import sys
from csv import DictReader
from logging import getLogger
from os import access, environ, path, R_OK
from typing import Iterator

import logfile_setup

# Logfile
logger = getLogger(__name__)

ID_SUFFIX_PATTERN = r"^(22|23|53|61|62|81|99)\d{{2,}}{alma_id_suffix}$"


def main():
    """
    When used from commandline, read_input will only validate
    the contents of the file provided via argv1 and output the
    the first valid line or information on why it failed to do so.
    :return: None
    """
    logfile_setup.log_to_stdout(logger)

    print("Use as commandline-tool only to test a given list of IDs for validity.")
    print("---")
    csv_path = set_csv_path_from_argv1()
    generator_from_csv = read_csv_contents(csv_path, True)
    first_row = next(generator_from_csv)
    print("---")
    print(f"First valid row of csv-file: {first_row}")


def set_csv_path_from_argv1() -> str:
    """
    Only relevant if read_input is run from commandline.
    :return: String of the file-path provided as argv1.
    """
    try:
        argv1 = sys.argv[1]
    except IndexError:
        logger.error('Please provide CSV-file as argument.')
        sys.exit(1)
    else:
        if check_file_path(argv1):
            return sys.argv[1]
        else:
            sys.exit('Exiting: Check for file-path failed.')


def check_file_path(file_path: str) -> bool:
    """
    Checks file path for existence, readability and whether the file is
    ending on either .csv or .tsv
    :param file_path: Absolute or relative path to the csv/tsv file.
    :return: Boolean to indicate if the provided file exists, is readable and ends on .csv or .tsv.
    """
    if not path.exists(file_path):
        logger.error(f'File {file_path} does not exist.')
    elif not access(file_path, R_OK):
        logger.error(f'File {file_path} is not readable.')
    elif file_path[-4:] != '.csv' and file_path[-4:] != '.tsv':
        logger.error(f'File {file_path} does not seem to be a csv- or tsv-file?')
    else:
        return True


def read_csv_contents(csv_path: str, validation: bool = True) -> Iterator[str]:
    """
    Feeds the contents of a csv or tsv file into a generator via DictReader.
    If the first column does not match an Alma ID, the whole row
    will be discarded. This validation can be overridden with the
    second param of the function set to False.
    :param csv_path: Relative or absolute path to a csv or tsv file.
    :param validation: If set to "False", the first column will not be checked for validity.
    :return: Generator of csv/tsv file lines as dictionaries.
    """
    logger.info(f"Reading file {csv_path} into generator.")
    if csv_path[-4:] == '.csv':
        delimit = ';'
    elif csv_path[-4:] == '.tsv':
        delimit = '\t'
    else:
        logger.error(f"Extension of the given file not expected (csv for semicolon, tsv for tabs).")
        sys.exit(1)
    with open(csv_path, newline="") as csv_file:
        csv_reader = DictReader(csv_file, delimiter=delimit)
        for row in csv_reader:
            first_column_value = list(row.values())[0]
            if all(is_this_an_alma_id(string) for string in str.split(first_column_value, ',')) \
                    or not validation:
                yield row
            else:
                logger.warning(f"The following row was discarded: {row}")


def is_this_an_alma_id(identifier: str) -> bool:
    """
    Expected input is a string of an identifier. This function checks
    if the ID provided matches the expected pattern of Alma IDs.
    :param identifier: String to be verified as an Alma-ID.
    :return: Boolean indicating the status of the verification.
    """
    if type(identifier) != str:
        logger.warning("Please provide ID as a string.")
        return False

    if not identifier:
        logger.error("No identifier given.")
        return False

    try:
        alma_id_suffix = environ['ALMA_REST_ID_INSTITUTIONAL_SUFFIX']
    except KeyError:
        logger.error("Env var 'ALMA_REST_ID_INSTITUTIONAL_SUFFIX' not set.")
        exit(1)

    pattern = ID_SUFFIX_PATTERN.format(alma_id_suffix=alma_id_suffix)
    if re.fullmatch(pattern, identifier):
        return True

    logger.warning(f"Identifier is not a valid Alma ID: '{identifier}'")
    return False


if __name__ == "__main__":
    main()
