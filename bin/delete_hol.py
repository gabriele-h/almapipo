#!/usr/bin/env python
"""
For a given list of combinations MMS_ID,HOL_ID,
delete the holdings.
"""

from argparse import ArgumentParser
from logging import getLogger
from pathlib import Path

from almapipo import (
    almapipo,
    db_connect,
    db_read,
    input_helpers,
    setup_logfile,
)

# timestamp
job_timestamp = almapipo.job_timestamp

# Logfile
logger = getLogger("delete_hol")
setup_logfile.log_to_stdout(logger)

# provide -h information on the script
parser = ArgumentParser(
    description="Based on a CSV/TSV file containing the necessary alma-ids "
                "delete Holdings from Alma.",
    epilog="")
parser.add_argument(
    "input_file",
    type=Path,
    help="File containing a list of alma_ids to be deleted. Format per line "
         "should be MMSID,HOLID and the file should contain a header."
)
args = parser.parse_args()

# read CSV
csv = input_helpers.CsvHelper(str(args.input_file))
alma_id_generator = csv.extract_almaids()

with db_connect.DBSession() as db_session:

    csv.add_to_source_csv_table(job_timestamp, db_session)
    db_session.commit()

    almapipo.call_api_for_list(
        alma_id_generator,
        "bibs",
        "holdings",
        "DELETE",
        db_session
    )
    db_session.commit()

    db_read.log_success_rate("DELETE", job_timestamp, db_session)
