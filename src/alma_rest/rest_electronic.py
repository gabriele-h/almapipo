"""
Query the Alma API for electronic resources
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


def retrieve_e_collection(collection_id: str) -> str:
    """
    Get e-collection by collection-id only.
    :param collection_id: ID of the electronic collection.
    :return: String of the API response.
    """
    logger.info(f'Trying to fetch collection with collection_id {collection_id}.')
    collection_record = rest_call_api.get_record(f'/electronic/e-collections/{collection_id}')
    return collection_record


def update_e_collection(record_data: bytes, collection_id: str) -> str:
    """
    Update-collection by collection-id only.
    :param record_data: XML to be sent via PUT via API.
    :param collection_id: ID of the electronic collection.
    :return: String of the API response.
    """
    logger.info(f'Trying to update collection with collection_id {collection_id}.')
    update_response = rest_call_api.update_record(record_data, f'/electronic/e-collections/{collection_id}')
    return update_response
