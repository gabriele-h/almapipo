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
import warnings
from csv import DictReader
from logging import getLogger
from os import access, environ, path, R_OK
from typing import Iterable

# Logfile
logger = getLogger(__name__)

ALMA_ID_PATTERN = r"^(22|23|53|61|62|81|99)\d{{2,}}{alma_id_suffix}$"


def read_csv_contents(
        csv_path: str,
        validation: bool = False) -> Iterable[dict]:
    """
    Feeds the contents of a csv or tsv file into a generator via DictReader.
    If the first column does not match an Alma ID, the whole row
    will be discarded. This validation can be overridden with the
    second param of the function set to False.
    :param csv_path: Relative or absolute path to a csv or tsv file
    :param validation: Check ID structure of first column, defaults to False
    :return: Generator of csv/tsv file lines as dictionaries
    """
    logger.info(f"Reading file {csv_path} into generator.")

    if not check_file_path(csv_path):
        logger.error("No valid file path provided.")
        raise ValueError

    if csv_path[-4:] in [".csv", ".CSV"]:
        delimit = ";"
    elif csv_path[-4:] in [".tsv", ".TSV"]:
        delimit = "\t"
    else:
        logger.error(f"Extension of the given file not expected (csv for"
                     f" semicolon, tsv for tabs).")
        raise ValueError

    with open(csv_path, newline="") as csv_file:

        csv_reader = DictReader(csv_file, delimiter=delimit)

        for row in csv_reader:

            first_column_value = list(row.values())[0]

            if all(is_this_an_alma_id(string)
                   for string in str.split(first_column_value, ",")) \
                   or not validation:
                yield row
            else:
                logger.warning(f"The following row was discarded: {row}")


def check_file_path(file_path: str) -> bool:
    """
    Checks file path for existence, readability and whether the file is
    ending on either .csv or .tsv
    :param file_path: Absolute or relative path to the csv/tsv file
    :return: Boolean for file exists, is readable and ends on .csv or .tsv
    """

    if path.exists(file_path) \
            and access(file_path, R_OK) \
            and file_path[-4:] in [".csv", ".tsv", ".CSV", ".TSV"]:
        return True

    logger.error(f"File {file_path} does not exist, is not readable, or does"
                 f"not end on csv, tsv, CSV or TSV.")


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

        alma_id_suffix = environ["ALMA_REST_ID_INSTITUTIONAL_SUFFIX"]

    except KeyError:

        warnings.warn("Env var 'ALMA_REST_ID_INSTITUTIONAL_SUFFIX' not set.")

    else:

        pattern = ALMA_ID_PATTERN.format(alma_id_suffix=alma_id_suffix)

        if re.fullmatch(pattern, identifier):
            return True

        logger.warning(f"Identifier is not a valid Alma ID: '{identifier}'")
        return False
