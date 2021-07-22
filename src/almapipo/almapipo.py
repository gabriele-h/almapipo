"""Main point of access

This will import the other modules and do the following:
* Call the API on a list of records
* Save the results of successful calls to table fetched_records
* In job_status_per_id keep track of the API-call's success:
    * Unhandled calls keep status "new"
    * Successful calls change to "done"
    * If there is an error to "error"
"""

from datetime import datetime, timezone
from logging import getLogger
from typing import Callable, Iterable

from sqlalchemy.orm import Session

from . import (
    db_read,
    db_write,
    rest_acq,
    rest_bibs,
    rest_conf,
    rest_electronic,
    setup_rest,
    rest_users,
)

# Timestamp as inserted in the database
job_timestamp = datetime.now(timezone.utc)

# Logfile
logger = getLogger(__name__)
logger.info(f"Starting {__name__} with Job-ID {job_timestamp}")


def call_api_for_alma_set(
        set_id: str,
        api: str,
        record_type: str,
        method: str,
        db_session: Session,
        manipulate_xml: Callable[[str, str], bytes] = None) -> bool:
    """
    Retrieve the alma_ids of all members in a set and make API calls on them.
    Will add one line to job_status_per_id for the set itself.
    See call_api_for_list for information on how calls work for set members.
    :param set_id: In the Alma UI go to "Set Details" and look for "Set ID"
    :param api: First path-argument after "almaws/v1" (e. g. "bibs")
    :param record_type: Type of record to call the API for (e. g. "holdings")
    :param method: "DELETE", "GET" or "PUT" (POST not implemented yet!)
    :param db_session: SQLAlchemy session for DB connection
    :param manipulate_xml: Function with arguments alma_id and data_retrieved
    :return: Success of set retrieval
    """
    db_write.add_alma_id_to_job_status_per_id(
        "GET", set_id, job_timestamp, db_session
    )
    alma_id_list = rest_conf.retrieve_set_member_alma_ids(set_id)

    if type(alma_id_list) is None:
        db_write.update_job_status(
            "error", set_id, "GET", job_timestamp, db_session
        )
        logger.error(f"An error occurred while retrieving the set's members."
                     f" Is the set {set_id} empty?")
        return False

    call_api_for_list(
        alma_id_list, api, record_type, method, db_session, manipulate_xml
    )

    db_write.update_job_status(
        "done", set_id, "GET", job_timestamp, db_session
    )

    return True


def call_api_for_list(
        alma_ids: Iterable[str],
        api: str,
        record_type: str,
        method: str,
        db_session: Session,
        manipulate_xml: Callable[[str, str], bytes] = None) -> None:
    """
    Call api for each record in the list, stores information in the db.
    See call_api_for_record doc string for details.
    Then outputs the according success rate (number of actions failed,
    succeeded or not handled at all).
    :param alma_ids: Iterable of alma_ids, e. g. a list or generator
    :param api: First path-argument after "almaws/v1" (e. g. "bibs")
    :param record_type: Type of record to call the API for (e. g. "holdings")
    :param method: "DELETE", "GET" or "PUT" (POST not implemented yet!)
    :param db_session: SQLAlchemy session for DB connection
    :param manipulate_xml: Function with arguments alma_id and data_retrieved
    :return: None
    """

    for alma_id in alma_ids:
        call_api_for_record(
            alma_id, api, record_type, method, db_session, manipulate_xml
        )

    db_read.log_success_rate(method, job_timestamp, db_session)


def call_api_for_record(
        alma_id: str,
        api: str,
        record_type: str,
        method: str,
        db_session: Session,
        manipulate_xml: Callable[[str, str], bytes] = None) -> None:
    """
    For one alma_id this function does the following:
    * Add alma_id to job_status_per_id
    * Call GET for the alma_id and store it in fetched_records
    * For method PUT: Manipulate the retrieved record with function
        manipulate_xml and save in sent_records
    * For methods PUT or POST: Save the response to put_post_responses
    * Set status of all API calls in job_status_per_id
    * NOTE: method 'POST' is not implemented yet!
    :param alma_id: Comma-separated string of record-ids, most specific last
    :param api: First path-argument after "almaws/v1" (e. g. "bibs")
    :param record_type: Type of record to call the API for (e. g. "holdings")
    :param method: "DELETE", "GET" or "PUT" (POST not implemented yet!)
    :param db_session: SQLAlchemy session for DB connection
    :param manipulate_xml: Function with arguments alma_id and data_retrieved
    :return:
    """

    if method not in ["DELETE", "GET", "PUT", "POST"]:
        logger.error(f"Provided method {method} not known.")
        raise ValueError

    if method == "POST":
        raise NotImplementedError

    CurrentApi = instantiate_api_class(alma_id, api, record_type)

    db_write.add_alma_id_to_job_status_per_id(
        alma_id, "GET", job_timestamp, db_session
    )

    record_id = str.split(alma_id, ",")[-1]
    record_data = CurrentApi.retrieve(record_id)

    if not record_data:
        logger.error(f"Could not fetch record {alma_id}.")
        db_write.update_job_status(
            "error", alma_id, "GET", job_timestamp, db_session
        )
    else:
        db_write.add_response_content_to_fetched_records(
            alma_id, record_data, job_timestamp, db_session
        )
        db_write.update_job_status(
            "done", alma_id, "GET", job_timestamp, db_session
        )

        if method == "DELETE":

            db_write.add_alma_id_to_job_status_per_id(
                alma_id, method, job_timestamp, db_session
            )

            alma_response = CurrentApi.delete(record_id)

            if alma_response is None:
                db_write.update_job_status(
                    "error", alma_id, method, job_timestamp, db_session
                )
            else:
                db_write.update_job_status(
                    "done", alma_id, method, job_timestamp, db_session
                )

        elif method == "PUT":

            db_write.add_alma_id_to_job_status_per_id(
                alma_id, method, job_timestamp, db_session
            )

            new_record_data = manipulate_xml(alma_id, record_data)

            if not new_record_data:

                logger.error(f"Could not manipulate data of record {alma_id}.")
                db_write.update_job_status(
                    "error", alma_id, method, job_timestamp, db_session
                )

            else:

                response = CurrentApi.update(record_id, new_record_data)

                if response:

                    logger.info(f"Manipulation for {alma_id} successful."
                                f" Adding to put_post_responses.")

                    db_write.add_put_post_response(
                        alma_id, response, job_timestamp, db_session
                    )
                    db_write.add_sent_record(
                        alma_id, new_record_data, job_timestamp, db_session
                    )
                    db_write.update_job_status(
                        "done", alma_id, method, job_timestamp, db_session
                    )
                    db_read.check_data_sent_equals_response(
                        alma_id, job_timestamp, db_session
                    )

                else:

                    logger.error(f"Did not receive a response for {alma_id}?")

                    db_write.update_job_status(
                        "error", alma_id, method, job_timestamp, db_session
                    )


def instantiate_api_class(
        alma_id: str,
        api: str,
        record_type: str) -> setup_rest.GenericApi:
    """
    Kind of a switch for api calls.
    :param alma_id: Comma-separated string of record-ids, most specific last
    :param api: First path-argument after "almaws/v1" (e. g. "bibs")
    :param record_type: Type of record to call the API for (e. g. "holdings")
    :return: Instance of an Api Object with correct path
    """
    split_alma_id = str.split(alma_id, ",")

    if api == "bibs":

        if record_type == "bibs":
            return rest_bibs.BibsApi()
        elif record_type == "holdings":
            return rest_bibs.HoldingsApi(split_alma_id[0])
        elif record_type == "items":
            return rest_bibs.ItemsApi(split_alma_id[0], split_alma_id[1])
        elif record_type == "portfolios":
            return rest_bibs.PortfoliosApi(split_alma_id[0])
        else:
            raise NotImplementedError

    elif api == "electronic":

        if record_type == "e-collections":
            return rest_electronic.EcollectionsApi()
        elif record_type == "e-services":
            return rest_electronic.EservicesApi(split_alma_id[0])
        elif record_type == "portfolios":
            return rest_electronic.PortfoliosApi(
                split_alma_id[0], split_alma_id[1]
            )
        else:
            raise NotImplementedError

    elif api == "users":

        if record_type == "users":
            return rest_users.UsersApi()
        else:
            raise NotImplementedError

    elif api == "acq":

        if record_type == "vendors":
            return rest_acq.VendorsApi()
        else:
            raise NotImplementedError

    logger.error("The API you are trying to call is not implemented yet"
                 " or does not exist.")
    raise NotImplementedError
