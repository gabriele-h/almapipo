"""
This module has two functions, each create a list of MARC fields.
It is primarily intended to create a tsv-file from an iterable of records.
One function creates a list of field identifiers (e. g. '24500' or '009').
The other function extracts a list of contents as a generator.
"""

from logging import getLogger
from typing import Iterable
from xml.etree.ElementTree import Element

from alma_rest import xml_extract

logger = getLogger(__name__)


def extract_all_keys_sorted(all_records: Iterable[dict]) -> list:
    """
    Makes use of extract_all_keys, then sorts the keys, putting "leader" first.
    :param all_records: Generator of all records given as dictionaries
    :return: Sorted list of all field-keys within a set of MARC21 records
    """

    list_of_keys = extract_keys_for_records(all_records)

    list_of_keys_sorted = sorted(list_of_keys)

    # put leader first, which will otherwise sort to last
    list_of_keys_sorted.insert(0, list_of_keys_sorted.pop())

    return list_of_keys_sorted


def extract_keys_for_records(all_records: Iterable[Element]) -> list:
    """
    For an Element as returned by xml_extract.extract_marc_for_job_timestamp
    create a list of all fields for the header of the tsv.
    :param all_records: Generator of all records given as dictionaries
    :return: Unsorted list of all field-keys within a set of MARC21 records
    """
    list_of_keys = []

    for record_element in all_records:

        current_keys = list(
            extract_keys_for_single_record(record_element)
        )

        for key in current_keys:

            if key not in list_of_keys:
                
                list_of_keys += [key]
                
            elif key in list_of_keys \
                    and current_keys.count(key) > list_of_keys.count(key):
                list_of_keys += [key]

    return list_of_keys


def extract_keys_for_single_record(record: Element) -> tuple:
    """
    For a given record Element create a generator of all field_keys,
    which look like this:
    * Leader will be added as "leader" if present
    * Controlfields have a field_key of "tag" (e. g. "009")
    * Datafields have a field_key of "tag" + "ind1" + "ind2" (e. g. "24500")
    :param record: xml.etree.ElementTree.Element of a MARC21 XML record
    :return: generator of field_keys
    """

    if record.find('leader') is not None:
        yield 'leader'

    for field_element in record.findall('.//*[@tag]'):

        if field_element.tag == 'controlfield':

            key = field_element.get('tag')

        elif field_element.tag == 'datafield':

            key = field_element.get('tag') \
                  + field_element.get('ind1') \
                  + field_element.get('ind2')

        else:
            logger.warning(f"XML contains unexpected element "
                           f"{field_element.tag}. Skipping that element.")
            continue

        yield key


def extract_values_as_lists(
        all_records: Iterable[Element],
        tsv_header: list) -> Iterable[list]:
    """
    For an Iterable of record dicts return an Iterable of lists for the values
    given in tsv_header list.
    :param all_records: Generator of all records given as dictionaries
    :param tsv_header: List of strings identifying MARC21 categories
    :return: Generator of lists, one list of values per record
    """
    for field_element in all_records:

        list_of_values = []

        for i in range(len(tsv_header)):

            tag = tsv_header[i][0:3]

            if tsv_header[i] == 'leader':

                list_of_values += [field_element.find('leader').text]

            elif len(tsv_header[i]) == 3:

                xpath = f'controlfield[@tag="{tag}"]'

                if len(field_element.findall(xpath)) > 1:

                    indices = [i for i, x in enumerate(tsv_header)
                               if x == tsv_header[i]]
                    num_occurence = indices.index(i)

                    list_of_values += [field_element.findall(xpath)
                                       [num_occurence].text]

                elif len(field_element.findall(xpath)) == 1:

                    list_of_values += [field_element.find(xpath).text]

                else:
                    list_of_values += ['']

            elif len(tsv_header[i]) == 5:

                ind1 = tsv_header[i][3]
                ind2 = tsv_header[i][4]

                xpath = f'datafield[@tag="{tag}"][@ind1="{ind1}"]' \
                        f'[@ind2="{ind2}"]'

                if len(field_element.findall(xpath)) > 1:

                    indices = [i for i, x in enumerate(tsv_header)
                               if x == tsv_header[i]]
                    num_occurence = indices.index(i)
                    subfields = xml_extract.extract_subfields_as_string(
                        field_element.findall(xpath)[num_occurence]
                    )

                    list_of_values += [subfields]

                elif len(field_element.findall(xpath)) == 1:

                    subfields = xml_extract.extract_subfields_as_string(
                        field_element.find(xpath)
                    )

                    list_of_values += [subfields]

                else:
                    list_of_values += ['']

            else:
                logger.error('Key does not match expected format. Either '
                             '"leader" or length of 3 or 5 expected.')
                continue

        yield list_of_values
