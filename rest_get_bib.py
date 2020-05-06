"""Query the Alma API for a single BIB record
"""

from os import environ

api_key = environ['ALMA_REST_API_KEY']
api_base_url = environ['ALMA_REST_API_BASE_URL']
