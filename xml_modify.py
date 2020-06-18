"""
Does some generic XML modifications like "remove element" or "replace element content".
"""

from copy import deepcopy
from logging import getLogger
from xml.etree import ElementTree
from xml.etree.ElementTree import Element

# noinspection PyUnresolvedReferences
import logfile_setup

# Logfile
logger = getLogger(__name__)


def add_element_to_root(
        xml: ElementTree,
        element_tag: str,
        element_attributes: dict = None,
        element_text: str = None) -> ElementTree:
    """
    For an xml given as an ElementTree, add the given Element.
    The Element will be added as a direct descendant of the root element.
    The original xml fed to the function will be untouched by this operation.
    :param xml: ElementTree of the xml to be manipulated.
    :param element_tag: Type of tag of the element to be added.
    :param element_attributes: Attributes of the element to be added.
    :param element_text: Text of the elemet to be added.
    :return: ElementTree of the manipulated xml.
    """
    manipulated_xml = deepcopy(xml)
    if element_attributes:
        element = Element(element_tag, element_attributes)
    else:
        element = Element(element_tag)
    if element_text:
        element.text = element_text
    manipulated_xml.append(element)
    return manipulated_xml


def remove_element_from_root_by_tag(xml: ElementTree, element_tag: str) -> ElementTree:
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
