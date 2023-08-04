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

