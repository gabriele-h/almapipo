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
        alma_url = rest_create_session.api_base_url+f'/bibs/{mms_id}'
        alma_response = session.get(alma_url)
        if alma_response.status_code == "200":
            alma_record = alma_response.content
    return alma_record
