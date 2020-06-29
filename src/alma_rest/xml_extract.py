"""
Extracts XML from the database and offers helper functions for further
handling of the record.
"""

from logging import getLogger
from xml.etree import ElementTree

import db_read_write
# noinspection PyUnresolvedReferences
import logfile_setup

# Logfile
logger = getLogger(__name__)


def extract_response_from_fetched_records(alma_ids: str) -> ElementTree:
    """
    From the table fetched_records extract the whole response for the record.
    :param alma_ids: Comma separated string of Alma IDs to identify the record.
    :return: ElementTree of the record.
    """
    logger.info(f'Extracting most recent response for alma_ids {alma_ids} from table fetched_records.')
    response_query = db_read_write.get_record_from_fetched_records(alma_ids)
    response = response_query.alma_record
    return response
