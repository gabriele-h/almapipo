"""
Create XML of a single record.
"""

from datetime import datetime, timezone
from logging import getLogger
from re import compile
from typing import List
from xml.etree.ElementTree import Element, SubElement

timestamp_datetime = datetime.now(timezone.utc)
timestamp_str = timestamp_datetime.strftime("%Y%m%d%H%M%S.0")
logger = getLogger(__name__)


def create_record(record_keys: List[str], record_values: List[str]) -> Element:
    """
    For two lists, one with keys, the other with values, create
    a MARC XML record to create new records. You will need to
    wrap this into the according elements like <holding> etc.
    and add other elements where necessary.
    :param record_keys: List of keys for the record's data
    :param record_values: List of values for the record's data
    :return: collection as an xml.etree.ElementTree.Element
    """

    new_record = MarcRecord()

    for i in range(0, len(record_keys)):

        field_key = record_keys[i]
        field_value = record_values[i]

        if field_value != "":

            if field_key in ('LDR', 'leader', 'LDR  '):
                new_record.append_leader(field_value)
            elif field_key[0:2] == "00" and len(field_key) == 3:
                new_record.append_controlfield(field_key, field_value)
            elif compile(r'^[0-9]{3}[0-9A-z ]{2}$').match(field_key) and field_key[0:2] != "00":
                new_record.append_datafield(field_key, field_value)
            else:
                logger.error(f"""field_key '{field_key}' did not match expectations. Skipping.""")

    if "005" not in record_keys:
        new_record.append_controlfield('005', timestamp_str)

    return new_record.root


class MarcRecord:
    """
    Create a single MARC21 record as xml.etree.ElementTree.Element
    """
    def __init__(self):
        self.root = Element('record')

    def append_datafield(self, attributes: str, subfields: str) -> SubElement:
        """
        For given attributes and subfields, create append a datafield to the record.
        :param attributes: tag, ind1 and ind2 in a string without delimiters, e. g. '041  '
        :param subfields: One string of all subfields with "$$<code>" prefix
        :return: datafield as an xml.etree.ElementTree.SubElement
        """
        datafield = SubElement(self.root, "datafield")
        datafield.set("tag", attributes[0:3])
        datafield.set("ind1", attributes[3])
        datafield.set("ind2", attributes[4])

        for subfield in subfields.lstrip("$").split('$$'):

            code = subfield[0]
            content = subfield[1:]
            subfield_element = self.create_subfield(code, content)

            try:
                datafield.append(subfield_element)
            except TypeError:
                logger.error("Could not append subfield.")

        return datafield

    @staticmethod
    def create_subfield(code: str, text: str) -> Element:
        """
        Create subfield by code and text.
        :param code: Attribute "code" of the element with tag "subfield"
        :param text: Content of the subfield element
        :return: subfield as an xml.etree.ElementTree.Element
        """
        subfield = Element("subfield")
        subfield.set("code", code)
        subfield.text = text
        return subfield

    def append_controlfield(self, tag: str, text: str) -> SubElement:
        """
        Append a controlfield to the record by attribute "tag" and content.
        :param tag: Attribute "tag" of the element with tag "controlfield"
        :param text: Content of the controlfield element
        :return: controlfield as an xml.etree.ElementTree.SubElement
        """
        controlfield = self.append_field("controlfield", text)
        controlfield.set("tag", tag)
        return controlfield

    def append_leader(self, text: str) -> SubElement:
        """
        Append a leader to the record.
        :param text: Content of the element with tag "leader"
        :return: leader as an xml.etree.ElementTree.SubElement
        """
        leader = self.append_field("leader", text)
        return leader

    def append_field(self, name: str, text: str) -> SubElement:
        """
        Meta function for appending simple fields.
        :param name: Tag of the xml element
        :param text: Text of the xml element
        :return: Element as and xml.etree.ElementTree.SubElement
        """
        field = SubElement(self.root, name)
        field.text = text
        return field
