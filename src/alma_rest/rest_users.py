"""
Query the Alma API for users.
See https://developers.exlibrisgroup.com/console/?url=/wp-content/uploads/alma/openapi/users.json
"""

from logging import getLogger

from . import rest_call_api
# noinspection PyUnresolvedReferences
from . import logfile_setup

# Logfile
logger = getLogger(__name__)


class UsersApi(rest_call_api.GenericApi):
    """
    Make calls for bibliographic records. Here the record_id is the MMS ID.
    """
    def __init__(self):
        """
        Initialize API calls for bibliographic records.
        """
        base_path = '/users/'

        logger.info(f'Instantiating {type(self).__name__}.')

        super().__init__(base_path)
