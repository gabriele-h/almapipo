"""
Query the Alma API for bibs records
"""

from logging import getLogger
from urllib import parse

from . import rest_call_api
# noinspection PyUnresolvedReferences
from . import logfile_setup

# Logfile
logger = getLogger(__name__)


#######
# GET #
#######


def get_bib(mms_id: str) -> str:
    """
    Get BIB record by MMS-ID via Alma API.
    :param mms_id: Unique ID of Alma BIB records.
    :return: Record data in XML format.
    """
    logger.info(f'Trying to fetch BIB with mms_id {mms_id}.')
    bib_record = rest_call_api.get_record(f'/bibs/{mms_id}')
    return bib_record


def get_hol(mms_id: str, hol_id: str) -> str:
    """
    Get HOL record via Alma API by MMS-ID and HOL-id.
    :param mms_id: Unique ID of the BIB record the HOL is connected to.
    :param hol_id: ID of the HOL record.
    :return: Record data in XML format.
    """
    logger.info(f'Trying to fetch HOL with mms_id {mms_id} and hol_id {hol_id}.')
    hol_record = rest_call_api.get_record(f'/bibs/{mms_id}/holdings/{hol_id}')
    return hol_record


def get_item(mms_id: str, hol_id: str, itm_id: str) -> str:
    """
    Get Item record via Alma API by MMS-ID, HOL-id and ITM-ID.
    :param mms_id: Unique ID of the BIB record the HOL is connected to.
    :param hol_id: ID of the HOL record the ITM is connected to.
    :param itm_id: ID of the ITM record.
    :return: Record data in XML format.
    """
    logger.info(f'Trying to fetch ITM with mms_id {mms_id} and hol_id {hol_id} and itm_id {itm_id}.')
    itm_record = rest_call_api.get_record(f'/bibs/{mms_id}/holdings/{hol_id}/items/{itm_id}')
    return itm_record


def get_portfolio(mms_id: str, portfolio_id: str) -> str:
    """
    Get portfolio record via Alma API by MMS-ID and portfolio-ID.
    :param mms_id: Unique ID of the BIB record the portfolio is connected to.
    :param portfolio_id: ID of the portfolio record.
    :return: Record data in XML format.
    """
    logger.info(f'Trying to fetch portfolio record with mms_id {mms_id} and portfolio_id {portfolio_id}.')
    portfolio_record = rest_call_api.get_record(f'/bibs/{mms_id}/portfolios/{portfolio_id}')
    return portfolio_record


def get_e_collection_with_mms_id(mms_id: str, collection_id: str) -> str:
    """
    Get e-collection record for id combination mms-ID and collection-ID.
    :param mms_id: Unique ID of the BIB record the collection is connected to.
    :param collection_id: ID of the e-collection.
    :return: Record in XML format.
    """
    logger.info(f'Trying to fetch e-collection record with mms_id {mms_id} and collection_id {collection_id}.')
    collection_record = rest_call_api.get_record(f'/bibs/{mms_id}/e-collections/{collection_id}')
    return collection_record


def get_all_items_for_bib(mms_id: str) -> str:
    """
    For a given mms_id, get all holding and item information.
    :param mms_id: Unique ID of the BIB record the holdings and items are connected to.
    :return: Record in XML format.
    """
    logger.info(f'Trying to fetch all holdings and items information for bib record {mms_id}')
    physical_inventory_record = rest_call_api.get_record(f'/bibs/{mms_id}/holdings/ALL/items')
    return physical_inventory_record


def get_all_e_collections_for_bib(mms_id: str) -> str:
    """
    For a given mms_id, get all e-collection information.
    :param mms_id: Unique ID of the BIB record the e-collections are connected to.
    :return: Record in XML format.
    """
    logger.info(f'Trying to fetch all e-collections for bib record {mms_id}.')
    e_inventory_record = rest_call_api.get_record(f'/bibs/{mms_id}/e-collections/')
    return e_inventory_record


def get_item_by_barcode(item_barcode: str) -> str:
    """
    Get item information by barcode.
    :param item_barcode: Barcode of the item.
    :return: Record in XML format.
    """
    logger.info(f'Trying to fetch item by barcode {item_barcode}.')
    api_url_query = {"item_barcode": item_barcode}
    api_url_query_encoded = parse.urlencode(api_url_query)
    item_record = rest_call_api.get_record(f'/items?{api_url_query_encoded}')
    return item_record


def get_bibs_by_query(id_type: str, other_id: str) -> str:
    """
    Get records by ID via Alma API. Possible ID types:
    * mms_id
    * ie_id
    * holdings_id
    * representation_id
    * nz_mms_id
    * cz_mms_id
    * other_system_id
    :param id_type: Query key. One of the ID types listed above.
    :param other_id: Query value. ID of the record to be fetched.
    :return: Record in XML format.
    """
    logger.info(f'Trying to fetch record by query with id_type {id_type} and other_id {other_id}.')
    api_url_path = '/bibs?'
    api_url_query = {id_type: other_id}
    api_url_query_encoded = parse.urlencode(api_url_query)
    api_url = api_url_path + api_url_query_encoded
    bib_records_response = rest_call_api.get_record(api_url)
    return bib_records_response


########
# POST #
########


def create_bib(record_data: bytes, mms_id: str) -> str:
    """
    Create BIB record by MMS-ID via Alma API.
    :param record_data: XML of the record to be created.
    :param mms_id: Unique ID of Alma BIB records.
    :return: Response data in XML format.
    """
    logger.info(f'Trying to create BIB with mms_id {mms_id}.')
    bib_record = rest_call_api.create_record(record_data, f'/bibs/')
    return bib_record


def create_hol(record_data: bytes, mms_id: str, hol_id: str) -> str:
    """
    Create HOL record via Alma API by MMS-ID and HOL-id.
    :param record_data: XML of the record to be created.
    :param mms_id: Unique ID of the BIB record the HOL is connected to.
    :param hol_id: ID of the HOL record.
    :return: Response data in XML format.
    """
    logger.info(f'Trying to create HOL with mms_id {mms_id} and hol_id {hol_id}.')
    hol_record = rest_call_api.create_record(record_data, f'/bibs/{mms_id}/holdings/')
    return hol_record


def create_item(record_data: bytes, mms_id: str, hol_id: str, itm_id: str) -> str:
    """
    Create Item record via Alma API by MMS-ID, HOL-id and ITM-ID.
    :param record_data: XML of the record to be created.
    :param mms_id: Unique ID of the BIB record the HOL is connected to.
    :param hol_id: ID of the HOL record the ITM is connected to.
    :param itm_id: ID of the ITM record.
    :return: Response data in XML format.
    """
    logger.info(f'Trying to create ITM with mms_id {mms_id} and hol_id {hol_id} and itm_id {itm_id}.')
    itm_record = rest_call_api.create_record(record_data, f'/bibs/{mms_id}/holdings/{hol_id}/items/')
    return itm_record


def create_portfolio(record_data: bytes, mms_id: str, portfolio_id: str) -> str:
    """
    Create portfolio record via Alma API by MMS-ID and portfolio-ID.
    :param record_data: XML of the record to be created.
    :param mms_id: Unique ID of the BIB record the portfolio is connected to.
    :param portfolio_id: ID of the portfolio record.
    :return: Response data in XML format.
    """
    logger.info(f'Trying to create portfolio record with mms_id {mms_id} and portfolio_id {portfolio_id}.')
    portfolio_record = rest_call_api.create_record(record_data, f'/bibs/{mms_id}/portfolios/')
    return portfolio_record


#######
# PUT #
#######


def update_bib(record_data: bytes, mms_id: str) -> str:
    """
    Update BIB record via Alma API by MMS-ID.
    :param record_data: XML of the record to be updated.
    :param mms_id: Unique ID of the BIB record.
    :return: Response data in XML format.
    """
    logger.info(f'Trying to update BIB with mms_id {mms_id}.')
    bib_record = rest_call_api.update_record(record_data, f'/bibs/{mms_id}')
    return bib_record


def update_hol(record_data: bytes, mms_id: str, hol_id: str) -> str:
    """
    Update HOL record via Alma API by MMS-ID and HOL-ID.
    :param record_data: XML of the record to be updated.
    :param mms_id: Unique ID of the BIB record the HOL is connected to.
    :param hol_id: ID of the HOL record.
    :return: Response data in XML format.
    """
    logger.info(f'Trying to update HOL with mms_id {mms_id} and hol_id {hol_id}.')
    hol_record = rest_call_api.update_record(record_data, f'/bibs/{mms_id}/holdings/{hol_id}')
    return hol_record


def update_item(record_data: bytes, mms_id: str, hol_id: str, itm_id: str) -> str:
    """
    Update ITM record via Alma API by MMS-ID, HOL-ID and ITM-ID.
    :param record_data: XML of the record to be updated.
    :param mms_id: Unique ID of the BIB record the HOL is connected to.
    :param hol_id: ID of the HOL record the ITM is connected to.
    :param itm_id: ID of the ITM record.
    :return: Response data in XML format.
    """
    logger.info(f'Trying to update ITM with mms_id {mms_id}, hol_id {hol_id}, and itm_id {itm_id}.')
    itm_record = rest_call_api.update_record(record_data, f'/bibs/{mms_id}/holdings/{hol_id}/items/{itm_id}')
    return itm_record


def update_portfolio(record_data: bytes, mms_id: str, portfolio_id: str) -> str:
    """
    Update portfolio record via Alma API by MMS-ID and portfolio-ID.
    :param record_data: XML of the record to be updated.
    :param mms_id: Unique ID of the BIB record the portfolio is connected to.
    :param portfolio_id: ID of the portfolio.
    :return: Response data in XML format.
    """
    logger.info(f'Trying to update portfolio with mms_id {mms_id} and portfolio-id {portfolio_id}.')
    portfolio_record = rest_call_api.update_record(record_data, f'/bibs/{mms_id}/portfolios/{portfolio_id}.')
    return portfolio_record


##########
# DELETE #
##########


def delete_bib(mms_id: str) -> str:
    """
    Delete BIB record by MMS-ID via Alma API.
    :param mms_id: Unique ID of Alma BIB records.
    :return: API response
    """
    logger.info(f'Trying to DELETE BIB with mms_id {mms_id}.')
    delete_response = rest_call_api.delete_record(f'/bibs/{mms_id}')
    return delete_response


def delete_hol(mms_id: str, hol_id: str) -> str:
    """
    Delete HOL record via Alma API by MMS-ID and HOL-id.
    :param mms_id: Unique ID of the BIB record the HOL is connected to.
    :param hol_id: ID of the HOL record.
    :return: API response
    """
    logger.info(f'Trying to DELETE HOL with mms_id {mms_id} and hol_id {hol_id}.')
    delete_response = rest_call_api.delete_record(f'/bibs/{mms_id}/holdings/{hol_id}')
    return delete_response


def delete_item(mms_id: str, hol_id: str, itm_id: str) -> str:
    """
    Delete Item record via Alma API by MMS-ID, HOL-id and ITM-ID.
    :param mms_id: Unique ID of the BIB record the HOL is connected to.
    :param hol_id: ID of the HOL record the ITM is connected to.
    :param itm_id: ID of the ITM record.
    :return: API response
    """
    logger.info(f'Trying to DELETE ITM with mms_id {mms_id} and hol_id {hol_id} and itm_id {itm_id}.')
    delete_response = rest_call_api.delete_record(f'/bibs/{mms_id}/holdings/{hol_id}/items/{itm_id}')
    return delete_response


def delete_portfolio(mms_id: str, portfolio_id: str) -> str:
    """
    Delete portfolio record via Alma API by MMS-ID and portfolio-ID.
    :param mms_id: Unique ID of the BIB record the portfolio is connected to.
    :param portfolio_id: ID of the portfolio record.
    :return: API response
    """
    logger.info(f'Trying to DELETE portfolio record with mms_id {mms_id} and portfolio_id {portfolio_id}.')
    delete_response = rest_call_api.delete_record(f'/bibs/{mms_id}/portfolios/{portfolio_id}')
    return delete_response
