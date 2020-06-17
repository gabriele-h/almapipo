"""
Does some generic XML modifications like "remove element" or "replace element content".
"""

from copy import deepcopy
from logging import getLogger
from xml.etree import ElementTree

# noinspection PyUnresolvedReferences
import logfile_setup

# Logfile
logger = getLogger(__name__)


def remove_element_from_xml_by_tag(xml: ElementTree, element_tag: str) -> ElementTree:
    """
    From an xml given as an ElementTree, remove all elements with the given tag.
    Works only if the element is a direct descendant of the root element.
    The original xml fed to the function will be untouched by this operation.
    :param xml: ElementTree of the xml to be manipulated.
    :param element_tag: Type of tag to be removed from the XML.
    :return: ElementTree of the manipulated xml.
    """
    manipulated_xml = deepcopy(xml)
    for element in manipulated_xml.findall(element_tag):
        manipulated_xml.remove(element)
    return manipulated_xml
