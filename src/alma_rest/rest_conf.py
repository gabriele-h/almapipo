"""
Query the Alma API for configurations in the system.
See https://developers.exlibrisgroup.com/console/?url=/wp-content/uploads/alma/openapi/conf.json
"""

from logging import getLogger
from typing import Iterator
from xml.etree.ElementTree import fromstring, tostring

from . import rest_call_api
# noinspection PyUnresolvedReferences
from . import logfile_setup

# Logfile
logger = getLogger(__name__)


def retrieve_libraries() -> str:
    """
    Retrieve all libraries configured in Alma.
    :return: str
    """
    logger.info("Trying to fetch all libraries configured in Alma.")
    libraries_record = rest_call_api.get_record(f'/conf/libraries/')
    return libraries_record


def retrieve_library(library: str) -> str:
    """
    Retrieve one specific library.
    :param library:
    :return: str
    """
    logger.info(f"Trying to fetch one library with code {library}.")
    library_record = rest_call_api.get_record(f'/conf/libraries/{library}')
    return library_record


def retrieve_all_locations_generator() -> Iterator[str]:
    """
    Retrieve all locations for all libraries in Alma. Note that this will add the attribute
    "library" to the root element "locations" of all xml strings in the generator.
    :return: Generator of strings containing get_locations() return values plus attribute "library"
    """
    logger.info(f"Trying to fetch all locations for all libraries configured in Alma.")
    libraries_record = retrieve_libraries()
    libraries_xml = fromstring(libraries_record)
    for library in libraries_xml.findall('library/code'):
        library_code = library.text
        locations = retrieve_locations(library_code)
        locations_xml = fromstring(locations)
        if locations_xml:
            locations_xml.set('library', library_code)
            yield tostring(locations_xml, encoding='unicode')
        logger.warning(f'Library {library_code} has no locations.')


def retrieve_locations(library: str) -> str:
    """
    Get the locations of one specific library.
    :param library:
    :return: str
    """
    logger.info(f"Trying to fetch all locations for library {library}.")
    locations_record = rest_call_api.get_record(f'/conf/libraries/{library}/locations')
    return locations_record
