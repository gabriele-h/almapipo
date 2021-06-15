"""
Count occurrences for combinations of MARC content designators.
"""

from logging import getLogger
from typing import Iterable


# Logfile
logger = getLogger('marc_to_tsv')


def count_for_tag_and_inds(all_records: Iterable[dict], designators: Iterable[str]) -> dict:
    """
    For a list of records as returned by almapipo.xml_extract.extract_marc_for_job_timestamp
    create a dictionary with counters for the given content designators.
    :param all_records: Generator of all records given as dictionaries
    :param designators: List of tags with indicators concatenated into one string, e. g. '035  '
    :return: Dict of all field- and subfield-keys within a set of MARC21 records with overall maximum of repetitions
    """

    num_repetition = {}

    for record_dict in all_records:

        for designator in designators:

            if designator not in num_repetition.keys():

                try:
                    record_dict[designator]
                except KeyError:
                    logger.debug(f"Field '{designator}' not found in record {record_dict['001'][0]} (MARC 001)")
                else:
                    try:
                        # will the below ever not fail?
                        num_repetition[designator]
                    except KeyError:
                        num_repetition[designator] = len(record_dict[designator])
                    else:
                        if num_repetition[designator] < len(record_dict[designator]):
                            num_repetition[designator] = len(record_dict[designator])

            # only datafields (tag >= 010) have subfields and indicators
            if designator[0:2] != '00' and designator != 'leader':
                pass

    return num_repetition
