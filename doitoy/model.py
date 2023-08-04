import dataclasses
import re
import typing

# identifier composed of <scheme> + ":" [+ <curator> [+ "/" + <value>]]
IDENTIFIER_PATTERN = re.compile(
    r"^((?P<scheme>.*)\:\/?)?(?P<curator>[\w\.]*)?(\/?(?P<value>.*)?)"
)

SCHEME_PATTERN = re.compile("^(?P<scheme>.*):")

@dataclasses.dataclass
class Identifier:
    scheme: typing.Optional[str] = None
    curator: typing.Optional[str] = None
    value: typing.Optional[str] = None

    def __str__(self) -> str:
        s = f"{self.scheme}:" if not None else ''
        v = f"/{self.value}" if not None else ''
        if self.curator is None:
            return s
        return f"{s}{self.curator}{v}"

    @classmethod
    def parse(cls, identifier: str, default_scheme=None) -> 'Identifier':
        identifier = identifier.strip()
        match = re.fullmatch(IDENTIFIER_PATTERN, identifier)
        scheme = match.group("scheme")
        curator = match.group("curator")
        value = match.group("value")
        if scheme is None or scheme == '':
            scheme = default_scheme
        if curator == '':
            curator = None
        if value == '':
            value = None
        return Identifier(scheme=scheme, curator=curator, value=value)

