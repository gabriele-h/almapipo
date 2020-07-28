"""
Query the Alma API for electronic resources
"""

from logging import getLogger

from . import rest_call_api
# noinspection PyUnresolvedReferences
from . import logfile_setup

# Logfile
logger = getLogger(__name__)


class EcollectionsApi(rest_call_api.GenericApi):
    """
    Make API calls for e-collections.
    """
    def __init__(self):
        """
        Initialize API for e-collections.
        """
        base_path = '/electronic/e-collections/'

        logger.info(f'Instantiating {type(self).__name__}.')

        super().__init__(base_path)
