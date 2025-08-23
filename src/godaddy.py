
import requests
import typing
import webbrowser

from . import const as c
from . import utils as u


# NOTE: Some of Godaddy's API services will work, until you own 10+ domains.


godaddy_search_link = lambda domain: f"https://www.godaddy.com/pt-br/domainsearch/find?domainToCheck={domain}"
godaddy_eval_link = lambda domain: f"https://br.godaddy.com/domain-value-appraisal/appraisal/?domainToCheck={domain}"


def registered_domains() -> typing.Iterator[dict] | None:
    headers: dict = {
        "Authorization": f"sso-key {c.GODADDY_API_KEY}:{c.GODADDY_API_SECRET}",
        "Accept": "application/json"
    }

    OTEurl: str = "https://api.ote-godaddy.com/v1/domains"
    url: str = "https://api.godaddy.com/v1/domains"

    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        domains = response.json()
        for d in domains:
            yield d
    else:
        c.LOGGER.error(f"API ERROR: {response.status_code}: {response.text}")
        return {
            "error": True,
            "status_code": response.status_code,
            "message": response.text
        }


def check_domain_availability(domaintld: str) -> dict | None:
    OTEurl: str = f"https://api.ote-godaddy.com/v1/domains/available?domain={domaintld}"
    url: str = f"https://api.godaddy.com/v1/domains/available?domain={domaintld}"

    headers = {
        "Authorization": f"sso-key {c.OTE_GODADDY_API_KEY}:{c.OTE_GODADDY_API_SECRET}",
        "Accept": "application/json"
    }

    response = requests.get(OTEurl, headers=headers)

    if response.status_code == 200:
        return response.json()  # Returns availability info
    else:
        c.LOGGER.error(f"API ERROR: {response.status_code}: {response.text}")
        return {
            "error": True,
            "status_code": response.status_code,
            "message": response.text
        }
