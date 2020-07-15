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

from . import db_setup
from . import db_read_write
from . import input_read
# noinspection PyUnresolvedReferences
from . import logfile_setup
from . import rest_bibs
from . import rest_electronic
from . import rest_users
from . import xml_extract

# Timestamp as inserted in the database
job_timestamp = datetime.now(timezone.utc)

# Logfile
logger = getLogger(__name__)
logger.info(f"Starting {__name__} with Job-ID {job_timestamp}")


def restore_records_for_csv_list(csv_path: str, api: str, record_type: str) -> None:
    """
    For a list of Alma-IDs given in a CSV file, this function does the following:
    * Query for the latest XML of the fetched record's xml in the database
    * Call POST with the XML on the API defined in the parameters
    * Save the response from the API in table put_post_responses
    * Set status of API call in job_status_per_id
    :param csv_path: Path of the CSV file containing the Alma IDs.
    :param api: API to call, first path-argument after "almaws/v1" (e. g. "bibs")
    :param record_type: Type of the record to call the API for (e. g. "holdings")
    :return: None
    """
    logger.info(f"Trying to restore records listed in {csv_path} with latest version in the database.")
    db_session = db_setup.create_db_session()
    import_csv_and_ids_to_db_tables(csv_path, 'POST')
    list_of_ids = db_read_write.get_list_of_ids_by_status_and_action('new', 'POST', job_timestamp, db_session)
    for alma_id, in list_of_ids:
        record_data = xml_extract.extract_response_from_fetched_records(alma_id)
        alma_response = create_record_for_alma_ids(alma_id, api, record_type, record_data)
        if alma_response is None:
            db_read_write.update_job_status('error', alma_id, 'POST', job_timestamp, db_session)
        else:
            db_read_write.update_job_status('done', alma_id, 'POST', job_timestamp, db_session)
            db_read_write.add_put_post_response(alma_id, alma_response, job_timestamp, db_session)
    db_session.commit()
    db_read_write.log_success_rate('POST', job_timestamp, db_session)
    db_session.close()


def call_api_for_csv_list(
        csv_path: str,
        api: str,
        record_type: str,
        action: str,
        manipulate_record: Callable[[str, str], bytes] = None) -> None:
    """
    For a list of Alma-IDs given in a CSV file, this function does the following:
    * Call GET for the Alma-IDs and store it in fetched_records
    * For action PUT: Manipulate the retrieved record with the manipulation_function
    * For actions PUT or POST: Save the response to put_post_responses
    * Set status of all API calls in job_status_per_id
    * NOTE: action 'POST' is not implemented yet!
    :param csv_path: Path of the CSV file containing the Alma IDs
    :param api: API to call, first path-argument after "almaws/v1" (e. g. "bibs")
    :param record_type: Type of the record to call the API for (e. g. "holdings")
    :param action: As in job_status_per_id, possible values are "DELETE", "GET", "PUT" - POST not implemented yet!
    :param manipulate_record: Function with arguments alma_ids and data retrieved via GET that returns record_data
    :return: None
    """
    if action not in ['DELETE', 'GET', 'PUT', 'POST']:
        logger.error(f'Provided action {action} does not match any of the expected values.')
        raise ValueError
    if action == 'POST':
        raise NotImplementedError

    db_session = db_setup.create_db_session()
    import_csv_and_ids_to_db_tables(csv_path, action)

    list_of_ids = db_read_write.get_list_of_ids_by_status_and_action('new', action, job_timestamp, db_session)

    if action in ['DELETE', 'GET', 'PUT']:
        for alma_id, in list_of_ids:
            if action != 'GET' and action != 'POST':
                db_read_write.add_alma_ids_to_job_status_per_id(alma_id, 'GET', job_timestamp, db_session)
            if action != 'POST':
                record_data = get_record_for_alma_ids(alma_id, api, record_type)
                if not record_data:
                    logger.error(f'Could not fetch record {alma_id}.')
                    db_read_write.update_job_status('error', alma_id, 'GET', job_timestamp, db_session)
                else:
                    db_read_write.add_response_content_to_fetched_records(
                        alma_id, record_data, job_timestamp, db_session
                    )
                    db_read_write.update_job_status('done', alma_id, 'GET', job_timestamp, db_session)
                    if action == 'DELETE':
                        alma_response = delete_record_for_alma_ids(alma_id, api, record_type)
                        if alma_response is None:
                            db_read_write.update_job_status('error', alma_id, action, job_timestamp, db_session)
                        else:
                            db_read_write.update_job_status('done', alma_id, action, job_timestamp, db_session)
                    elif action == 'PUT':
                        new_record_data = manipulate_record(alma_id, record_data)
                        if not new_record_data:
                            logger.error(f'Could not manipulate data of record {alma_id}.')
                            db_read_write.update_job_status('error', alma_id, action, job_timestamp, db_session)
                        else:
                            response = update_record_for_alma_ids(alma_id, api, record_type, new_record_data)
                            if response:
                                logger.info(f'Manipulation for {alma_id} successful. Adding to put_post_responses.')
                                db_read_write.add_put_post_response(alma_id, response, job_timestamp, db_session)
                                db_read_write.add_sent_record(alma_id, new_record_data, job_timestamp, db_session)
                                db_read_write.update_job_status('done', alma_id, action, job_timestamp, db_session)
                                db_read_write.check_data_sent_equals_response(alma_id, job_timestamp, db_session)
                            logger.error(f'Did not receive a response for {alma_id}?')
                            db_read_write.update_job_status('error', alma_id, action, job_timestamp, db_session)

    db_session.commit()
    db_read_write.log_success_rate(action, job_timestamp, db_session)
    db_session.close()


def import_csv_and_ids_to_db_tables(file_path: str, action: str, validation: bool = True) -> None:
    """
    Imports a whole csv or tsv file to the table source_csv.
    Imports valid Alma-IDs to table job_status_per_id.
    Checks for file existence first.
    :param file_path: Path to the CSV file to be imported
    :param action: REST action - GET, PUT, POST or DELETE
    :param validation: If set to "False", the first column will not be checked for validity. Defaults to True.
    :return: None
    """
    if input_read.check_file_path(file_path):
        db_session = db_setup.create_db_session()
        csv_generator = input_read.read_csv_contents(file_path, validation)
        for csv_line in csv_generator:
            # noinspection PyTypeChecker
            db_read_write.add_csv_line_to_tables(csv_line, job_timestamp, db_session, action)
        db_session.commit()
        db_session.close()
    logger.error('No valid file path provided.')
    raise ValueError


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
    Meta-function for all api_calls. Please note that for some API calls there is a fake
    record_type available, such as 'all_items_for_bib'. These will not take additional
    query-parameters, though, and are only meant as convenience functions.
    :param action: DELETE, GET, POST or PUT.
    :param alma_ids: String with concatenated Alma IDs from least to most specific (mms-id, hol-id, item-id)
    :param api: API to call, first path-argument after "almaws/v1" (e. g. "bibs")
    :param record_type: Type of the record, usually last path-argument with hardcoded string (e. g. "holdings")
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
            elif action == 'PUT':
                return rest_bibs.update_bib(record_data, split_alma_ids[0])
        elif record_type == 'holdings':
            if action == 'DELETE':
                return rest_bibs.delete_hol(split_alma_ids[0], split_alma_ids[1])
            elif action == 'GET':
                return rest_bibs.get_hol(split_alma_ids[0], split_alma_ids[1])
            elif action == 'POST':
                return rest_bibs.create_hol(record_data, split_alma_ids[0], split_alma_ids[1])
            elif action == 'PUT':
                return rest_bibs.update_hol(record_data, split_alma_ids[0], split_alma_ids[1])
        elif record_type == 'items':
            if action == 'DELETE':
                return rest_bibs.delete_item(split_alma_ids[0], split_alma_ids[1], split_alma_ids[2])
            elif action == 'GET':
                return rest_bibs.get_item(split_alma_ids[0], split_alma_ids[1], split_alma_ids[2])
            elif action == 'POST':
                return rest_bibs.create_item(record_data, split_alma_ids[0], split_alma_ids[1], split_alma_ids[2])
            elif action == 'PUT':
                return rest_bibs.update_item(record_data, split_alma_ids[0], split_alma_ids[1], split_alma_ids[2])
        elif record_type == 'portfolios':
            if action == 'DELETE':
                return rest_bibs.delete_portfolio(split_alma_ids[0], split_alma_ids[1])
            elif action == 'GET':
                return rest_bibs.get_portfolio(split_alma_ids[0], split_alma_ids[1])
            elif action == 'POST':
                return rest_bibs.create_portfolio(record_data, split_alma_ids[0], split_alma_ids[1])
            elif action == 'PUT':
                return rest_bibs.update_portfolio(record_data, split_alma_ids[0], split_alma_ids[1])
        elif record_type == 'e-collections':
            if action == 'GET':
                return rest_bibs.get_e_collection_with_mms_id(split_alma_ids[0], split_alma_ids[1])
        elif record_type == 'all_holdings':
            if action == 'GET':
                return rest_bibs.get_all_holdings_for_bib(split_alma_ids[0])
        elif record_type == 'all_items_for_bib':
            if action == 'GET':
                return rest_bibs.get_all_items_for_bib(split_alma_ids[0])
        elif record_type == 'all_items_for_holding':
            if action == 'GET':
                return rest_bibs.get_all_items_for_holding(split_alma_ids[0], split_alma_ids[1])
        elif record_type == 'all_portfolios':
            if action == 'GET':
                return rest_bibs.get_all_portfolios_for_bib(split_alma_ids[0])
        elif record_type == 'all_e_collections':
            if action == 'GET':
                return rest_bibs.get_all_e_collections_for_bib(split_alma_ids[0])
    elif api == 'items':
        if record_type == 'items':
            if action == 'GET':
                return rest_bibs.get_item_by_barcode(split_alma_ids[0])
    elif api == 'users':
        if record_type == 'users':
            if action == 'GET':
                return rest_users.get_user(split_alma_ids[0])
    elif api == 'electronic':
        if record_type == 'e-collections':
            if action == 'GET':
                return rest_electronic.get_e_collection(split_alma_ids[0])
            elif action == 'PUT':
                return rest_electronic.update_e_collection(record_data, split_alma_ids[0])
    logger.error('No valid combination of API and record type provided.')
    raise ValueError
