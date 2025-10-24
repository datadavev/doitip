"""Working with ROR identifiers."""

import logging

import requests

import doitip.model


ROR_API_URL = "https://api.ror.org"

# Reserved characters in OpenSearch query terms.
ES_RESERVED_CHARS = str.maketrans(
    {
        "+": "\\+",
        "-": "\\-",
        "&": "\\&",
        "|": "\\|",
        "!": "\\!",
        "(": "\\(",
        ")": "\\)",
        "{": "\\{",
        "}": "\\}",
        "[": "\\[]",
        "]": "\\]",
        "^": "\\^",
        '"': '\\"',
        "~": "\\~",
        "*": "\\*",
        "?": "\\?",
        ":": "\\:",
        "\\": "\\\\",
        "/": "\\/",
    }
)


def getLogger():
    return logging.getLogger("ror")


class Ror:
    def __init__(self, api_url=ROR_API_URL):
        self.api_url = api_url

    @classmethod
    def escapeQueryTerm(cls, term: str) -> str:
        return term.translate(ES_RESERVED_CHARS)

    def metadata(self, ror: str) -> dict:
        pid = doitip.model.Identifier.parse(ror, default_scheme="ror")
        url = f"{self.api_url}/{pid.curator}"
        headers = {"Accept": "application/json"}
        response = requests.get(url, headers=headers)
        if response.status_code not in [
            200,
        ]:
            raise KeyError(f"ROR {ror} not found.")
        return response.json()

    def searchByOrganization(self, query: str) -> list[str]:
        url = f"{self.api_url}/organizations"
        params = {"query": Ror.escapeQueryTerm(query)}
        headers = {"Accept": "application/json"}
        response = requests.get(url, headers=headers, params=params)
        if response.status_code not in [
            200,
        ]:
            raise ValueError(
                f"Error when querying ROR service: {response.reason} ({response.status_code})"
            )
        results = response.json()
        # records = []
        # for result in results.get("items", []):
        #    record = {
        #        "pid": result.get("id"),
        #        "name": "",
        #        "acronym": "",
        #    }
        return results
