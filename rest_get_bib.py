"""Query the Alma API for a single BIB record
"""

import rest_create_session


def get_bib_by_mms_id(mms_id: str):
    """
    Get BIB record via Alma API.
    :param mms_id: Unique ID of Alma BIB records.
    :return: Record data in JSON format.
    """
    with rest_create_session.create_alma_api_session() as session:
        alma_record = session.get(rest_create_session.api_base_url+f'/bibs/{mms_id}')
    return alma_record
