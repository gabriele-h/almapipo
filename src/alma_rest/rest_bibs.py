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


class BibsApiCallerForBibs(rest_call_api.ApiCaller):
    """
    Make calls for bibliographic records. Here the record_id is the MMS ID.
    """
    def __init__(self):
        """
        Initialize API calls for bibliographic records.
        """

        base_path = '/bibs/'

        logger.info(f'Instantiating {type(self).__name__}.')

        super().__init__(base_path)

    def get_all_holdings(self, mms_id: str) -> str:
        """
        For a given mms_id, get all holdings information.
        :param mms_id: Unique ID of the BIB record the holdings are connected to.
        :return: Record in XML format.
        """
        logger.info(f'Trying to fetch all holdings information for bib record {mms_id}.')
        record = rest_call_api.get_record(f'{self.base_path}{mms_id}/holdings')
        return record

    def get_all_items(self, mms_id: str) -> str:
        """
        For a given mms_id, get all holding and item information.
        :param mms_id: Unique ID of the BIB record the holdings and items are connected to.
        :return: Record in XML format.
        """
        logger.info(f'Trying to fetch all holdings and items information for bib record {mms_id}.')
        physical_inventory_record = rest_call_api.get_record(f'{self.base_path}{mms_id}/holdings/ALL/items')
        return physical_inventory_record

    def get_all_portfolios(self, mms_id: str) -> str:
        """
        For a given mms_id, get all portfolios.
        param: mms_id: Unique ID of the BIB record the portfolios are connected to.
        :return: Record in XML format.
        """
        logger.info(f'Trying to fetch all portfolios for bib record {mms_id}.')
        e_inventory_record = rest_call_api.get_record(f'{self.base_path}{mms_id}/portfolios/')
        return e_inventory_record

    def get_all_e_collections(self, mms_id: str) -> str:
        """
        For a given mms_id, get all e-collection information.
        :param mms_id: Unique ID of the BIB record the e-collections are connected to.
        :return: Record in XML format.
        """
        logger.info(f'Trying to fetch all e-collections for bib record {mms_id}.')
        e_inventory_record = rest_call_api.get_record(f'{self.base_path}{mms_id}/e-collections/')
        return e_inventory_record

    def get_by_query(self, id_type: str, other_id: str) -> str:
        """
        Get bibliographic records by ID via Alma API. Possible ID types:
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
        api_url_query = {id_type: other_id}
        api_url_query_encoded = parse.urlencode(api_url_query)
        api_url = self.base_path + '?' + api_url_query_encoded
        bib_records_response = rest_call_api.get_record(api_url)
        return bib_records_response


class BibsApiCallerForHoldings(rest_call_api.ApiCaller):
    """
    Make calls for holding records. Here the record_id is the Holding PID.
    """
    def __init__(self, mms_id: str):
        """
        Initialize API calls for holding records connected to a bibliographic record.
        :param mms_id: MMS ID of the bibliographic record the holding is connected to.
        """
        self.mms_id = mms_id

        base_path = f'/bibs/{self.mms_id}/holdings/'

        logger.info(f'Instantiating {type(self).__name__} with mms_id {self.mms_id}.')

        super().__init__(base_path)

    def get_all_items(self, hol_id: str) -> str:
        """
        For a given mms_id, get all holding and item information.
        :param hol_id: ID of the HOL record the ITMs are connected to.
        :return: Record in XML format.
        """
        logger.info(f'Trying to fetch all items information for hol_id {hol_id}.')
        physical_inventory_record = rest_call_api.get_record(f'{self.base_path}{hol_id}/items')
        return physical_inventory_record


class BibsApiCallerForItems(rest_call_api.ApiCaller):
    """
    Make calls for item records. Here the record_id is the Item PID.
    """
    def __init__(self, mms_id: str, hol_id: str):
        """
        Initialize API calls for holding records connected to a bibliographic record.
        :param mms_id: MMS ID of the bibliographic record the item's holding record is connected to.
        :param hol_id: Holding PID of the holding the item is connected to.
        """
        self.mms_id = mms_id
        self.hol_id = hol_id

        base_path = f'/bibs/{self.mms_id}/holdings/{self.hol_id}/items/'

        logger.info(f'Instantiating {type(self).__name__} with mms_id {self.mms_id} and hol_id {self.hol_id}.')

        super().__init__(base_path)


class BibsApiCallerForPortfolios(rest_call_api.ApiCaller):
    """
    Make calls for portfolio records. Here the record_id is the Portfolio PID.
    """
    def __init__(self, mms_id: str):
        """
        Initialize API calls for holding records connected to a bibliographic record.
        :param mms_id: MMS ID of the bibliographic record the portfolio is connected to.
        :param portfolio_id: ID of the portfolio record.
        """
        self.mms_id = mms_id
        self.portfolio_id = portfolio_id

        base_path = f'/bibs/{self.mms_id}/portfolios/'

        log_string = f"""Instantiating {type(self).__name__} with mms_id {self.mms_id} """
        log_string += f"""and portfolio_id {self.portfolio_id}."""
        logger.info(log_string)

        super().__init__(base_path)


# TODO Extraneous functions not yet refactored to meet OOP style


def get_e_collection_with_mms_id(mms_id: str, collection_id: str) -> str:
    """
    Get e-collection record for id combination mms-ID and collection-ID.
    :param mms_id: Unique ID of the BIB record the collection is connected to.
    :param collection_id: ID of the e-collection.
    :return: Record in XML format.
    """
    logger.info(f'Trying to fetch e-collection record with mms_id {mms_id} and collection_id {collection_id}.')
    collection_record = rest_call_api.call_api(f'/bibs/{mms_id}/e-collections/{collection_id}', 'GET', 200)
    return collection_record


def get_item_by_barcode(item_barcode: str) -> str:
    """
    Get item information by barcode. Please note that this equals a scan-in operation!
    :param item_barcode: Barcode of the item.
    :return: Record in XML format.
    """
    logger.info(f'Trying to fetch item by barcode {item_barcode}.')
    api_url_query = {"item_barcode": item_barcode}
    api_url_query_encoded = parse.urlencode(api_url_query)
    item_record = rest_call_api.call_api(f'/items?{api_url_query_encoded}', 'GET', 200)
    return item_record
