"""Main point of access

This will import the other modules and do the following:
* Call the API on a list of records with the according method (POST, GET, PUT, DELETE)
* Save the results of successful API calls to database table fetched_records
* If API calls are not successful, mark the IDs with "error" in job_status_per_id
"""

from logging import getLogger
from datetime import datetime, timezone
from typing import Callable, Iterable

from . import db_setup
from . import db_read_write
from . import input_read
# noinspection PyUnresolvedReferences
from . import logfile_setup
from . import rest_bibs
from . import rest_electronic
from . import rest_users
from . import rest_setup

# Timestamp as inserted in the database
job_timestamp = datetime.now(timezone.utc)

# Logfile
logger = getLogger(__name__)
logger.info(f"Starting {__name__} with Job-ID {job_timestamp}")


def call_api_for_list(
        alma_ids: Iterable[str],
        api: str,
        record_type: str,
        method: str,
        manipulate_record: Callable[[str, str], bytes] = None) -> None:
    """
    For a list of Alma-IDs given in a CSV file, this function does the following:
    * Add csv list to job_status_per_id and source_csv for the given method
    * Call GET for the Alma-IDs and store it in fetched_records
    * For method PUT: Manipulate the retrieved record with the manipulation_function
    * For methods PUT or POST: Save the response to put_post_responses
    * Set status of all API calls in job_status_per_id
    * NOTE: method 'POST' is not implemented yet!
    :param alma_ids: Iterable of alma_ids, e. g. a list or generator
    :param api: API to call, first path-argument after "almaws/v1" (e. g. "bibs")
    :param record_type: Type of the record to call the API for (e. g. "holdings")
    :param method: As in job_status_per_id, possible values are "DELETE", "GET", "PUT" - POST not implemented yet!
    :param manipulate_record: Function with arguments alma_id and data retrieved via GET that returns record_data
    :return: None
    """
    if method not in ['DELETE', 'GET', 'PUT', 'POST']:
        logger.error(f'Provided method {method} does not match any of the expected values.')
        raise ValueError

    if method == 'POST':
        raise NotImplementedError

    db_session = db_setup.create_db_session()

    for alma_id in alma_ids:

        CurrentApi = instantiate_api_class(alma_id, api, record_type)

        if method != 'POST':

            db_read_write.add_alma_id_to_job_status_per_id(alma_id, 'GET', job_timestamp, db_session)

            record_id = str.split(alma_id, ',')[-1]
            record_data = CurrentApi.retrieve(record_id)

            if not record_data:
                logger.error(f'Could not fetch record {alma_id}.')
                db_read_write.update_job_status('error', alma_id, 'GET', job_timestamp, db_session)
            else:
                db_read_write.add_response_content_to_fetched_records(
                    alma_id, record_data, job_timestamp, db_session
                )
                db_read_write.update_job_status('done', alma_id, 'GET', job_timestamp, db_session)

                if method == 'DELETE':

                    alma_response = CurrentApi.delete(record_id)

                    if alma_response is None:
                        db_read_write.update_job_status('error', alma_id, method, job_timestamp, db_session)
                    else:
                        db_read_write.update_job_status('done', alma_id, method, job_timestamp, db_session)

                elif method == 'PUT':

                    new_record_data = manipulate_record(alma_id, record_data)

                    if not new_record_data:
                        logger.error(f'Could not manipulate data of record {alma_id}.')
                        db_read_write.update_job_status('error', alma_id, method, job_timestamp, db_session)
                    else:

                        response = CurrentApi.update(record_id, new_record_data)

                        if response:
                            logger.info(f'Manipulation for {alma_id} successful. Adding to put_post_responses.')
                            db_read_write.add_put_post_response(alma_id, response, job_timestamp, db_session)
                            db_read_write.add_sent_record(alma_id, new_record_data, job_timestamp, db_session)
                            db_read_write.update_job_status('done', alma_id, method, job_timestamp, db_session)
                            db_read_write.check_data_sent_equals_response(alma_id, job_timestamp, db_session)

                        logger.error(f'Did not receive a response for {alma_id}?')
                        db_read_write.update_job_status('error', alma_id, method, job_timestamp, db_session)

        db_session.commit()

    db_read_write.log_success_rate(method, job_timestamp, db_session)
    db_session.close()


def csv_id_generator_and_add_to_source_csv(csv_path: str, validation: bool = True) -> Iterable[str]:
    """
    Imports a whole csv or tsv file to the table source_csv and returns generator of alma_ids as per first column.
    Checks for file existence first.
    :param csv_path: Path to the CSV file to be imported
    :param method: GET, PUT, POST or DELETE
    :param validation: If set to "False", the first column will not be checked for validity. Defaults to True.
    :return: Generator of Alma IDs
    """
    if input_read.check_file_path(csv_path):
        db_session = db_setup.create_db_session()
        csv_generator = input_read.read_csv_contents(csv_path, validation)
        for csv_line in csv_generator:
            # noinspection PyTypeChecker
            db_read_write.add_csv_line_to_source_csv_table(csv_line, job_timestamp, db_session)
            db_session.commit()
            yield list(csv_line.values())[0]
        db_session.close()
    else:
        logger.error('No valid file path provided.')
        raise ValueError


def instantiate_api_class(
        alma_id: str,
        api: str,
        record_type: str) -> rest_setup.GenericApi:
    """
    Meta-function for all api_calls. Please note that for some API calls there is a fake
    record_type available, such as 'all_items_for_bib'. These will not take additional
    query-parameters, though, and are only meant as convenience functions.
    :param alma_id: String with concatenated Alma IDs from least to most specific (mms-id, hol-id, item-id)
    :param api: API to call, first path-argument after "almaws/v1" (e. g. "bibs")
    :param record_type: Type of the record, usually last path-argument with hardcoded string (e. g. "holdings")
    :return: API response as a string.
    """
    split_alma_id = str.split(alma_id, ',')

    if api == 'bibs':
        if record_type == 'bibs':
            return rest_bibs.BibsApi()
        elif record_type == 'holdings':
            return rest_bibs.HoldingsApi(split_alma_id[0])
        elif record_type == 'items':
            return rest_bibs.ItemsApi(split_alma_id[0], split_alma_id[1])
        elif record_type == 'portfolios':
            return rest_bibs.PortfoliosApi(split_alma_id[0])
        else:
            raise NotImplementedError
    elif api == 'electronic':
        if record_type == 'e-collections':
            return rest_electronic.EcollectionsApi()
        elif record_type == 'e-services':
            return rest_electronic.EservicesApi(split_alma_id[0])
        elif record_type == 'portfolios':
            return rest_electronic.PortfoliosApi(split_alma_id[0], split_alma_id[1])
        else:
            raise NotImplementedError
    elif api == 'users':
        if record_type == 'users':
            return rest_users.UsersApi()

    logger.error('The API you are trying to call is not implemented yet.')
    raise NotImplementedError
