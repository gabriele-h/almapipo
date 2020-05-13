"""Main point of access

This will import the other modules and do the following:
* Import a CSV or TSV file to the database tables source_csv and job_status_per_id
* Call the API with the according action (POST, GET, PUT, DELETE)
* Save the results of successful API calls to database table fetched_records
* If API calls are not successful, mark the IDs with "error" in job_status_per_id
"""

from logging import getLogger
from datetime import datetime

import db_read_write
import input_read
# noinspection PyUnresolvedReferences
import logfile_setup
import rest_bibs

# Timestamp for as inserted in the database
job_timestamp = datetime.now()

# Logfile
logger = getLogger(__name__)
logger.info(f"Starting {__name__} with Job-ID {job_timestamp}")


def delete_records_via_api_for_csv_list(csv_path: str, api: str, record_type: str):
    """
    For a list of Alma-IDs given in a CSV file, this function does the following:
    * Save the data from the CSV-file to tables job_status_per_id and source_csv
    * Call GET on the Alma API for each Alma-ID
    * Save the response from the API in table fetched_records
    Note that this will only work for Alma-IDs and not alternatives like "Other system number".

    :param csv_path: Path of the CSV file containing the Alma IDs.
    :param api: API to call, first path-argument after "almaws/v1" (e. g. "bibs")
    :param record_type: Type of the record to call the API for (e. g. "holdings")
    :return:
    """
    db_session = db_read_write.create_db_session()
    get_records_via_api_for_csv_list(csv_path, api, record_type)
    list_of_ids = db_read_write.get_list_of_ids_by_status_and_action('done', 'GET', job_timestamp, db_session)
    for alma_id, in list_of_ids:
        db_read_write.add_alma_ids_to_job_status_per_id(alma_id, job_timestamp, db_session, 'DELETE')
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


def get_records_via_api_for_csv_list(csv_path: str, api: str, record_type: str):
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


def import_csv_to_db_tables(file_path: str, action: str = 'GET', validation: bool = True):
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


def delete_record_for_alma_ids(alma_ids: str, api: str, record_type: str):
    """
    For a specific API and record type make the DELETE call to that API
    and return the resulting response.
    :param alma_ids: String with concatenated Alma IDs from least to most specific (mms-id, hol-id, item-id)
    :param api: API to call, first path-argument after "almaws/v1" (e. g. "bibs")
    :param record_type: Type of the record to call the API for (e. g. "holdings")
    :return: API response
    """
    split_alma_ids = str.split(alma_ids, ',')
    if api == 'bibs' and record_type == 'holdings':
        return rest_bibs.delete_hol(split_alma_ids[0], split_alma_ids[1])
    else:
        logger.error('No valid combination of API and record type provided.')
        raise ValueError


def get_record_for_alma_ids(alma_ids: str, api: str, record_type: str):
    """
    For a specific API and record type make the GET call to that API
    and return the resulting response.
    :param alma_ids: String with concatenated Alma IDs from least to most specific (mms-id, hol-id, item-id)
    :param api: API to call, first path-argument after "almaws/v1" (e. g. "bibs")
    :param record_type: Type of the record to call the API for (e. g. "holdings")
    :return: API response
    """
    split_alma_ids = str.split(alma_ids, ',')
    if api == 'bibs' and record_type == 'bibs':
        return rest_bibs.get_bib(split_alma_ids[0])
    elif api == 'bibs' and record_type == 'holdings':
        return rest_bibs.get_hol(split_alma_ids[0], split_alma_ids[1])
    elif api == 'bibs' and record_type == 'items':
        return rest_bibs.get_item(split_alma_ids[0], split_alma_ids[1], split_alma_ids[2])
    elif api == 'bibs' and record_type == 'portfolios':
        return rest_bibs.get_portfolio(split_alma_ids[0], split_alma_ids[1])
    elif api == 'bibs' and record_type == 'e-collections':
        return rest_bibs.get_e_collection(split_alma_ids[0], split_alma_ids[1])
    else:
        logger.error('No valid combination of API and record type provided.')
        raise ValueError
