"""Create necessary tables

Only used for initial setup of DB-tables. Checks for existence.
"""

from sqlalchemy import create_engine

import db_setup

connection_params = db_setup.prepare_connection_params_from_env()
db_engine = create_engine(connection_params)

db_setup.Base.metadata.create_all(db_engine)
