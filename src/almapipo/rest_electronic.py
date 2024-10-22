"""
Query the Alma API for electronic resources.
See https://developers.exlibrisgroup.com/console/?url=/wp-content/uploads/alma/openapi/electronic.json
"""

from logging import getLogger

from . import setup_rest

# Logfile
logger = getLogger(__name__)


class EcollectionsApi(setup_rest.GenericApi):
    """
    Make API calls for e-collections.
    """
    def __init__(self):
        """
        Initialize API for e-collections.
        """
        base_path = "/electronic/e-collections/"

        logger.info(f"Instantiating {type(self).__name__}.")

        super().__init__(base_path)


class EservicesApi(setup_rest.GenericApi):
    """
    Make API calls for e-services.
    """
    def __init__(self, collection_id: str):
        """
        Initialize API for e-collections.
        """
        self.collection_id = collection_id

        base_path = f"/electronic/e-collections/{self.collection_id}/"

        logger.info(f"Instantiating {type(self).__name__} with collection_id "
                    f"{self.collection_id}.")

        super().__init__(base_path)


class PortfoliosApi(setup_rest.GenericApi):
    """
    Make API calls for portfolios.
    """

    def __init__(self, collection_id: str, service_id: str):
        """
        Initialize API for portfolios.
        """
        self.collection_id = collection_id
        self.service_id = service_id

        base_path = f"/electronic/e-collections/{self.collection_id}" \
                    f"/e-services/{self.service_id}/"

        logger.info(f"Instantiating {type(self).__name__} with "
                    f"collection_id {self.collection_id} and service_id "
                    f"{self.service_id}.")

        super().__init__(base_path)
