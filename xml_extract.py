"""
Extracts XML from the database and offers helper functions for further
handling of the record.
"""

import json
from logging import getLogger
from xml.etree import ElementTree

import db_read_write
import db_setup
# noinspection PyUnresolvedReferences
import logfile_setup

# Logfile
logger = getLogger(__name__)


def extract_record_from_fetched_records(alma_ids: str) -> ElementTree.Element:
    """
    From table fetched_records extract the XML of the record and
    return it as an xml.etree Element.
    :param alma_ids: Comma separated string of Alma IDs to identify the record.
    :return: Element of the record's XML.
    """
    logger.info(f'Searching for record within XML response for {alma_ids}.')
    response_xml = extract_response_from_fetched_records(alma_ids)
    record_as_etree = response_xml.findall('record')
    return record_as_etree


def extract_response_as_bytes_from_fetched_records(alma_ids: str) -> bytes:
    """
    From the table fetched_records extract the whole response for the record
    and convert the ElementTree to bytes.
    :param alma_ids: Comma separated string of Alma IDs to identify the record.
    :return: bytes of the record's GET response content
    """
    logger.info(f'Converting XML response for {alma_ids} to bytes.')
    response_xml = extract_response_from_fetched_records(alma_ids)
    record_as_bytes = ElementTree.tostring(response_xml)
    return record_as_bytes


def extract_response_from_fetched_records(alma_ids: str) -> ElementTree:
    """
    From the table fetched_records extract the whole response for the record
    and convert it from byte-array to string.
    :param alma_ids: Comma separated string of Alma IDs to identify the record.
    :return: ElementTree of the GET response in XML format for the record.
    """
    logger.info(f'Extracting most recent response for alma_ids {alma_ids} from table fetched_records.')
    response_query = db_read_write.get_record_from_fetched_records(alma_ids)
    response = response_query.alma_record
    return response
