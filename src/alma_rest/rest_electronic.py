"""
Query the Alma API for electronic resources
"""

from logging import getLogger

from alma_rest import rest_call_api
# noinspection PyUnresolvedReferences
from alma_rest import logfile_setup

# Logfile
logger = getLogger(__name__)


#######
# GET #
#######


def get_e_collection(collection_id: str) -> str:
    """
    Get e-collection by collection-id only.
    :param collection_id: ID of the electronic collection.
    :return: String of the API response.
    """
    logger.info(f'Trying to fetch collection with collection_id {collection_id}.')
    collection_record = rest_call_api.get_record(f'/electronic/e-collections/{collection_id}')
    return collection_record
