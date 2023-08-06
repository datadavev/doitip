import json
import sys
import click
import requests
import doitoy.model
import doitoy.doira

DOI_URL = "https://doi.org"


@click.group()
def main():
    return 0


def redirect_hook(r, *args, **kwargs):
    print(r.url)


@main.command()
@click.argument("doi")
def resolve(doi):
    """Resolve a DOI, showing the targets on the way."""
    pid = doitoy.model.Identifier.parse(doi, default_scheme="doi")
    if pid.scheme != "doi":
        raise ValueError(f"Identifier is not a DOI string: '{doi}'")
    if pid.curator is None:
        raise ValueError(f"Provided DOI has no DOI prefix: '{doi}'")
    url = f"{DOI_URL}/{doitoy.doira.identifier_as_doistr(pid)}"
    hooks = {
        "response": [
            redirect_hook,
        ]
    }
    response = requests.get(url, hooks=hooks, allow_redirects=True)
    print(f"Result: ({response.status_code}) {response.url}")


@main.command()
@click.argument("doi")
def ra(doi: str):
    """Show the RA for a DOI."""
    pid = doitoy.model.Identifier.parse(doi, default_scheme="doi")
    if pid.scheme != "doi":
        raise ValueError(f"Identifier is not a DOI string: '{doi}'")
    url = f"{DOI_URL}/doiRA/{doitoy.doira.identifier_as_doistr(pid)}"
    headers = {"Accept": "application/json"}
    response = requests.get(url, headers=headers)
    print(json.dumps(response.json(), indent=2))


@main.command()
@click.argument("doi")
def info(doi):
    """Show the registration info for a DOI."""
    pid = doitoy.model.Identifier.parse(doi, default_scheme="doi")
    if pid.scheme != "doi":
        raise ValueError(f"Identifier is not a DOI string: '{doi}'")
    url = f"{DOI_URL}/api/handles/{doitoy.doira.identifier_as_doistr(pid)}"
    headers = {"Accept": "application/json"}
    response = requests.get(url, headers=headers)
    print(json.dumps(response.json(), indent=2))


@main.command()
@click.argument("doi")
def meta(doi):
    """Try and retrieve registered metadata for doi."""
    pid = doitoy.model.Identifier.parse(doi, default_scheme="doi")
    if pid.scheme != "doi":
        raise ValueError(f"Identifier is not a DOI string: '{doi}'")
    ra = doitoy.doira.get_doi_ra(pid)
    metadata = ra.info(pid)
    print(json.dumps(metadata, indent=2))


@main.command()
@click.argument("ra_name")
def prefixes(ra_name):
    ra_name = ra_name.lower()
    ra = doitoy.doira.get_ra(ra_name)
    prefixes = ra.get_prefixes()
    print(json.dumps(prefixes, indent=2))


if __name__ == "__main__":
    sys.exit(main())
