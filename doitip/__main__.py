import json
import sys
import click
import requests
import requests_toolbelt
import doitip
import doitip.model
import doitip.doira

DOI_URL = "https://doi.org"
USER_AGENT = requests_toolbelt.user_agent("doitip", doitip.__version__)
REQUEST_TIMEOUT = 10.0


@click.group()
@click.version_option(USER_AGENT)
def main():
    return 0


def redirect_hook(r, *args, **kwargs):
    print(r.url)


@main.command()
@click.argument("doi")
@click.option(
    "-a",
    "--accept",
    default="*/*",
    help="Accept header value to use in resolve request.",
    show_default=True,
)
def resolve(doi, accept):
    """Resolve a DOI, showing the targets on the way."""
    pid = doitip.model.Identifier.parse(doi, default_scheme="doi")
    if pid.scheme != "doi":
        raise ValueError(f"Identifier is not a DOI string: '{doi}'")
    if pid.curator is None:
        raise ValueError(f"Provided DOI has no DOI prefix: '{doi}'")
    headers = {
        "Accept": accept,
        "User-Agent": USER_AGENT,
    }
    url = f"{DOI_URL}/{doitip.doira.identifier_as_doistr(pid)}"
    hooks = {
        "response": [
            redirect_hook,
        ]
    }
    result = []
    with requests.get(
        url, headers=headers, timeout=REQUEST_TIMEOUT, allow_redirects=True, stream=True, #hooks=hooks
    ) as resp:
        for r in resp.history:
            result.append({
                "url": r.url,
                "status": r.status_code,
                "elapsed_ms": (r.elapsed.microseconds / 1000.0)
            })
        result.append({
            "url": resp.url,
            "status": resp.status_code,
            "elapsed_ms": (resp.elapsed.microseconds / 1000.0)
        })
    print(json.dumps(result, indent=2))

@main.command()
@click.argument("doi")
def ra(doi: str):
    """Show the Regitration Agency for a DOI."""
    pid = doitip.model.Identifier.parse(doi, default_scheme="doi")
    if pid.scheme != "doi":
        raise ValueError(f"Identifier is not a DOI string: '{doi}'")
    url = f"{DOI_URL}/doiRA/{doitip.doira.identifier_as_doistr(pid)}"
    headers = {"Accept": "application/json"}
    response = requests.get(url, headers=headers)
    print(json.dumps(response.json(), indent=2))


@main.command()
@click.argument("doi")
def info(doi):
    """Show the registration info for a DOI."""
    pid = doitip.model.Identifier.parse(doi, default_scheme="doi")
    if pid.scheme != "doi":
        raise ValueError(f"Identifier is not a DOI string: '{doi}'")
    url = f"{DOI_URL}/api/handles/{doitip.doira.identifier_as_doistr(pid)}"
    headers = {"Accept": "application/json"}
    response = requests.get(url, headers=headers)
    print(json.dumps(response.json(), indent=2))


@main.command()
@click.argument("doi")
def meta(doi):
    """Try and retrieve registered metadata for doi."""
    pid = doitip.model.Identifier.parse(doi, default_scheme="doi")
    if pid.scheme != "doi":
        raise ValueError(f"Identifier is not a DOI string: '{doi}'")
    ra = doitip.doira.get_doi_ra(pid)
    metadata = ra.info(pid)
    print(json.dumps(metadata, indent=2))


@main.command()
@click.argument("ra_name")
def prefixes(ra_name):
    """List prefixes registered by a Registration Agency."""
    ra_name = ra_name.lower()
    ra = doitip.doira.get_ra(ra_name)
    prefixes = ra.get_prefixes()
    print(json.dumps(prefixes, indent=2))


@main.command()
def ras():
    """List Registration Agencies known to this tool."""
    _ras = doitip.doira.list_ras()
    print(json.dumps([str(_ra) for _ra in _ras], indent=2))


if __name__ == "__main__":
    sys.exit(main())
