"""
Extracts XML from the database and offers helper functions for further
handling of the record.
"""

from logging import getLogger
from xml.etree import ElementTree

from . import db_read_write
# noinspection PyUnresolvedReferences
from . import logfile_setup

# Logfile
logger = getLogger(__name__)


def extract_response_from_fetched_records(alma_id: str) -> ElementTree:
    """
    From the table fetched_records extract the whole response for the record.
    :param alma_id: Comma separated string of Alma IDs to identify the record.
    :return: ElementTree of the record.
    """
    logger.info(f'Extracting most recent response for alma_id {alma_id} from table fetched_records.')
    response_query = db_read_write.get_most_recent_version_from_fetched_records(alma_id)
    response = response_query.alma_record
    return response
