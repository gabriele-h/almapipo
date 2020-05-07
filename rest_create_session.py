"""Create consistent sessions

Basic definitions for requests sent to the Alma API, including:
* Base URL
* API Key
* Headers
"""

from logging import getLogger
from os import environ
from requests import Session

# noinspection PyUnresolvedReferences
import logfile_setup

# Logfile
logger = getLogger(__name__)

api_key = environ['ALMA_REST_API_KEY']
api_base_url = environ['ALMA_REST_API_BASE_URL']


def make_api_call(url_parameters: str):
    """Generic function for API calls.

    Will return the record if HTTP status code is 200 plus a second
    return value for table job_status_per_id. If the operation is successful,
    job_status_per_id will be set to "done" for the record. If the HTTP status
    is anything other than 200, job_status_per_id will be set to "error" and
    the status-code and content of the response will be added to the logfile.

    :param url_parameters: Necessary path and arguments for API call.
    :return: Contents of the Response and status-string for table job_status_per_id.
    """

    with create_alma_api_session() as session:
        alma_url = api_base_url+url_parameters
        alma_response = session.get(alma_url)
        if alma_response.status_code == 200:
            alma_record = alma_response.content
            logger.info(
                f'Record for parameters "{url_parameters}" successfully retrieved.'
            )
            return alma_record
        else:
            logger.error(
                f'Record could not be retrieved. Reason: {alma_response.status_code} - {alma_response.content}'
            )


def create_alma_api_session():
    """Create a Session with parameters from env vars
    :return: Session object for connections to Alma
    """
    session = Session()
    session.headers.update({
        "accept": "application/json",
        "authorization": f"apikey {api_key}",
        "User-Agent": "alma_rest/0.0.1"
    })
    return session
