"""Making consistent API calls

Basic definitions for requests sent to the Alma API, including:
* Base URL
* API Key
* Headers

There is one function to define what every session for Alma should look like.

Then for each REST operation (POST, GET, PUT, DELETE) there is one base
function that the more specific modules (like rest_bibs) can make use of.
"""

from logging import getLogger
from os import environ
from requests import Session, Response

# noinspection PyUnresolvedReferences
from . import logfile_setup

# Logfile
logger = getLogger(__name__)

api_key = environ['ALMA_REST_API_KEY']
api_base_url = environ['ALMA_REST_API_BASE_URL']


def update_record(record_data: bytes, url_parameters: str) -> str:
    """Generic function for PUT calls to the Alma API.

    Will return the response if HTTP status code is 200.
    Otherwise the error returned by the API will be added to the
    logfile as an ERROR.
    :param record_data: XML of the record to be updated in bytes format.
    :param url_parameters: Necessary path and arguments for API call.
    :return: Contents of the response.
    """
    response = call_api(url_parameters, 'PUT', 200, record_data)
    return response


def create_record(record_data: bytes, url_parameters: str) -> str:
    """Generic function for POST calls to the Alma API.

    Will return the response if HTTP status code is 200.
    Otherwise the error returned by the API will be added to the
    logfile as an ERROR.
    :param record_data: XML of the record to be created in bytes format.
    :param url_parameters: Necessary path and arguments for API call.
    :return: Contents of the response.
    """
    response_content = call_api(url_parameters, 'POST', 200, record_data)
    return response_content


def delete_record(url_parameters: str) -> str:
    """Generic function for DELETE calls to the Alma API.

    Will return the response if HTTP status code is 204.
    Otherwise the error returned by the API will be added to the
    logfile as an ERROR.

    :param url_parameters: Necessary path and arguments for API call.
    :return: Contents of the response.
    """
    response_content = call_api(url_parameters, 'DELETE', 204)
    return response_content


def get_record(url_parameters: str) -> str:
    """Generic function for GET calls to the Alma API.

    Will return the record if HTTP status code is 200.
    Otherwise the error returned by the API will be added to the
    logfile as an ERROR.

    :param url_parameters: Necessary path and arguments for API call.
    """
    response_content = call_api(url_parameters, 'GET', 200)
    return response_content


def call_api(url_parameters: str, action: str, status_code: int, record_data: bytes = None) -> str:
    """
    Generic function for all API calls.

    Will return the response if the HTTP status code is met.
    Otherwise the error returned by the API will be added to the
    logfile as an ERROR.

    Additionally there is a check for responses that meet the
    required HTTP status code, but still contain an error. In this
    case the response will be saved to the database (if it exists),
    and the error will be added to the logfile as an ERROR.

    :param url_parameters: Necessary path and arguments for the API call.
    :param action: DELETE, GET, POST or PUT
    :param status_code: Status code of a successful action.
    :param record_data: Necessary input for POST and PUT, defaults to None.
    :return: The API's response in XML format as a string.
    """
    with create_alma_api_session('xml') as session:
        alma_url = api_base_url+url_parameters
        if action == 'DELETE':
            alma_response = session.delete(alma_url)
        elif action == 'GET':
            alma_response = session.get(alma_url)
        elif action == 'POST':
            alma_response = session.post(alma_url, data=record_data)
        elif action == 'PUT':
            alma_response = session.put(alma_url, data=record_data)
        else:
            logger.error('No valid REST action supplied.')
            raise ValueError
        if alma_response.status_code == status_code:
            alma_response_content = alma_response.content.decode("utf-8")
            logger.info(
                f'{action} for record "{url_parameters}" completed.'
            )
            if '<errorList>' in alma_response_content:
                logger.warning(f"""The response contained an error, even though it had status code {status_code}.
Reason: {alma_response.status_code} - {alma_response.content}""")
            elif not alma_response_content.startswith('<?xml') and status_code != 204:
                logger.error(f"""The response retrieved does not seem to be valid xml - startswith('<?xml')
{alma_response_content}""")
            return alma_response_content
        else:
            error_string = f"""{action} for record "{url_parameters}" failed.
Reason: {alma_response.status_code} - {alma_response.content.decode("utf-8")}"""
            logger.error(error_string)


def create_alma_api_session(session_format):
    """Create a Session with parameters from env vars
    :param session_format: Format in which records are sent and retrieved.
    :return: Session object for connections to Alma
    """
    session = Session()
    session.headers.update({
        "accept": "application/" + session_format,
        "Content-Type": "application/" + session_format,
        "authorization": f"apikey {api_key}",
        "User-Agent": "alma_rest/0.0.1"
    })
    return session
