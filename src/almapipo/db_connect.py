"""Create SQLAlchemy sessions"""

from os import environ

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# SQLAlchemy logging behavior

try:
    does_sqlalchemy_log = bool(int(environ["ALMA_REST_DB_VERBOSE"]))
except KeyError:
    does_sqlalchemy_log = False

# DB Connection setup

database = environ["ALMA_REST_DB"]
db_user = environ["ALMA_REST_DB_USER"]
db_pw = environ["ALMA_REST_DB_PW"]
db_url = environ["ALMA_REST_DB_URL"]

params = f"postgresql://{db_user}:{db_pw}@{db_url}/{database}"

db_engine = create_engine(
    params,
    echo=does_sqlalchemy_log,
    execution_options={
        "isolation_level": "AUTOCOMMIT"
    }
)
DBSession = sessionmaker(bind=db_engine)
