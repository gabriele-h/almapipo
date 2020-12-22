"""Main point of access

This will import the other modules and do the following:
* Call the API on a list of records with the according method (POST, GET, PUT, DELETE)
* Save the results of successful API calls to database table fetched_records
* If API calls are not successful, mark the IDs with "error" in job_status_per_id
"""

from logging import getLogger
from datetime import datetime, timezone
from sqlalchemy.orm import Session
from typing import Callable, Iterable

from . import db_setup
from . import db_read_write
from . import input_read
from . import rest_bibs
from . import rest_conf
from . import rest_electronic
from . import rest_users
from . import rest_setup

# Timestamp as inserted in the database
job_timestamp = datetime.now(timezone.utc)

# Logfile
logger = getLogger(__name__)
logger.info(f"Starting {__name__} with Job-ID {job_timestamp}")


def call_api_for_set(
        set_id: str,
        api: str,
        record_type: str,
        method: str,
        manipulate_record: Callable[[str, str], bytes] = None) -> None:
    """
    Retrieve the alma_ids of all members in a set and make API calls on them.
    Will add one line to job_status_per_id for the set itself in addition to all member API calls.
    See call_api_for_list for more information on how the API is called for the members.
    :param set_id: In the Alma UI go to "Set Details" and look for "Set ID"
    :param api: API to call, first path-argument after "almaws/v1" (e. g. "bibs")
    :param record_type: Type of the record to call the API for (e. g. "holdings")
    :param method: As in job_status_per_id, possible values are "DELETE", "GET", "PUT" - POST not implemented yet!
    :param manipulate_record: Function with arguments alma_id and data retrieved via GET that returns record_data
    :return: None
    """
    db_session = db_setup.create_db_session()
    db_read_write.add_alma_id_to_job_status_per_id('GET', set_id, job_timestamp, db_session)
    alma_id_list = rest_conf.retrieve_set_member_alma_ids(set_id)

    try:
        call_api_for_list(alma_id_list, api, record_type, method, manipulate_record)
    except TypeError:
        db_read_write.update_job_status('error', set_id, 'GET', job_timestamp, db_session)
        logger.error(f"""An error occurred while retrieving the set's members. Is the set {set_id} empty?""")
    else:
        db_read_write.update_job_status('done', set_id, 'GET', job_timestamp, db_session)

    db_session.commit()
    db_session.close()


def call_api_for_list(
        alma_ids: Iterable[str],
        api: str,
        record_type: str,
        method: str,
        manipulate_record: Callable[[str, str], bytes] = None) -> None:
    """
    Call api for each record in the list, stores information in the db. See call_api_for_record doc string for details.
    Then outputs the according success rate (number of actions failed, succeeded or not handled at all).
    :param alma_ids: Iterable of alma_ids, e. g. a list or generator
    :param api: API to call, first path-argument after "almaws/v1" (e. g. "bibs")
    :param record_type: Type of the record to call the API for (e. g. "holdings")
    :param method: As in job_status_per_id, possible values are "DELETE", "GET", "PUT" - POST not implemented yet!
    :param manipulate_record: Function with arguments alma_id and data retrieved via GET that returns record_data
    :return: None
    """

    db_session = db_setup.create_db_session()

    for alma_id in alma_ids:
        call_api_for_record(alma_id, api, record_type, method, db_session, manipulate_record)

    db_read_write.log_success_rate(method, job_timestamp, db_session)
    db_session.close()


def call_api_for_record(
        alma_id: str,
        api: str,
        record_type: str,
        method: str,
        db_session: Session,
        manipulate_record: Callable[[str, str], bytes] = None) -> None:
    """
    For one alma_id this function does the following:
    * Add alma_id to job_status_per_id
    * Call GET for the alma_id and store it in fetched_records
    * For method PUT: Manipulate the retrieved record with function manipulate_record and save in sent_records
    * For methods PUT or POST: Save the response to put_post_responses
    * Set status of all API calls in job_status_per_id
    * NOTE: method 'POST' is not implemented yet!
    :param alma_id: alma_id identifying a record and its ancestors, comma-separated (e. g. MMS_ID,HOL_ID)
    :param api: API to call, first path-argument after "almaws/v1" (e. g. "bibs")
    :param record_type: Type of the record to call the API for (e. g. "holdings")
    :param method: As in job_status_per_id, possible values are "DELETE", "GET", "PUT" - POST not implemented yet!
    :param db_session: Session for the postgres database
    :param manipulate_record: Function with arguments alma_id and data retrieved via GET that returns record_data
    :return:
    """

    if method not in ['DELETE', 'GET', 'PUT', 'POST']:
        logger.error(f'Provided method {method} does not match any of the expected values.')
        raise ValueError

    if method == 'POST':
        raise NotImplementedError

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

            db_session.commit()

            if method == 'DELETE':

                db_read_write.add_alma_id_to_job_status_per_id(alma_id, method, job_timestamp, db_session)

                alma_response = CurrentApi.delete(record_id)

                if alma_response is None:
                    db_read_write.update_job_status('error', alma_id, method, job_timestamp, db_session)
                else:
                    db_read_write.update_job_status('done', alma_id, method, job_timestamp, db_session)

            elif method == 'PUT':
                db_read_write.add_alma_id_to_job_status_per_id(alma_id, method, job_timestamp, db_session)

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
                    else:
                        logger.error(f'Did not receive a response for {alma_id}?')
                        db_read_write.update_job_status('error', alma_id, method, job_timestamp, db_session)

    db_session.commit()


def csv_id_generator_and_add_to_source_csv(csv_path: str, validation: bool = True) -> Iterable[str]:
    """
    Imports a whole csv or tsv file to the table source_csv and returns generator of alma_ids as per first column.
    Checks for file existence first.
    :param csv_path: Path to the CSV file to be imported
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
