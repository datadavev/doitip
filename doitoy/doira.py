import typing
import requests
import doitoy.model


def identifier_as_doistr(pid: doitoy.model.Identifier) -> str:
    if pid.curator is None:
        raise ValueError(f"Provided DOI has no DOI prefix: '{pid}'")
    return f"{pid.curator}/{pid.value if not None else ''}"


class DoiRA:
    def __init__(self, name: str):
        self.name = name

    def _get_response(self, response) -> typing.Dict:
        err_msg = None
        if response.status_code == 200:
            try:
                return response.json()
            except Exception as e:
                err_msg = str(e)
        return {
            "status": response.status_code,
            "message": err_msg if not None else response.text,
        }

    def get_prefixes(self):
        raise NotImplementedError

    def get_handle_info(self, doi: doitoy.model.Identifier):
        url = f"https://doi.org/api/handles/{identifier_as_doistr(doi)}"
        headers = {"Accept": "application/json"}
        response = requests.get(url, headers=headers)
        return self._get_response(response)

    def get_publisher_info(self, doi: doitoy.model.Identifier):
        raise NotImplementedError

    def get_pid_metadata(self, doi: doitoy.model.Identifier):
        raise NotImplementedError

    def info(self, doi: doitoy.model.Identifier):
        return {
            "handle": self.get_handle_info(doi),
            "prefix": self.get_publisher_info(doi),
            "metadata": self.get_pid_metadata(doi),
        }


class CrossrefDoiRA(DoiRA):
    def __init__(self):
        super().__init__("Crossref")

    def get_prefixes(self):
        params = {"prefix": "all"}
        url = "http://doi.crossref.org/getPrefixPublisher/"
        headers = {"Accept": "application/json"}
        response = requests.get(url, params=params, headers=headers)
        return self._get_response(response)

    def get_publisher_info(self, doi: doitoy.model.Identifier):
        # https://crossref.gitlab.io/knowledge_base/docs/services/get-prefix-publisher/
        # see also:
        # https://api.crossref.org/swagger-ui/index.html#/Prefixes/get_prefixes__prefix_
        url = "https://doi.crossref.org/getPrefixPublisher/"
        params = {"prefix": doi.curator}
        headers = {"Accept": "application/json"}
        response = requests.get(url, params=params, headers=headers)
        return self._get_response(response)

    def get_pid_metadata(self, doi: doitoy.model.Identifier):
        # https://api.crossref.org/swagger-ui/index.html#/Works/get_works
        url = f"https://api.crossref.org/works/{identifier_as_doistr(doi)}"
        headers = {"Accept": "application/json"}
        response = requests.get(url, headers=headers)
        return self._get_response(response)


class DataciteDoiRA(DoiRA):
    def __init__(self):
        super().__init__("Datacite")

    def get_prefixes(self):
        # https://support.datacite.org/reference/get_prefixes
        headers = {"Accept": "application/json"}
        url = "https://api.datacite.org/prefixes"
        response = requests.get(url, headers=headers)
        return self._get_response(response)

    def get_publisher_info(self, doi: doitoy.model.Identifier):
        return {
            "note": "Datacite publisher info is in metadata record.",
        }

    def get_pid_metadata(self, doi: doitoy.model.Identifier):
        # https://support.datacite.org/reference/get_dois-id
        url = f"https://api.datacite.org/dois/{identifier_as_doistr(doi)}"
        headers = {"Accept": "application/json"}
        response = requests.get(url, headers=headers)
        return self._get_response(response)


def get_ra(ra_name: str) -> DoiRA:
    handlers = {
        "datacite": DataciteDoiRA,
        "crossref": CrossrefDoiRA,
    }
    return handlers[ra_name]()


def get_doi_ra(doi: doitoy.model.Identifier) -> DoiRA:
    url = f"https://doi.org/doiRA/{identifier_as_doistr(doi)}"
    headers = {"Accept": "application/json"}
    ra_info = requests.get(url, headers=headers).json()
    ra_name = ra_info[0].get("RA", "").lower()
    return get_ra(ra_name)
