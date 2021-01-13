"""Setup for DB connection and tables

Does the following two:
* Prepare setup for the DB connection
* Prepare setup of table definitions

DB needs to support native XML data type, so only PostgreSQL is supported.
"""

from logging import getLogger
import xml.etree.ElementTree as etree
from os import environ

# more sqlalchemy setup below with conditions
from sqlalchemy import create_engine
from sqlalchemy import Column, DateTime, Integer, MetaData, String
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.types import UserDefinedType
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.dialects.postgresql import JSON

# Logfile
logger = getLogger(__name__)

# DB Setup
does_sqlalchemy_log = bool(int(environ["ALMA_REST_DB_VERBOSE"]))

# Basic shortenings for SQLAlchemy
metadata = MetaData()
Base = declarative_base()


# Define Custom Type XML
# https://stackoverflow.com/questions/16153512/using-postgresql-xml-data-type-with-sqlalchemy
# noinspection PyUnusedLocal,PyMethodMayBeStatic
class XMLType(UserDefinedType):
    def get_col_spec(self):
        return "XML"

    def bind_processor(self, dialect):
        def process(value):
            if value is not None:
                if isinstance(value, str):
                    return value
                else:
                    return etree.tostring(value, encoding="unicode")
            else:
                return None
        return process

    def result_processor(self, dialect, coltype):
        def process(value):
            if value is not None:
                value = etree.fromstring(value)
            return value
        return process


# Connection setup
def prepare_connection_params_from_env() -> str:
    """
    Set up the engine for connections to the PostgreSQL database.
    :return: String with connection params as provided via env vars.
    """

    database = environ["ALMA_REST_DB"]
    db_user = environ["ALMA_REST_DB_USER"]
    db_pw = environ["ALMA_REST_DB_PW"]
    db_url = environ["ALMA_REST_DB_URL"]

    connection_params = f"postgresql://{db_user}:{db_pw}@{db_url}/{database}"

    return connection_params


def create_db_session(
        connection_params: str = prepare_connection_params_from_env(),
        verbosity: bool = does_sqlalchemy_log) -> Session:
    """
    Create a DB session according to the information provided in env vars,
    including SQLAlchemy verbosity. Both connection parameters and verbosity
    may be overriden by providing them as paramters to the function call.
    :param connection_params: Parameters to initiate the database connection,
        defaults to info from env vars
    :param verbosity: Whether or not to add SQLAlchemy output to the log,
        defaults to content of env var ALMA_REST_DB_VERBOSE
    :return: Session for connection to the DB.
    """

    db_engine = create_engine(connection_params, echo=verbosity)
    DBSession = sessionmaker(bind=db_engine)
    session = DBSession()

    return session


class JobStatusPerId(Base):
    __tablename__ = "job_status_per_id"

    primary_key = Column(Integer, primary_key=True)
    job_timestamp = Column(DateTime(timezone=True))
    alma_id = Column(String(100))
    job_status = Column(String(5))
    job_action = Column(String(6))


class SourceCsv(Base):
    __tablename__ = "source_csv"

    primary_key = Column(Integer, primary_key=True)
    job_timestamp = Column(DateTime(timezone=True))
    csv_line = Column(JSON)


class FetchedRecords(Base):
    __tablename__ = "fetched_records"

    primary_key = Column(Integer, primary_key=True)
    job_timestamp = Column(DateTime(timezone=True))
    alma_id = Column(String(100))
    alma_record = Column(XMLType)


class SentRecords(Base):
    __tablename__ = "sent_records"

    primary_key = Column(Integer, primary_key=True)
    job_timestamp = Column(DateTime(timezone=True))
    alma_id = Column(String(100))
    alma_record = Column(XMLType)


class PutPostResponses(Base):
    __tablename__ = "put_post_responses"

    primary_key = Column(Integer, primary_key=True)
    job_timestamp = Column(DateTime(timezone=True))
    alma_id = Column(String(100))
    alma_record = Column(XMLType)
