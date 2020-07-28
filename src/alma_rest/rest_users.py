"""
Query the Alma API for users
"""

from logging import getLogger

from . import rest_call_api
# noinspection PyUnresolvedReferences
from . import logfile_setup

# Logfile
logger = getLogger(__name__)


#######
# GET #
#######


def retrieve_user(user_id: str) -> str:
    """
    Get user record by user-ID via Alma API.
    :param user_id: Unique ID of Alma user record.
    :return: Record data in XML format.
    """
    logger.info(f'Trying to fetch user with user_id {user_id}.')
    user_record = rest_call_api.get_record(f'/users/{user_id}')
    return user_record
