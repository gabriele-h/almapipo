"""Config used package-wide."""

from datetime import datetime, timezone

# Timestamp as inserted in the database and used for logfile-names
job_timestamp = datetime.now(timezone.utc)
