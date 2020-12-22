"""
Query the Alma API for bibs records.
See https://developers.exlibrisgroup.com/console/?url=/wp-content/uploads/alma/openapi/bibs.json
"""

from logging import getLogger
from urllib import parse

from . import rest_setup

# Logfile
logger = getLogger(__name__)


class BibsApi(rest_setup.GenericApi):
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

    def retrieve_bib_by_query(self, url_parameters: dict) -> str:
        """
        Make a query to the bibs API with url_parameters only.
        E. g. {'other_system_id': 'AC08455773'}
        :param url_parameters: Python dictionary of parameters.
        :return: Search result in XML format.
        """
        logger.info(f'Trying to fetch bibs records with parameters {url_parameters}.')
        search_result = self.retrieve('', url_parameters)
        return search_result

    def retrieve_all_holdings(self, mms_id: str) -> str:
        """
        For a given mms_id, get all holdings information.
        :param mms_id: Unique ID of the BIB record the holdings are connected to.
        :return: Record in XML format.
        """
        logger.info(f'Trying to fetch all holdings information for bib record {mms_id}.')
        record = self.retrieve(f'{mms_id}/holdings')
        return record

    def retrieve_all_items(self, mms_id: str) -> str:
        """
        For a given mms_id, get all holding and item information.
        :param mms_id: Unique ID of the BIB record the holdings and items are connected to.
        :return: Record in XML format.
        """
        logger.info(f'Trying to fetch all holdings and items information for bib record {mms_id}.')
        physical_inventory_record = self.retrieve(f'{mms_id}/holdings/ALL/items')
        return physical_inventory_record

    def retrieve_all_portfolios(self, mms_id: str) -> str:
        """
        For a given mms_id, get all portfolios.
        param: mms_id: Unique ID of the BIB record the portfolios are connected to.
        :return: Record in XML format.
        """
        logger.info(f'Trying to fetch all portfolios for bib record {mms_id}.')
        e_inventory_record = self.retrieve(f'{mms_id}/portfolios/')
        return e_inventory_record

    def retrieve_all_ecollections(self, mms_id: str) -> str:
        """
        For a given mms_id, get all e-collection information.
        :param mms_id: Unique ID of the BIB record the e-collections are connected to.
        :return: Record in XML format.
        """
        logger.info(f'Trying to fetch all e-collections for bib record {mms_id}.')
        e_inventory_record = self.retrieve(f'{mms_id}/e-collections/')
        return e_inventory_record

    def retrieve_ecollection(self, mms_id: str, collection_id: str) -> str:
        """
        For a given mms_id and collection_id, retrieve one e-collection.
        :param mms_id: Unique ID of the BIB record the e-collection is connected to.
        :param collection_id: Unique ID of the e-collection.
        :return: Record in XML format.
        """
        logger.info(f'Trying to fetch all e-collections for mms_id {mms_id} and collection_id {collection_id}.')
        e_inventory_record = self.retrieve(f'{mms_id}/e-collections/{collection_id}')
        return e_inventory_record


class HoldingsApi(rest_setup.GenericApi):
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

    def retrieve_all_items(self, hol_id: str) -> str:
        """
        For a given mms_id, retrieve all holding and item information.
        :param hol_id: ID of the HOL record the ITMs are connected to.
        :return: Record in XML format.
        """
        logger.info(f'Trying to fetch all items information for hol_id {hol_id}.')
        physical_inventory_record = self.retrieve(f'{hol_id}/items')
        return physical_inventory_record


class ItemsApi(rest_setup.GenericApi):
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


class PortfoliosApi(rest_setup.GenericApi):
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

        base_path = f'/bibs/{self.mms_id}/portfolios/'

        logger.info(f"""Instantiating {type(self).__name__} with mms_id {self.mms_id}.""")

        super().__init__(base_path)


# The following has its own path and can hence not be included in one of the above classes.
# Since it operates on items it is still listed in this module and not elsewhere.
def scan_in_item_by_barcode(item_barcode: str) -> str:
    """
    Retrieve item information by barcode. Please note that this equals a scan-in operation!
    :param item_barcode: Barcode of the item.
    :return: Record in XML format.
    """
    logger.info(f'Trying to fetch item by barcode {item_barcode}.')
    api_url_query = {"item_barcode": item_barcode}
    api_url_query_encoded = parse.urlencode(api_url_query)
    item_record = rest_setup.call_api(f'/items?{api_url_query_encoded}', 'GET', 200)
    return item_record
