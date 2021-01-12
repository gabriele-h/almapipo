"""
Query the Alma API for users.
See https://developers.exlibrisgroup.com/console/?url=/wp-content/uploads/alma/openapi/users.json
"""

from logging import getLogger

from . import rest_setup

# Logfile
logger = getLogger(__name__)


class UsersApi(rest_setup.GenericApi):
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

    def retrieve_all_fees(self, user_id: str) -> str:
        """
        For a given user_id retrieve all fines and fees.
        :param user_id: Any unique ID of the user
        :return: Record in XML format as a string
        """

        logger.info(f'Trying to fetch all fees for user_id {user_id}.')

        all_fees = self.retrieve(f'{user_id}/fees')

        return all_fees
