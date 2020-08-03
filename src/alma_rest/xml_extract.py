"""
Extracts XML from the database and offers helper functions for further
handling of the record.
"""

from datetime import datetime
from logging import getLogger
from typing import Iterable, Tuple
from xml.etree import ElementTree
from xml.etree.ElementTree import Element

from . import db_read_write
# noinspection PyUnresolvedReferences
from . import logfile_setup

# Logfile
logger = getLogger(__name__)


def extract_response_from_fetched_records(alma_id: str) -> ElementTree:
    """
    From the table fetched_records extract the whole response for the record.
    :param alma_id: Comma separated string of Alma IDs to identify the record.
    :return: ElementTree of the record.
    """
    logger.info(f'Extracting most recent response for alma_id {alma_id} from table fetched_records.')
    response_query = db_read_write.get_most_recent_version_from_fetched_records(alma_id)
    response = response_query.alma_record
    return response


def extract_marc_for_job_timestamp(job_timestamp: datetime) -> Iterable[dict]:
    """
    For a given job_timestamp, query all records from the database and extract
    the MARC21 categories to a dictionary. The keys in the dictionary will be
    a combination of tag, and where applicable ind1, ind2 and subfield code. The leader will
    have the key "LDR". Repeated fields will be split to multiple columns, where
    the count of >1 column is appended as a suffix separated by an underscore.
    The dictionaries are returned within a generator.
    :param job_timestamp: Job to extract the data for
    :return: Generator of dictionaries
    """
    logger.info(f'Getting bibs retrieved on {job_timestamp} from the database and extracting MARC21 categories.')
    record_generator = db_read_write.get_records_by_timestamp(job_timestamp)
    column_headers = create_list_of_marc_fields(record_generator)

    for record in db_read_write.get_records_by_timestamp(job_timestamp):
        yield extract_field_contents_from_marc(record, column_headers)


def extract_field_contents_from_marc(record: Element, column_headers: Iterable[str]) -> dict:
    """
    For a given record extract the information as per column_headers list.
    The latter may be generated automatically for a list of records
    with the create_list_of_marc_fields function.
    :param record: MARC21 record as xml.ElementTree.Element
    :param column_headers: List of strings with keys to find elements by
    :return: Dictionary of values retrieved by keys given in column_headers
    """
    marc21_dict = {'LDR': record.find('record/leader').text}

    for marc_key in column_headers:

        content = ''
        superfields = record.findall(f'record/*[@tag="{marc_key[0:3]}"]')

        if '_' in marc_key:
            num_suffix = int(marc_key.split('_')[1])
            num_repeat = num_suffix - 1
        else:
            num_repeat = 0

        try:
            ind1 = marc_key[3]
            ind2 = marc_key[4]
            sf_code = marc_key[5]
        except IndexError:
            try:
                content = superfields[num_repeat].text
            except IndexError:
                content = ''
        else:

            xpath = f'[@ind1="{ind1}"][@ind2="{ind2}"]/subfield[@code="{sf_code}"]'

            try:
                field = superfields[num_repeat].findall(xpath)[0]
            except IndexError:
                pass
            else:
                content = field.text

        marc21_dict[marc_key] = content or ''

    return marc21_dict


def create_list_of_marc_fields(record_generator: Iterable[Element]) -> Iterable[str]:
    """
    For a given generator of MARC21 records, create a list of keys consisting
    of the tag, and where applicable ind1, ind2 and subfield code. The leader will have the
    key "LDR".
    :param record_generator: Generator containing MARC21 records as etree.Element
    :return: List of strings containing keys of MARC21 categories
    """
    controlfield_headers = []
    datafield_headers = []
    counters = {}

    for record in record_generator:
        controlfield_headers, counters = extract_controlfield_keys_from_marc(record, controlfield_headers, counters)
        datafield_headers, counters = extract_datafield_keys_from_marc(record, datafield_headers, counters)

    controlfield_headers_sorted = sorted(controlfield_headers, key=lambda x: x[0:7])
    datafield_headers_sorted = sorted(datafield_headers, key=lambda x: x[0:7])

    column_headers = controlfield_headers_sorted + datafield_headers_sorted

    return column_headers


def extract_controlfield_keys_from_marc(
        record: Element,
        column_headers: Iterable[str],
        counters: dict) -> Tuple[Iterable[str], dict]:
    """
    For a given record appends descriptors of controlfields to the list
    column_headers provided in the second parameter.
    :param record: MARC21 record as etree.Element
    :param column_headers: List of strings containing keys of MARC21 categories
    :param counters: Keep count of all fields across all records
    :return: Manipulated list of column_headers
    """
    controlfields = record.findall('record/controlfield')
    local_counters = {}

    for controlfield in controlfields:

        controlfield_tag = controlfield.attrib['tag']

        try:
            local_counters[controlfield_tag]
        except KeyError:
            local_counters[controlfield_tag] = 1
        else:
            local_counters[controlfield_tag] += 1

        try:
            counters[controlfield_tag]
        except KeyError:
            counters[controlfield_tag] = 1
        else:
            if local_counters[controlfield_tag] > counters[controlfield_tag]:
                counters[controlfield_tag] = local_counters[controlfield_tag]

        if controlfield_tag not in column_headers:
            column_headers.append(controlfield_tag)

    return column_headers, counters


def extract_datafield_keys_from_marc(
        record: Element,
        column_headers: Iterable[str],
        counters: dict) -> Tuple[Iterable[str], dict]:
    """
    For a given record appends descriptors of datafields to the list
    column_headers provided in the second parameter.
    :param record: MARC21 record as etree.Element
    :param column_headers: List of strings containing keys of MARC21 categories
    :param counters: Keep count of all fields across all records
    :return: Manipulated list of column_headers
    """
    datafields = record.findall('record/datafield')
    local_counters = {}

    for datafield in datafields:

        datafield_tag = datafield.attrib['tag']

        try:
            datafield_ind1 = datafield.attrib['ind1']
        except KeyError:
            datafield_ind1 = None

        try:
            datafield_ind2 = datafield.attrib['ind2']
        except KeyError:
            datafield_ind2 = None

        for subfield in datafield.findall('subfield'):

            try:
                subfield_code = subfield.attrib['code']
            except KeyError:
                logger.warning('No subfield code attribute?')
            else:

                datafield_description = datafield_tag

                if datafield_ind1:
                    datafield_description += datafield_ind1

                if datafield_ind2:
                    datafield_description += datafield_ind2

                if subfield_code:
                    datafield_description += subfield_code

                try:
                    local_counters[datafield_description]
                except KeyError:
                    local_counters[datafield_description] = 1
                else:
                    local_counters[datafield_description] += 1

                try:
                    counters[datafield_description]
                except KeyError:
                    counters[datafield_description] = 1
                else:
                    if local_counters[datafield_description] > counters[datafield_description]:
                        counters[datafield_description] = local_counters[datafield_description]

                if datafield_description not in column_headers:
                    column_headers.append(datafield_description)

                if counters[datafield_description] > 1:
                    max_datafield_description = datafield_description+'_'+str(counters[datafield_description])
                    if max_datafield_description not in counters:
                        for i in range(2, counters[datafield_description]):
                            datafield_description_with_counter = datafield_description+'_'+str(i)
                            if datafield_description_with_counter not in column_headers:
                                column_headers.append(datafield_description_with_counter)

    return column_headers, counters
