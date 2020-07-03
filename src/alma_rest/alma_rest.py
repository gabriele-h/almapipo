"""Main point of access

This will import the other modules and do the following:
* Import a CSV or TSV file to the database tables source_csv and job_status_per_id
* Call the API with the according action (POST, GET, PUT, DELETE)
* Save the results of successful API calls to database table fetched_records
* If API calls are not successful, mark the IDs with "error" in job_status_per_id
"""

from logging import getLogger
from datetime import datetime, timezone
from typing import Callable

from . import db_read_write
from . import input_read
# noinspection PyUnresolvedReferences
from . import logfile_setup
from . import rest_bibs
from . import rest_electronic
from . import rest_users
from . import xml_extract

# Timestamp for as inserted in the database
job_timestamp = datetime.now(timezone.utc)

# Logfile
logger = getLogger(__name__)
logger.info(f"Starting {__name__} with Job-ID {job_timestamp}")


def update_records_via_api_for_csv_list(
        csv_path: str,
        api: str,
        record_type: str,
        manipulation: Callable[[str, str], bytes]) -> None:
    """
    Fro a list of Alma-IDs given in a CSV file, this function does the following:
    * Call GET for the Alma-IDs and store it in fetched_records
    * Manipulate the retrieved record with the manipulation_function
    * Call PUT with the manipulated data if input for manipulation_function and its output differ
    * Save the response to the PUT call in put_post_responses
    * Set status of all API calls in job_status_per_id
    :param csv_path: Path of the CSV file containing the Alma IDs.
    :param api: API to call, first path-argument after "almaws/v1" (e. g. "bibs")
    :param record_type: Type of the record to call the API for (e. g. "holdings")
    :param manipulation: Function with arguments alma_ids and data retrieved via GET. Returns manipulated data.
    :return: None
    """
    db_session = db_read_write.create_db_session()
    import_csv_to_db_tables(csv_path, 'PUT')
    list_of_ids = db_read_write.get_list_of_ids_by_status_and_action('new', 'PUT', job_timestamp, db_session)
    for alma_id, in list_of_ids:
        record_data = get_record_for_alma_ids(alma_id, api, record_type)
        if not record_data:
            logger.error(f'Could not fetch record {alma_id}.')
            db_read_write.update_job_status_for_alma_id('error', alma_id, job_timestamp, db_session, 'PUT')
        else:
            db_read_write.add_fetched_record_to_session(alma_id, record_data, job_timestamp, db_session)
            new_record_data = manipulation(alma_id, record_data)
            if not new_record_data:
                logger.error(f'Could not manipulate data of record {alma_id}.')
                db_read_write.update_job_status_for_alma_id('error', alma_id, job_timestamp, db_session, 'PUT')
            elif record_data == new_record_data:
                logger.error(f"{manipulation.__name__} did not carry out a change of {alma_id}.")
                db_read_write.update_job_status_for_alma_id('error', alma_id, job_timestamp, db_session, 'PUT')
            else:
                logger.info(f'Record manipulation for {alma_id} successful. Adding to put_post_response.')
                update_record_for_alma_ids(alma_id, api, record_type, new_record_data)
                db_read_write.add_put_post_response_to_session(alma_id, new_record_data, job_timestamp, db_session)
                db_read_write.add_sent_record_to_session(alma_id, new_record_data, job_timestamp, db_session)
                db_read_write.update_job_status_for_alma_id('done', alma_id, job_timestamp, db_session, 'PUT')
    db_session.commit()
    ids_done = db_read_write.get_list_of_ids_by_status_and_action('done', 'PUT', job_timestamp, db_session)
    ids_error = db_read_write.get_list_of_ids_by_status_and_action('error', 'PUT', job_timestamp, db_session)
    ids_new = db_read_write.get_list_of_ids_by_status_and_action('new', 'PUT', job_timestamp, db_session)
    logger.info(f"Completed PUT successfully for {ids_done.count()} record(s).")
    logger.info(f"Errors were encountered for PUT of {ids_error.count()} record(s).")
    logger.info(f"PUT was not handled at all for {ids_new.count()} record(s).")
    db_session.close()


def restore_records_from_db_via_api_for_csv_list(csv_path: str, api: str, record_type: str) -> None:
    """
    For a list of Alma-IDs given in a CSV file, this function does the following:
    * Query for the latest version of the fetched record's xml in the local database
    * Call POST with the XML on the API defined in the parameters
    * Save the response from the API in table fetched_records
    * Set status of API call in job_status_per_id
    :param csv_path: Path of the CSV file containing the Alma IDs.
    :param api: API to call, first path-argument after "almaws/v1" (e. g. "bibs")
    :param record_type: Type of the record to call the API for (e. g. "holdings")
    :return: None
    """
    db_session = db_read_write.create_db_session()
    import_csv_to_db_tables(csv_path, 'POST')
    list_of_ids = db_read_write.get_list_of_ids_by_status_and_action('new', 'POST', job_timestamp, db_session)
    for alma_id, in list_of_ids:
        record_data = xml_extract.extract_response_from_fetched_records(alma_id)
        alma_response = create_record_for_alma_ids(alma_id, api, record_type, record_data)
        if alma_response is None:
            db_read_write.update_job_status_for_alma_id('error', alma_id, job_timestamp, db_session, 'POST')
        else:
            db_read_write.update_job_status_for_alma_id('done', alma_id, job_timestamp, db_session, 'POST')
    db_session.commit()
    ids_done = db_read_write.get_list_of_ids_by_status_and_action('done', 'POST', job_timestamp, db_session)
    ids_error = db_read_write.get_list_of_ids_by_status_and_action('error', 'POST', job_timestamp, db_session)
    logger.info(f"Completed POST successfully for {ids_done.count()} record(s).")
    logger.info(f"Errors were encountered for POST of {ids_error.count()} record(s).")
    db_session.close()


def delete_records_via_api_for_csv_list(csv_path: str, api: str, record_type: str) -> None:
    """
    For a list of Alma-IDs given in a CSV file, this function does the following:
    * Save the data from the CSV-file to tables job_status_per_id and source_csv
    * Call GET on the Alma API for each Alma-ID
    * Save the response from the API in table fetched_records
    * For all successful GET calls, add DELETE lines to job_status_per_id
    * Call DELETE on the Alma API for each Alma-ID that could be fetched via GET
    Note that this will only work for Alma-IDs and not alternatives like "Other system number"
    or other kinds of bibs queries.

    :param csv_path: Path of the CSV file containing the Alma IDs.
    :param api: API to call, first path-argument after "almaws/v1" (e. g. "bibs")
    :param record_type: Type of the record to call the API for (e. g. "holdings")
    :return: None
    """
    db_session = db_read_write.create_db_session()
    get_records_via_api_for_csv_list(csv_path, api, record_type)
    list_of_ids = db_read_write.get_list_of_ids_by_status_and_action('done', 'GET', job_timestamp, db_session)
    for alma_id, in list_of_ids:
        db_read_write.add_alma_ids_to_job_status_per_id(alma_id, 'DELETE', job_timestamp, db_session)
        alma_response = delete_record_for_alma_ids(alma_id, api, record_type)
        if alma_response is None:
            db_read_write.update_job_status_for_alma_id('error', alma_id, job_timestamp, db_session, 'DELETE')
        else:
            db_read_write.update_job_status_for_alma_id('done', alma_id, job_timestamp, db_session, 'DELETE')
    db_session.commit()
    ids_done = db_read_write.get_list_of_ids_by_status_and_action('done', 'DELETE', job_timestamp, db_session)
    ids_error = db_read_write.get_list_of_ids_by_status_and_action('error', 'DELETE', job_timestamp, db_session)
    logger.info(f"Completed DELETE successfully for {ids_done.count()} record(s).")
    logger.info(f"Errors were encountered for DELETE of {ids_error.count()} record(s).")
    db_session.close()


def get_records_via_api_for_csv_list(csv_path: str, api: str, record_type: str) -> None:
    """
    For a list of Alma-IDs given in a CSV file, this function does the following:
    * Save the data from the CSV-file to tables job_status_per_id and source_csv
    * Call GET on the Alma API for each Alma-ID
    * Save the response from the API in table fetched_records
    Note that this will only work for Alma-IDs and not alternatives like "Other system number".

    :param csv_path: Path of the CSV file containing the Alma IDs.
    :param api: API to call, first path-argument after "almaws/v1" (e. g. "bibs")
    :param record_type: Type of the record to call the API for (e. g. "holdings")
    :return: None
    """
    db_session = db_read_write.create_db_session()
    import_csv_to_db_tables(csv_path, 'GET')
    list_of_ids = db_read_write.get_list_of_ids_by_status_and_action('new', 'GET', job_timestamp, db_session)
    for alma_id, in list_of_ids:
        record_data = get_record_for_alma_ids(alma_id, api, record_type)
        if record_data is None:
            db_read_write.update_job_status_for_alma_id('error', alma_id, job_timestamp, db_session)
        else:
            db_read_write.update_job_status_for_alma_id('done', alma_id, job_timestamp, db_session)
            db_read_write.add_fetched_record_to_session(alma_id, record_data, job_timestamp, db_session)
    db_session.commit()
    ids_done = db_read_write.get_list_of_ids_by_status_and_action('done', 'GET', job_timestamp, db_session)
    ids_error = db_read_write.get_list_of_ids_by_status_and_action('error', 'GET', job_timestamp, db_session)
    logger.info(f"Completed GET successfully for {ids_done.count()} record(s).")
    logger.info(f"Errors were encountered for GET of {ids_error.count()} record(s).")
    db_session.close()


def import_csv_to_db_tables(file_path: str, action: str = 'GET', validation: bool = True) -> None:
    """
    Imports a whole csv or tsv file to the table source_csv.
    Imports valid Alma-IDs to table job_status_per_id.
    Checks for file existence first.
    NOTE: If no action (GET, PUT, POST or DELETE) is provided,
    it will default to "GET".
    :param file_path: Path to the CSV file to be imported.
    :param action: REST action - GET, PUT, POST or DELETE, defaults to empty string.
    :param validation: If set to "False", the first column will not be checked for validity. Defaults to True.
    :return: None
    """
    if input_read.check_file_path(file_path):
        session = db_read_write.create_db_session()
        csv_generator = input_read.read_csv_contents(file_path, validation)
        for csv_line in csv_generator:
            # noinspection PyTypeChecker
            db_read_write.add_csv_line_to_session(csv_line, job_timestamp, session, action)
        session.commit()
    else:
        logger.error('No valid file path provided.')


def update_record_for_alma_ids(alma_ids: str, api: str, record_type: str, record_data: bytes) -> str:
    """
    For a specific API and record type make the PUT call to that API
    and return the resulting response.
    :param alma_ids: String with concatenated Alma IDs from least to most specific (mms-id, hol-id, item-id)
    :param api: API to call, first path-argument after "almaws/v1" (e. g. "bibs")
    :param record_type: Type of the record to call the API for (e. g. "holdings")
    :param record_data: Data of the record to be updated (usually XML)
    :return: API response
    """
    response = call_api_for_record('PUT', alma_ids, api, record_type, record_data)
    return response


def create_record_for_alma_ids(alma_ids: str, api: str, record_type: str, record_data: bytes) -> str:
    """
    For a specific API and record type make the POST call to that API
    and return the resulting response.
    :param alma_ids: String with concatenated Alma IDs from least to most specific (mms-id, hol-id, item-id)
    :param api: API to call, first path-argument after "almaws/v1" (e. g. "bibs")
    :param record_type: Type of the record to call the API for (e. g. "holdings")
    :param record_data: Data of the record to be created (usually XML)
    :return: API response
    """
    response = call_api_for_record('POST', alma_ids, api, record_type, record_data)
    return response


def delete_record_for_alma_ids(alma_ids: str, api: str, record_type: str) -> str:
    """
    For a specific API and record type make the DELETE call to that API
    and return the resulting response.
    :param alma_ids: String with concatenated Alma IDs from least to most specific (mms-id, hol-id, item-id)
    :param api: API to call, first path-argument after "almaws/v1" (e. g. "bibs")
    :param record_type: Type of the record to call the API for (e. g. "holdings")
    :return: API response
    """
    response = call_api_for_record('DELETE', alma_ids, api, record_type)
    return response


def get_record_for_alma_ids(alma_ids: str, api: str, record_type: str) -> str:
    """
    For a specific API and record type make the GET call to that API
    and return the resulting response.
    :param alma_ids: String with concatenated Alma IDs from least to most specific (mms-id, hol-id, item-id)
    :param api: API to call, first path-argument after "almaws/v1" (e. g. "bibs")
    :param record_type: Type of the record to call the API for (e. g. "holdings")
    :return: API response
    """
    response = call_api_for_record('GET', alma_ids, api, record_type)
    return response


def call_api_for_record(action: str, alma_ids: str, api: str, record_type: str, record_data: bytes = None) -> str:
    """
    Meta-function for all api_calls.
    :param action: DELETE, GET, POST or PUT.
    :param alma_ids: String with concatenated Alma IDs from least to most specific (mms-id, hol-id, item-id)
    :param api: API to call, first path-argument after "almaws/v1" (e. g. "bibs")
    :param record_type: Type of the record to call the API for (e. g. "holdings")
    :param record_data: Only necessary for POST and PUT actions.
    :return: API response as a string.
    """
    split_alma_ids = str.split(alma_ids, ',')
    if api == 'bibs':
        if record_type == 'bibs':
            if action == 'DELETE':
                return rest_bibs.delete_bib(split_alma_ids[0])
            elif action == 'GET':
                return rest_bibs.get_bib(split_alma_ids[0])
            elif action == 'POST':
                return rest_bibs.create_bib(record_data, split_alma_ids[0])
            else:
                logger.error('No valid combination of API, record type and action provided.')
                raise ValueError
        elif record_type == 'holdings':
            if action == 'DELETE':
                return rest_bibs.delete_hol(split_alma_ids[0], split_alma_ids[1])
            elif action == 'GET':
                return rest_bibs.get_hol(split_alma_ids[0], split_alma_ids[1])
            elif action == 'POST':
                return rest_bibs.create_hol(record_data, split_alma_ids[0], split_alma_ids[1])
            elif action == 'PUT':
                return rest_bibs.update_hol(record_data, split_alma_ids[0], split_alma_ids[1])
            else:
                logger.error('No valid combination of API, record type and action provided.')
                raise ValueError
        elif record_type == 'items':
            if action == 'DELETE':
                return rest_bibs.delete_item(split_alma_ids[0], split_alma_ids[1], split_alma_ids[2])
            elif action == 'GET':
                return rest_bibs.get_item(split_alma_ids[0], split_alma_ids[1], split_alma_ids[2])
            elif action == 'POST':
                return rest_bibs.create_item(record_data, split_alma_ids[0], split_alma_ids[1], split_alma_ids[2])
            else:
                logger.error('No valid combination of API, record type and action provided.')
                raise ValueError
        elif record_type == 'portfolios':
            if action == 'DELETE':
                return rest_bibs.delete_portfolio(split_alma_ids[0], split_alma_ids[1])
            elif action == 'GET':
                return rest_bibs.get_portfolio(split_alma_ids[0], split_alma_ids[1])
            elif action == 'POST':
                return rest_bibs.create_portfolio(record_data, split_alma_ids[0], split_alma_ids[1])
            else:
                logger.error('No valid combination of API, record type and action provided.')
                raise ValueError
        elif record_type == 'e-collections':
            if action == 'DELETE':
                return rest_bibs.delete_e_collection(split_alma_ids[0], split_alma_ids[1])
            elif action == 'GET':
                return rest_bibs.get_e_collection_with_mms_id(split_alma_ids[0], split_alma_ids[1])
            elif action == 'POST':
                return rest_bibs.create_e_collection(record_data, split_alma_ids[0], split_alma_ids[1])
            else:
                logger.error('No valid combination of API, record type and action provided.')
                raise ValueError
        elif record_type == 'all_items':
            if action == 'GET':
                return rest_bibs.get_all_items_for_bib(split_alma_ids[0])
            else:
                logger.error('No valid combination of API, record type and action provided.')
                raise ValueError
        else:
            logger.error('No valid combination of API and record type provided.')
            raise ValueError
    elif api == 'items':
        if record_type == 'items':
            if action == 'GET':
                return rest_bibs.get_item_by_barcode(split_alma_ids[0])
            else:
                logger.error('No valid combination of API, record type and action provided.')
                raise ValueError
        else:
            logger.error('No valid combination of API and record type provided.')
            raise ValueError
    elif api == 'users':
        if record_type == 'users':
            if action == 'GET':
                return rest_users.get_user(split_alma_ids[0])
            else:
                logger.error('No valid combination of API, record type and action provided.')
                raise ValueError
        else:
            logger.error('No valid combination of API and record type provided.')
            raise ValueError
    elif api == 'electronic':
        if record_type == 'e-collections':
            if action == 'GET':
                return rest_electronic.get_e_collection(split_alma_ids[0])
            elif action == 'PUT':
                return rest_electronic.update_e_collection(record_data, split_alma_ids[0])
        else:
            logger.error('No valid combination of API, record type and action provided.')
            raise ValueError
    else:
        logger.error('No valid combination of API and record type provided.')
        raise ValueError
