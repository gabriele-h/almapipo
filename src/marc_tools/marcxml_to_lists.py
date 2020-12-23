"""
This module has two functions, each create a list of MARC fields.
It is primarily intended to create a tsv-file from an iterable of MARC21 records.
One function creates a list that contains strings to identify the fields (e. g. '24500' or '009').
The other function extracts a list of contents for the given MARC21 records as a generator.
"""

from typing import Iterable


def extract_all_keys_sorted(all_records: Iterable[dict]) -> list:
    """
    Makes use of extract_all_keys, then sorts the keys, putting "leader" first.
    :param all_records: Generator of all records given as dictionaries
    :return: Sorted list of all field-keys within a set of MARC21 records
    """
    list_of_keys = extract_all_keys(all_records)

    list_of_keys_sorted = sorted(list_of_keys)
    # put leader first, which will otherwise sort to last
    list_of_keys_sorted.insert(0, list_of_keys_sorted.pop())

    return list_of_keys_sorted


def extract_all_keys(all_records: Iterable[dict]) -> list:
    """
    For a as returned by xml_extract.extract_marc_for_job_timestamp
    create a list of all fields for the header of the tsv.
    :param all_records: Generator of all records given as dictionaries
    :return: Unsorted list of all field-keys within a set of MARC21 records
    """
    list_of_keys = []

    for record_dict in all_records:

        for field_key in record_dict:
            if field_key[0:2] != '00' and field_key != 'leader':
                for field_dict in record_dict[field_key]:

                    ind1 = field_dict['ind1']
                    ind2 = field_dict['ind2']

                    heading_name = field_key + ind1 + ind2

                    if heading_name not in list_of_keys:
                        list_of_keys += [heading_name]

            else:
                if field_key not in list_of_keys:
                    list_of_keys += [field_key]

    return list_of_keys


def extract_values_as_lists(all_records: Iterable[dict], tsv_header: list) -> Iterable[list]:
    """
    For an Iterable of record dicts return an Iterable of lists for the values
    given in tsv_header list.
    :param all_records: Generator of all records given as dictionaries
    :param tsv_header: As created by extract_all_keys or given as argv.tsv_header
    :return: Generator of lists, one list of values per record
    """
    for record_dict in all_records:

        if 'leader' in tsv_header:
            list_of_values = [record_dict['leader']]
        else:
            list_of_values = []

        for tsv_column in tsv_header:
            if len(tsv_column) == 3:
                try:
                    list_of_values += [' ||| '.join(record_dict[tsv_column])]
                except TypeError:
                    try:
                        categories = []

                        for repetition in record_dict[tsv_column]:
                            category = []

                            for subfield in repetition:
                                if subfield not in ['ind1', 'ind2']:
                                    subfields = ','.join(repetition[subfield])
                                    category += [f"""$${subfield}{subfields}"""]

                            categories += [' '.join(category)]

                        list_of_values += [' ||| '.join(categories)]

                    except KeyError:
                        list_of_values += ['']
                except KeyError:
                    list_of_values += ['']
        yield list_of_values
