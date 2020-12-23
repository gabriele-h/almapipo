"""
Extracts XML from the database and offers helper functions for further
handling of the record.
"""

from datetime import datetime
from logging import getLogger
from typing import Iterable
from xml.etree import ElementTree
from xml.etree.ElementTree import Element

from . import db_read_write

# Logfile
logger = getLogger(__name__)


def extract_response_from_fetched_records(alma_id: str) -> ElementTree:
    """
    From the table fetched_records extract the whole response for the record. Only most recent version supported.
    :param alma_id: Comma separated string of Alma IDs to identify the record.
    :return: ElementTree of the record.
    """
    logger.info(f'Extracting most recent response for alma_id {alma_id} from table fetched_records.')
    response_query = db_read_write.get_most_recent_version_from_fetched_records(alma_id)
    response = response_query.alma_record
    return response


def extract_marc_for_job_timestamp(job_timestamp: datetime) -> Iterable[dict]:
    """
    For a given job_timestamp, query all records from the database and extract
    the MARC21 categories to a dictionary. Please mind that this is a one-way
    action as not all information (specifically: order of categories and subfields)
    will be pertained. This function is meant for the kind of analysis where you
    need to compare the content of two specific fields. All analyses that need to
    be order-aware should be done via xpath directly in the database. Use the
    script marc_to_tsv.py to look at the data in Excel.
    :param job_timestamp: Job to extract the data for
    :return: Generator of dictionaries
    """
    logger.info(f'Getting bibs retrieved on {job_timestamp} from the database.')
    db_record_generator = db_read_write.get_records_by_timestamp(job_timestamp)

    for db_record in db_record_generator:
        marc_dict = extract_contents_from_marc(db_record.find('record'))
        yield marc_dict


def extract_contents_from_marc(record: Element) -> dict:
    """
    For a given record-element extract the information as per column_headers list.
    The latter may be generated automatically for a list of records
    with the create_list_of_marc_fields function. NOTE: This is a one-way action.
    Information on order of categories and subfields is lost in the dictionary. The
    data returned by this function is *not* intended to be converted back to XML!
    :param record: MARC21 record as xml.ElementTree.Element
    :return: Dictionary representation of the record.
    """
    marc21_dict = {'leader': record.find('leader').text}

    for controlfield in record.findall('controlfield'):
        tag = controlfield.attrib['tag']
        text = controlfield.text
        append_multiple_to_dict(marc21_dict, tag, text)

    for datafield in record.findall('datafield'):
        tag_with_inds = f"""{datafield.attrib['tag']}{datafield.attrib['ind1']}{datafield.attrib['ind2']}"""
        datafield_dict = extract_subfields_from_datafield(datafield)
        append_multiple_to_dict(marc21_dict, tag_with_inds, datafield_dict)

    return marc21_dict


def extract_subfields_as_string(datafield: Element) -> str:
    """
    For a given datafield element extract a string of
    its subfields, each is prepended with '$$' and the subfield's code
    (e. g. $$ager' for subfield a with content 'ger')
    :param datafield:
    :return: Dictionary with subfield-code as key and subfield-text as value.
    """
    def gen_subfield(datafield):
        for subfield in datafield.findall('subfield'):
            code = subfield.attrib['code']
            text = subfield.text
            yield '$$' + code + text

    return ''.join(list(gen_subfield(datafield)))


def append_multiple_to_dict(dictionary: dict, key: str, value) -> dict:
    """
    For a given dictionary see if the key already exists and if
    it does, append the value to the list of values.
    :param dictionary: Dictionary to add the value to
    :param key: Potentially repeated key to check
    :param value: Value to add new key or append if key exists
    :return: Manipulated dictionary
    """
    try:
        dictionary[key]
    except KeyError:
        dictionary.update({key: [value]})
    else:
        new_values = dictionary[key] + [value]
        dictionary[key] = new_values

    return dictionary
