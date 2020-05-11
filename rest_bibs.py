"""Query the Alma API for a single BIB record
"""

from logging import getLogger
from urllib import parse

import rest_call_api
# noinspection PyUnresolvedReferences
import logfile_setup

# Logfile
logger = getLogger(__name__)


#
# GET
#


def get_bib(mms_id: str):
    """
    Get BIB record by MMS-ID via Alma API.
    :param mms_id: Unique ID of Alma BIB records.
    :return: Record data in JSON format.
    """
    logger.info(f'Trying to fetch BIB with mms_id {mms_id}.')
    bib_record = rest_call_api.get_record(f'/bibs/{mms_id}')
    return bib_record


def get_hol(mms_id: str, hol_id: str):
    """
    Get HOL record via Alma API with MMS-ID and HOL-id.
    :param mms_id: Unique ID of the BIB record the HOL is connected to.
    :param hol_id: ID of the HOL record.
    :return: Record data in JSON format.
    """
    logger.info(f'Trying to fetch HOL with mms_id {mms_id} and hol_id {hol_id}.')
    hol_record = rest_call_api.get_record(f'/bibs/{mms_id}/holdings/{hol_id}')
    return hol_record


def get_item(mms_id: str, hol_id: str, itm_id: str):
    """
    Get Item record via Alma API with MMS-ID, HOL-id and ITM-ID.
    :param mms_id: Unique ID of the BIB record the HOL is connected to.
    :param hol_id: ID of the HOL record the ITM is connected to.
    :param itm_id: ID of the ITM record.
    :return: Record data in JSON format.
    """
    logger.info(f'Trying to fetch ITM with mms_id {mms_id} and hol_id {hol_id} and itm_id {itm_id}.')
    itm_record = rest_call_api.get_record(f'/bibs/{mms_id}/holdings/{hol_id}/items/{itm_id}')
    return itm_record


def get_portfolio(mms_id: str, portfolio_id: str):
    """
    Get Portfolio record via Alma API with MMS-ID and portfolio-ID.
    :param mms_id: Unique ID of the BIB record the HOL is connected to.
    :param portfolio_id: ID of the portfolio record.
    :return: Record data in JSON format.
    """
    logger.info(f'Trying to fetch Portfolio record with mms_id {mms_id} and portfolio_id {portfolio_id}.')
    portfolio_record = rest_call_api.get_record(f'/bibs/{mms_id}/portfolios/{portfolio_id}')
    return portfolio_record


def get_single_bib_by_query(id_type: str, other_id: str):
    """
    Get single record by ID via Alma API. Possible ID types:
    * mms_id
    * ie_id
    * holdings_id
    * representation_id
    * nz_mms_id
    * cz_mms_id
    * other_system_id
    :param id_type: Query key. One of the ID types listed above.
    :param other_id: Query value. ID of the record to be fetched.
    :return: List of records in JSON format.
    """
    logger.info(f'Trying to fetch record by query with other_id {other_id}.')
    api_url_path = '/bibs?'
    api_url_query = {id_type: other_id}
    api_url_query_encoded = parse.urlencode(api_url_query)
    api_url = api_url_path + api_url_query_encoded
    bib_record = rest_call_api.get_record(api_url)
    return bib_record


#
# POST
#


# post_bib
# post_bib_from_nz
# post_bib_from_cz
# post_hol
# post_item
# post_portfolio


#
# PUT
#


# put_bib
# put_hol
# put_item
# put_portfolio


#
# DELETE
#


# delete_bib
# delete_hol
# delete_item
# delete_portfolio
