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


def create_marc(record_keys: List[str], record_values: List[str]) -> Element:
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


class ItemRecord:
    """
    Create a single item as xml.etree.ElementTree.Element.

    Base for this structure is the example as listed on
    https://developers.exlibrisgroup.com/alma/apis/docs/xsd/rest_item.xsd/?tags=POST
    (last checked on 2021-10-14)
    """
    def __init__(self):
        self.root = Element('item')
        self.item_data = SubElement(self.root, 'item_data')
        self.item_data.set("link", "")
        self.holding_data = SubElement(self.root, 'holding_data')
        self.holding_data.set("link", "")
        self.holding_id = SubElement(self.holding_data, 'holding_id')
        self.copy_id = SubElement(self.holding_data, 'copy_id')
        self.in_temp_location = SubElement(self.holding_data, 'in_temp_location')
        self.temp_library = SubElement(self.holding_data, 'temp_library')
        self.temp_location = SubElement(self.holding_data, 'temp_location')
        self.temp_call_number_type = SubElement(self.holding_data, 'temp_call_number_type')
        self.temp_call_number = SubElement(self.holding_data, 'temp_call_number')
        self.temp_call_number_source = SubElement(self.holding_data, 'temp_call_number_source')
        self.temp_policy = SubElement(self.holding_data, 'temp_policy')
        self.due_back_date = SubElement(self.holding_data, 'due_back_date')
        self.barcode = SubElement(self.item_data, 'barcode')
        self.physical_material_type = SubElement(self.item_data, 'physical_material_type')
        self.policy = SubElement(self.item_data, 'policy')
        self.provenance = SubElement(self.item_data, 'provenance')
        self.po_line = SubElement(self.item_data, 'po_line')
        self.issue_date = SubElement(self.item_data, 'issue_date')
        self.is_magnetic = SubElement(self.item_data, 'is_magnetic')
        self.arrival_date = SubElement(self.item_data, 'arrival_date')
        self.expected_arrival_date = SubElement(self.item_data, 'expected_arrival_date')
        self.year_of_issue = SubElement(self.item_data, 'year_of_issue')
        self.enumeration_a = SubElement(self.item_data, 'enumeration_a')
        self.enumeration_b = SubElement(self.item_data, 'enumeration_b')
        self.enumeration_c = SubElement(self.item_data, 'enumeration_c')
        self.enumeration_d = SubElement(self.item_data, 'enumeration_d')
        self.enumeration_e = SubElement(self.item_data, 'enumeration_e')
        self.enumeration_f = SubElement(self.item_data, 'enumeration_f')
        self.enumeration_g = SubElement(self.item_data, 'enumeration_g')
        self.enumeration_h = SubElement(self.item_data, 'enumeration_h')
        self.chronology_i = SubElement(self.item_data, 'chronology_i')
        self.chronology_j = SubElement(self.item_data, 'chronology_j')
        self.chronology_k = SubElement(self.item_data, 'chronology_k')
        self.chronology_l = SubElement(self.item_data, 'chronology_l')
        self.chronology_m = SubElement(self.item_data, 'chronology_m')
        self.break_indicator = SubElement(self.item_data, 'break_indicator')
        self.pattern_type = SubElement(self.item_data, 'pattern_type')
        self.linking_number = SubElement(self.item_data, 'linking_number')
        self.description = SubElement(self.item_data, 'description')
        self.replacement_cost = SubElement(self.item_data, 'replacement_cost')
        self.receiving_operator = SubElement(self.item_data, 'receiving_operator')
        self.inventory_number = SubElement(self.item_data, 'inventory_number')
        self.inventory_date = SubElement(self.item_data, 'inventory_date')
        self.inventory_price = SubElement(self.item_data, 'inventory_price')
        self.receive_number = SubElement(self.item_data, 'receive_number')
        self.weeding_number = SubElement(self.item_data, 'weeding_number')
        self.weeding_date = SubElement(self.item_data, 'weeding_date')
        self.alternative_call_number = SubElement(self.item_data, 'alternative_call_number')
        self.alt_number_source = SubElement(self.item_data, 'alt_number_source')
        self.storage_location_id = SubElement(self.item_data, 'storage_location_id')
        self.pages = SubElement(self.item_data, 'pages')
        self.pieces = SubElement(self.item_data, 'pieces')
        self.public_note = SubElement(self.item_data, 'public_note')
        self.fulfillment_note = SubElement(self.item_data, 'fulfillment_note')
        self.internal_note_1 = SubElement(self.item_data, 'internal_note_1')
        self.internal_note_2 = SubElement(self.item_data, 'internal_note_2')
        self.internal_note_3 = SubElement(self.item_data, 'internal_note_3')
        self.statistics_note_1 = SubElement(self.item_data, 'statistics_note_1')
        self.statistics_note_2 = SubElement(self.item_data, 'statistics_note_2')
        self.statistics_note_3 = SubElement(self.item_data, 'statistics_note_3')
        self.physical_condition = SubElement(self.item_data, 'physical_condition')
