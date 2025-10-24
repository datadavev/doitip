import dataclasses
import re
import typing

COMMON_PIDS = {
    "doi": re.compile(r"(?P<doi>10\.[0-9]{3,8}\/\S.*)", flags=re.I),
    "ark": re.compile(r"(?P<ark>[0-9a-z]{5,10}\/\S*)", flags=re.I),
    "geo": re.compile(r"(?P<geo>[0-9]{5,8})", flags=re.I),
    "orcid": re.compile(
        r"(?P<orcid>[0-9a-z]{4}-[0-9a-z]{4}-[0-9a-z]{4}-[0-9a-z]{4})", flags=re.I
    ),
    "ror": re.compile(r"(?P<ror>0[a-z|0-9]{6}[0-9]{2})", flags=re.I),
}


def splitUrl(url: str) -> dict:
    pattern = re.compile(
        r"(?P<protocol>^(https?):\/\/)?(?P<domain>(((?!-)[A-Za-z0-9-]{1,63}(?<!-)\.)+[A-Za-z0-9-]{1,63}))\/(?P<pid>.*)"
    )
    result = {"original": url, "protocol": None, "domain": None, "pid": None}
    match = re.fullmatch(pattern, url)
    if match is not None:
        result["protocol"] = match.group("protocol")
        result["domain"] = match.group("domain")
        result["pid"] = match.group("pid")
    return result


@dataclasses.dataclass
class Identifier:
    # identifier composed of <scheme> + ":" [+ <curator> [+ "/" + <value>]]
    pattern = re.compile(
        r"^((?P<scheme>.*)\:\/?)?(?P<curator>[\w\.\-]*)?(\/?(?P<value>.*)?)"
    )
    default_scheme: typing.Optional[str] = None
    scheme: typing.Optional[str] = None
    curator: typing.Optional[str] = None
    value: typing.Optional[str] = None

    def __str__(self) -> str:
        s = f"{self.scheme}:" if self.scheme is not None else ""
        v = f"/{self.value}" if self.value is not None else ""
        if self.curator is None:
            return s
        return f"{s}{self.curator}{v}"

    def __eq__(self, b):
        return (
            b.scheme == self.scheme
            and b.curator == self.curator
            and b.value == self.value
        )

    @classmethod
    def parse(
        cls, identifier: str, default_scheme: typing.Optional[str] = None
    ) -> "Identifier":
        identifier = identifier.strip()
        match = re.fullmatch(Identifier.pattern, identifier)
        scheme = match.group("scheme")
        curator = match.group("curator")
        value = match.group("value")
        match scheme:
            case None | "":
                scheme = default_scheme
            case "doi.org":
                scheme = "doi"
            case "arks.org":
                scheme = "ark"
            case "ror.org" | "api.ror.org":
                scheme = "ror"

        if curator == "":
            curator = None
        if value == "":
            value = None
        return Identifier(scheme=scheme, curator=curator, value=value)


def infer_identifier(original: str) -> Identifier | None:
    source = original.strip()
    for k, v in COMMON_PIDS.items():
        match = re.fullmatch(v, source)
        if match is not None:
            return Identifier.parse(source, default_scheme=k)
    url_split = splitUrl(source)
    match url_split["domain"]:
        case "ror.org" | "api.ror.org":
            return Identifier.parse(url_split["pid"], default_scheme="ror")
        case "doi.org" | "commons.datacite.org" | "crossref.org":
            return Identifier.parse(url_split["pid"], default_scheme="doi")
        case "orcid.org":
            return Identifier.parse(url_split["pid"], default_scheme="orcid")
        case "n2t.net" | "arks.org":
            return Identifier.parse(url_split["pid"], default_scheme="ark")
    if url_split["protocol"] is not None and url_split["pid"] is not None:
        source = url_split["pid"]
    for k, v in COMMON_PIDS.items():
        match = re.fullmatch(v, source)
        if match is not None:
            return Identifier.parse(source, default_scheme=k)
    try:
        return Identifier.parse(source)
    except ValueError:
        pass
    return None
