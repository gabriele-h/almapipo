"""Setup of DB tables

Table definitions necessary for use of almapipo
"""

from logging import getLogger
import xml.etree.ElementTree as etree

from sqlalchemy import Column, DateTime, Integer, MetaData, String
from sqlalchemy.types import UserDefinedType
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.dialects.postgresql import JSON

# Logfile
logger = getLogger(__name__)

# SQLAlchemy basic settings
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
