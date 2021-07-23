"""
Query the Alma API for configurations in the system.
See https://developers.exlibrisgroup.com/console/?url=/wp-content/uploads/alma/openapi/conf.json
"""

import re
from logging import getLogger
from typing import Iterable
from xml.etree.ElementTree import fromstring, tostring

from . import setup_rest

# Logfile
logger = getLogger(__name__)


def retrieve_libraries() -> str:
    """
    Retrieve all libraries configured in Alma.
    :return: str
    """
    logger.info("Trying to fetch all libraries configured in Alma.")
    libraries_record = setup_rest.call_api(f"/conf/libraries/", "GET", 200)
    return libraries_record


def retrieve_library(library: str) -> str:
    """
    Retrieve one specific library.
    :param library:
    :return: str
    """
    logger.info(f"Trying to fetch one library with code {library}.")
    library_record = setup_rest.call_api(
        f"/conf/libraries/{library}", "GET", 200
    )
    return library_record


def retrieve_all_locations_generator(lang: str = None) -> Iterable[str]:
    """
    Retrieve all locations for all libraries in Alma. Note that this will add
    the attribute "library" to the root element "locations" of all xml strings
    in the generator.
    :param lang: Use if different lang than 'en' is needed.
    :return: Generator of strings from get_locations() plus attribute "library"
    """

    logger.info(f"Trying to fetch all locations for all libraries configured "
                f"in Alma.")

    libraries_record = retrieve_libraries()
    libraries_xml = fromstring(libraries_record)

    for library in libraries_xml.findall("library/code"):

        library_code = library.text
        locations = retrieve_locations(library_code, lang)
        locations_xml = fromstring(locations)

        if locations_xml:
            locations_xml.set("library", library_code)
            yield tostring(locations_xml, encoding="unicode")
        else:
            logger.warning(f"Library {library_code} has no locations.")


def retrieve_locations(library: str, lang: str = None) -> str:
    """
    Get the locations of one specific library.
    :param library: Library to fetch the locations for.
    :param lang: Use if a different language than 'en' is needed.
    :return: str
    """
    if lang:
        lang_suffix = f"?lang={lang}"
    else:
        lang_suffix = ""

    logger.info(f"Trying to fetch all locations for library {library}.")

    locations_record = setup_rest.call_api(
        f"/conf/libraries/{library}/locations{lang_suffix}", "GET", 200
    )

    return locations_record


def retrieve_set_member_almaids(set_id: str) -> Iterable[str]:
    """
    For a given set retrieve the almaid for all members from their link
    attribute. If the link is not available, this function will return
    member/id, but be aware, that this is not always sufficient!

    Since not all kinds of sets have the information of an api link for their
    members, this function will not work for example for sets of electronic
    portfolios. Test this function on your set before you use it further.
    If you want to make calls like
    /bibs/{mms-id}/holdings/{hol-id}/items/{item-id},
    this function must return a comma-separated string of those three IDs!

    :param set_id: Set ID as given in Set Details in the Alma UI
    :return: Generator of almaid
    """

    logger.info(f"Trying to extract almaid for all members of set {set_id}.")

    re_prefix = r"^/?\w+/"
    regex_path = r"/\w+/"
    has_url = False

    member_urls_and_ids = retrieve_set_member_link_and_id(set_id)

    for member_url, member_id in member_urls_and_ids:

        if member_url:

            has_url = True
            member_url_path = member_url.replace(setup_rest.api_base_url, "")

            if member_url == member_url_path:
                logger.error(f"Could not remove base_url as per env var from "
                             f"the member's URL. Please check env vars.")
                raise ValueError

            member_url_path_wo_prefix = re.sub(re_prefix, "", member_url_path)
            almaid = re.sub(regex_path, ",", member_url_path_wo_prefix)

        else:
            # Usually we need more than one ID, this is just a fallback
            almaid = member_id

        yield almaid

    if not has_url:
        logger.info("Element member did not have a link attribute. Generator "
                    "yields member/id instead.")


def retrieve_set_member_link_and_id(set_id: str) -> Iterable[Iterable[str]]:
    """
    For a given set retrieve the URLs and IDs for all members.
    :param set_id: Set ID as given in Set Details in the Alma UI
    :return: Generator of list of two values: member/@link and member/id/text()
    """

    logger.info(f"Trying to fetch URLs for all members of {set_id}.")

    num_members = retrieve_set_total_record_count(set_id)

    api_url_path = f"/conf/sets/{set_id}/members"
    api_url_parameters = {"limit": 100}

    for page in range(0, num_members // 100 + 1):

        api_url_parameters["offset"] = page * 100
        api_url = setup_rest.add_parameters(api_url_path, api_url_parameters)

        set_response = setup_rest.call_api(api_url, "GET", 200)
        set_response_xml = fromstring(set_response)

        for member in set_response_xml.findall("member"):

            try:
                link = member.attrib["link"]
            except KeyError:
                link = ""

            yield [link, member.find("id").text]


def retrieve_set_total_record_count(set_id: str) -> int:
    """
    For a given Set retrieve the number of members in the set.
    :param set_id: Set ID as given in Set Details in the Alma UI
    :return: Number of members as int (total_record_count)
    """

    logger.info(f"Trying to fetch number of members for set {set_id}.")

    members_in_set = setup_rest.call_api(
        f"/conf/sets/{set_id}/members?limit=1", "GET", 200
    )
    response_xml = fromstring(members_in_set)
    num_members = response_xml.attrib["total_record_count"]

    return int(num_members)
