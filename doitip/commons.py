"""Methods for Datacite Commons."""

import dataclasses
import hashlib
import logging
import pathlib
import typing

import gql
import gql.transport.httpx

from . import model


def getLogger():
    return logging.getLogger("commons")


def createHashIdentifier(data: list[str]):
    h = hashlib.sha256()
    for d in data:
        if d is not None:
            h.update(d.encode("utf-8"))
    return f"_:sha256/{h.hexdigest()}"


@dataclasses.dataclass
class Entity:
    pid: str
    _type: str
    properties: dict[str, typing.Any]


@dataclasses.dataclass
class Edge:
    pid1: str
    pid2: str
    predicate: str
    properties: dict[str, typing.Any]


class Commons:
    """Implements mecanisms for interacting with the Datacite Commons graphql API."""

    def __init__(self):
        self.base_url = "https://api.datacite.org/graphql"
        self.qfolder = pathlib.Path(__file__).resolve().parent / "cqueries"
        self.client: gql.Client | None = None
        self._L = getLogger()

    def _getTransport(self) -> gql.transport.httpx.HTTPXTransport:
        _L = getLogger()
        headers = {}
        return gql.transport.httpx.HTTPXTransport(url=self.base_url, headers=headers)

    def getClient(self, refresh: bool = False) -> gql.Client:
        """Get a client for interacting with the Graphql server.

        The client is configured with a token and group_id if provided. The
        token and group_id are needed for all operations except the `groups`
        command.
        """
        if self.client is None or refresh:
            self.client = gql.Client(
                transport=self._getTransport(),
                fetch_schema_from_transport=False,
            )
        return self.client

    def getRelated(self, doi: str):
        """Yields an entity identified by doi and relations to entity."""
        qname = "only_related.graphql"
        qtext = open(self.qfolder / qname, "r").read()
        query = gql.gql(qtext)
        params = {"id": doi}
        client = self.getClient()
        res = client.execute(query, variable_values=params)
        res = res.get("work", {})
        self._L.debug("res: %s", res)
        _type = res.get("type", res.get("__typename"))
        _properties = {}
        _properties["title"] = []
        for _title in res.get("titles", []):
            _properties["title"].append(_title)
        _properties["url"] = res.get("url", None)
        _properties["geoLocations"] = res.get("geoLocations", [])
        entity = Entity(
            pid=doi,
            _type=_type,
            properties=_properties,
        )
        yield entity

        creators = res.get("creators", [])
        for creator in creators:
            _family_name = creator.get("familyName", None)
            _given_name = creator.get("givenName", None)
            if _family_name is None and _given_name is None:
                _name = creator.get("name", None)
            else:
                if _given_name is None:
                    _name = _family_name
                else:
                    _name = f"{_family_name}, {_given_name}"
            _id = creator.get("id", None)
            if _id is not None:
                _id = str(model.infer_identifier(_id))
                # if "-" in _id and not _id.lower().startswith("orcid:"):
                #    _id = f"orcid:{_id}"
            else:
                # _id = createHashIdentifier([doi, _name])
                _id = f"_creator:{_name.replace(' ', '')}"
            _edge = Edge(
                pid1=doi,
                pid2=_id,
                predicate="hasCreator",
                properties={
                    "name": _name,
                },
            )
            yield _edge
            for affiliation in creator.get("affiliation", []):
                aid = affiliation.get("id", None)
                name = affiliation.get("name", None)
                if aid is not None:
                    aid = str(model.infer_identifier(aid))
                else:
                    # aid = createHashIdentifier([_id, name])
                    aid = f"_affiliation:{name.replace(' ', '_')}"
                yield Edge(
                    pid1=_id,
                    pid2=aid,
                    predicate="hasAffiliation",
                    properties={"name": name},
                )
        # Yield the creator edges and the creator association edges
        related = res.get("allRelated", {}).get("nodes", [])
        for rel in related:
            _id = rel.get("id", None)
            if _id is not None:
                _id = str(model.infer_identifier(_id))
                _type = rel.get("type", rel.get("__typename"))
                yield Edge(pid1=doi, pid2=_id, predicate="related", properties={})

    def graphRelated(
        self, doi: str, max_depth=1, cdepth: int = 1, visited: list[str] = []
    ):
        """Follows related items to max depth. Breadth first."""
        self._L.debug("DOI = %s", doi)
        res: list[Edge] = []
        visited.append(doi)
        for _item in self.getRelated(doi):
            if isinstance(_item, Entity):
                yield _item
                continue
            if _item.pid2 not in visited:
                yield _item
                res.append(_item)
        if cdepth >= max_depth:
            return
        cdepth += 1
        for item in res:
            if item.pid2.startswith("doi"):
                yield from self.graphRelated(
                    item.pid2, max_depth=max_depth, cdepth=cdepth
                )
