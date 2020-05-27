"""Making consistent API calls

Basic definitions for requests sent to the Alma API, including:
* Base URL
* API Key
* Headers

There is one function to define what every session for Alma should look like.

Then for each REST operation (POST, GET, PUT, DELETE) there is one base
function that the more specific modules (like rest_bibs) can make use of.
"""

# TODO if http status code 2XX, check for errors

from logging import getLogger
from os import environ
from requests import Session

# noinspection PyUnresolvedReferences
import logfile_setup

# Logfile
logger = getLogger(__name__)

api_key = environ['ALMA_REST_API_KEY']
api_base_url = environ['ALMA_REST_API_BASE_URL']


def create_record(record_data: str, url_parameters: str):
    """Generic function for POST calls to the Alma API.

    Will return the response if HTTP status code is 200.
    Otherwise the error returned by the API will be added to the
    logfile as an ERROR.
    :param record_data: XML of the record to be created.
    :param url_parameters: Necessary path and arguments for API call.
    :return: Contents of the response.
    """

    with create_alma_api_session('xml') as session:
        alma_url = api_base_url+url_parameters
        alma_response = session.post(alma_url, data=record_data)
        if alma_response.status_code == 200:
            alma_response_content = alma_response.content
            logger.info(
                    f'Record for parameters "{url_parameters}" successfully POSTED.'
                    )
            return alma_response_content
        else:
            error_string = f"""Record for parameters "{url_parameters}" could not be created.
Reason: {alma_response.status_code} - {alma_response.content}"""
            logger.error(error_string)


def delete_record(url_parameters: str):
    """Generic function for DELETE calls to the Alma API.

    Will return the response if HTTP status code is 204.
    Otherwise the error returned by the API will be added to the
    logfile as an ERROR.

    :param url_parameters: Necessary path and arguments for API call.
    :return: Contents of the response.
    """

    with create_alma_api_session('xml') as session:
        alma_url = api_base_url+url_parameters
        alma_response = session.delete(alma_url)
        if alma_response.status_code == 204:
            alma_response_content = alma_response.content
            logger.info(
                f'Record for parameters "{url_parameters}" successfully DELETED.'
            )
            return alma_response_content
        else:
            error_string = f"""Record for parameters "{url_parameters}" could not be deleted.
Reason: {alma_response.status_code} - {alma_response.content}"""
            logger.error(error_string)


def get_record(url_parameters: str):
    """Generic function for GET calls to the Alma API.

    Will return the record if HTTP status code is 200.
    Otherwise the error returned by the API will be added to the
    logfile as an ERROR.

    :param url_parameters: Necessary path and arguments for API call.
    :return: Contents of the Response and status-string for table job_status_per_id.
    """

    with create_alma_api_session('xml') as session:
        alma_url = api_base_url+url_parameters
        alma_response = session.get(alma_url)
        if alma_response.status_code == 200:
            alma_response_content = alma_response.content
            logger.info(
                f'Record for parameters "{url_parameters}" successfully retrieved.'
            )
            return alma_response_content
        else:
            error_string = f"""Record for parameters "{url_parameters}" could not be retrieved.
Reason: {alma_response.status_code} - {alma_response.content}"""
            logger.error(error_string)


def create_alma_api_session(session_format):
    """Create a Session with parameters from env vars
    :param session_format: Format in which records are sent and retrieved.
    :return: Session object for connections to Alma
    """
    session = Session()
    session.headers.update({
        "accept": "application/" + session_format,
        "content_type": "application/" + session_format,
        "authorization": f"apikey {api_key}",
        "User-Agent": "alma_rest/0.0.1"
    })
    return session
