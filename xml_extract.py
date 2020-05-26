"""
Extracts XML from the database and offers helper functions for further
handling of the record.
"""

import json
from logging import getLogger
from xml.etree.ElementTree import fromstring, Element

import db_read_write
import db_setup
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
    logger.info(f'Converting string of XML for {alma_ids} to xml.etree Element.')
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
    logger.info(f'Extracting XML from response for {alma_ids} as string.')
    # SQLite will return str, Postgres dict
    response = extract_response_from_fetched_records(alma_ids)
    if db_setup.db_dialect == "sqlite":
        try:
            response_as_json = json.loads(response_as_string)
        except TypeError:
            logger.error('Data type not valid to load as JSON object.')
        else:
            xml_string = response_as_json['anies'][0]
    else:
        xml_string = response['anies'][0]
    return xml_string


def extract_response_from_fetched_records(alma_ids: str) -> str:
    """
    From the table fetched_records extract the whole response for the record
    and convert it from byte-array to string.
    :param alma_ids: Comma separated string of Alma IDs to identify the record.
    :return: String of the record's XML.
    """
    logger.info(f'Extracting most recent response for alma_ids {alma_ids} from table fetched_records.')
    response_query = db_read_write.get_record_from_fetched_records(alma_ids)
    response = response_query.alma_record
    return response
