"""Connect to DB

The DB needs to have support of the data type JSON.

According to SQLAlchemy-documentation the following dialects support JSON:
* PostgreSQL
* MySQL >= 5.7
* sqlite >= 3.9
(see https://docs.sqlalchemy.org/en/13/core/type_basics.html#sqlalchemy.types.JSON)
"""

import logging
from os import environ

from sqlalchemy import create_engine

# noinspection PyUnresolvedReferences
import logfile_setup

# Logfile
logger = logging.getLogger(__name__)

# Dialect
db_dialect = environ["ALMA_REST_DB_DIALECT"]


def import_type_json_for_dialect():
    if db_dialect == "postgresql":
        # noinspection PyUnresolvedReferences
        from sqlalchemy.db_dialects.postgresql import JSON
    elif db_dialect == "mysql":
        # noinspection PyUnresolvedReferences
        from sqlalchemy.db_dialects.mysql import JSON
    elif db_dialect == "sqlite":
        # noinspection PyUnresolvedReferences
        from sqlalchemy.dialects.sqlite import JSON


def setup_db_engine():
    """
    Set up the engine for connections to the PostgreSQL database.
    :return: SQL Engine with connection params as provided via env vars.
    """
    if db_dialect in ('postgresql', 'mysql'):
        db_user = environ["ALMA_REST_DB_USER"]
        db_pw = environ["ALMA_REST_DB_PW"]
        db_url = environ["ALMA_REST_DB_URL"]
    database = environ["ALMA_REST_DB"]
    if db_dialect == "postgresql":
        connection_params = f'postgresql://{db_user}:{db_pw}@{db_url}/{database}'
    elif db_dialect == "mysql":
        connection_params = f'mysql://{db_user}:{db_pw}@{db_url}/{database}'
    elif db_dialect == "sqlite":
        connection_params = f'sqlite:///{database}'
    sql_engine = create_engine(connection_params)
    return sql_engine
