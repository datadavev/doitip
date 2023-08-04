import json
import sys
import click
import requests

import doitoy.model

DOI_URL = "https://doi.org"


@click.group()
def main():
    return 0

@main.command()
def resolve():
    pass


@main.command()
@click.argument("doi")
def ra(doi: str):
    pid = doitoy.model.Identifier.parse(doi, default_scheme="doi")
    if pid.scheme != "doi":
        raise ValueError(f"Identifier is not a DOI string: '{doi}'")
    url = f"{DOI_URL}/doiRA/{pid.curator}"
    headers = {"Accept": "application/json"}
    response = requests.get(url, headers=headers)
    print(json.dumps(response.json(), indent=2))


@main.command()
@click.argument("doi")
def info(doi):
    pid = doitoy.model.Identifier.parse(doi, default_scheme="doi")
    if pid.scheme != "doi":
        raise ValueError(f"Identifier is not a DOI string: '{doi}'")
    url = f"{DOI_URL}/api/handles/{pid.curator}/{pid.value}"
    headers = {"Accept": "application/json"}
    response = requests.get(url, headers=headers)
    print(json.dumps(response.json(), indent=2))


if __name__ == "__main__":
    sys.exit(main())