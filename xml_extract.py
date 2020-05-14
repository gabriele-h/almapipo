"""
Extracts XML from the database and offers helper functions for further
handling of the record.
"""

import json
from logging import getLogger
from xml.etree.ElementTree import fromstring, Element

import db_read_write
# noinspection PyUnresolvedReferences
import logfile_setup

# Logfile
logger = getLogger(__name__)


def extract_xml_record_element_from_fetched_records(alma_ids: str) -> Element:
    """
    From table fetched_records extract the XML of the record and
    return it as an xml.etree Element.
    :param alma_ids: Comma separated string of Alma IDs to identify the record.
    :return: Element of the record's XML.
    """
    xml_as_string = extract_xml_from_fetched_records(alma_ids)
    xml_as_element = fromstring(xml_as_string)
    return xml_as_element


def extract_xml_from_fetched_records(alma_ids: str) -> str:
    """
    From the table fetched_records extract the XML of the record and
    return it as a string.
    :param alma_ids: Comma separated string of Alma IDs to identify the record.
    :return: String of the record's XML.
    """
    logger.info(f'Extracting most recent record with alma_ids {alma_ids} from table fetched_records.')
    record_query = db_read_write.get_record_from_fetched_records(alma_ids)
    record_as_bytes = record_query.alma_record
    record_as_string = str(record_as_bytes, 'utf-8')
    try:
        record_as_json = json.loads(record_as_string)
    except TypeError:
        logger.error('Data type not valid to load as JSON object.')
    else:
        xml_string = record_as_json['anies'][0]
        return xml_string
