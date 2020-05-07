"""Query the Alma API for a single BIB record
"""

from logging import getLogger

import rest_create_session
# noinspection PyUnresolvedReferences
import logfile_setup

# Logfile
logger = getLogger(__name__)


def get_bib_by_mms_id(mms_id: str):
    """
    Get BIB record via Alma API.
    :param mms_id: Unique ID of Alma BIB records.
    :return: Record data in JSON format.
    """
    logger.info(f'Trying to fetch BIB with mms_id {mms_id}.')
    alma_record = rest_create_session.make_api_call(f'/bibs/{mms_id}')
    return alma_record
