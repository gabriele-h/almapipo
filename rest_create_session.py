"""Create consistent sessions

Basic definitions for requests sent to the Alma API, including:
* Base URL
* API Key
* Headers
"""

from requests import Session
from os import environ

api_key = environ['ALMA_REST_API_KEY']
api_base_url = environ['ALMA_REST_API_BASE_URL']


def create_alma_api_session():
    session = Session()
    session.headers.update({
        "accept": "application/json",
        "authorization": f"apikey {api_key}",
        "User-Agent": "alma_rest/0.0.1"
    })
    return session
