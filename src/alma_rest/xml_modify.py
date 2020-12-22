"""
Does some generic XML modifications like "remove element" or "replace element content".
"""

from copy import deepcopy
from logging import getLogger
from xml.etree import ElementTree
from xml.etree.ElementTree import Element


# Logfile
logger = getLogger(__name__)


def add_element_to_root(
        xml: ElementTree,
        element_tag: str,
        element_text: str = None,
        element_attributes: dict = None) -> ElementTree:
    """
    For an xml given as an ElementTree, add the given Element.
    The Element will be added as a direct descendant of the root element.
    The original xml fed to the function will be left untouched by this operation.
    :param xml: ElementTree of the xml to be manipulated
    :param element_tag: Type of tag of the element to be added
    :param element_text: Text of the element to be added
    :param element_attributes: Attributes of the element to be added
    :return: ElementTree of the manipulated xml
    """
    manipulated_xml = deepcopy(xml)
    element = create_element(element_tag, element_text, element_attributes)
    manipulated_xml.append(element)
    return manipulated_xml


def add_element_to_child(
        xml: ElementTree,
        child: str,
        element_tag: str,
        element_text: str = None,
        element_attributes: dict = None) -> ElementTree:
    """
    For an xml given as an ElementTree, add the given Element to a specific child tag.
    The Element will be added to all children matching the description given for child.
    The original xml fed to the function will be left untouched by this operation.
    :param xml: ElementTree of the xml to be manipulated
    :param child: Path to the child as per Element.findall() - e. g. tag type
    :param element_tag: Type of tag of the element to be added
    :param element_text: Text of the element to be added
    :param element_attributes: Attributes of the element to be added
    :return: ElementTree of the manipulated xml
    """
    manipulated_xml = deepcopy(xml)
    element = create_element(element_tag, element_text, element_attributes)
    for child in manipulated_xml.findall(child):
        child.append(element)
    return manipulated_xml


def update_element(
        xml: ElementTree,
        element_tag: str,
        old_element_text: str = None,
        new_element_text: str = None,
        old_element_attributes: dict = None,
        new_element_attributes: dict = None) -> ElementTree:
    """
    In an xml given as an ElementTree, replace one element by another.
    Please note that you will have to provide all attributes of the element
    to make them match. If the element has more attributes than you provide,
    there will be no match and with that no manipulation.
    If you want to update attributes only without touching the element's text,
    provide the text as None for both old_element_text and new_element_text.
    The original xml fed to the function will be left untouched by this operation.
    :param xml: ElementTree of the xml to be manipulated
    :param element_tag: Type of tag of the element to be replaced
    :param old_element_text: Text of the element to be replaced
    :param new_element_text: Text of the new element
    :param old_element_attributes: Attributes of the element to be replaced
    :param new_element_attributes: Attributes of the new element
    :return: ElementTree of the manipulated xml
    """
    manipulated_xml = deepcopy(xml)
    list_of_elements = check_element_existence(manipulated_xml, element_tag, old_element_text, old_element_attributes)
    for element in list_of_elements:
        if new_element_text:
            element.text = new_element_text
            log_string = f"""Element {element_tag} had text {old_element_text}. """
            log_string += f"""New text is {new_element_text}."""
            logger.info(log_string)
        elif new_element_attributes:
            element.attrib = new_element_attributes
            log_string = f"""Element {element_tag} had attributes {old_element_attributes}. """
            log_string += f"""New attributes are {new_element_attributes}."""
            logger.info(log_string)
        else:
            logger.warning("Could not modify any element.")
    return manipulated_xml


def remove_element_by_path(xml: ElementTree, element_tag: str) -> ElementTree:
    """
    From an xml given as an ElementTree, remove all elements with the given path.
    This operation is based on Element.findall(), so besides providing a tag type
    you can identify the element to remove by path.
    The original xml fed to the function will be left untouched by this operation.
    :param xml: ElementTree of the xml to be manipulated
    :param element_tag: Type of tag to be removed from the XML
    :return: ElementTree of the manipulated xml
    """
    manipulated_xml = deepcopy(xml)
    for element in manipulated_xml.findall(element_tag):
        manipulated_xml.remove(element)
    return manipulated_xml


def check_element_existence(
        xml: ElementTree,
        element_tag: str,
        element_text: str = None,
        element_attributes: dict = None) -> list:
    """
    In an xml given as an ElementTree, check for existence of an element.
    Works only if all attributes provided match. If you want to check for
    attributes only and ignore the text, provide it as None.
    :param xml: ElementTree of the xml to be checked
    :param element_tag: Type of tag of the element to be searched for
    :param element_text: Text of the element to be searched for
    :param element_attributes: Attributes of the element to be searched for
    :return: List of matching Elements
    """
    list_of_elements = []
    for element in xml.findall(element_tag):
        if element_text and element.text == element_text:
            if element_attributes and element.attrib == element_attributes:
                list_of_elements.append(element)
            elif not element_attributes:
                list_of_elements.append(element)
        elif not element_text and element_attributes and element.attrib == element_attributes:
            list_of_elements.append(element)
        elif not element_attributes and not element_text:
            list_of_elements.append(element)
    if not list_of_elements:
        logger.info(f'No matching element found with {element_tag}, {element_text} and {element_attributes}.')
    return list_of_elements


def create_element(
        element_tag: str,
        element_text: str = None,
        element_attributes: dict = None) -> Element:
    """
    Simple helper function to create Elements from strings and a dict.
    :param element_tag: Type of tag of the element to be added
    :param element_text: Text of the element to be added
    :param element_attributes: Attributes of the element to be added
    """
    if element_attributes:
        element = Element(element_tag, element_attributes)
    else:
        element = Element(element_tag)
    if element_text:
        element.text = element_text
    return element
