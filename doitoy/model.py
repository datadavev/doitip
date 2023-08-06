import dataclasses
import re
import typing


@dataclasses.dataclass
class Identifier:
    # identifier composed of <scheme> + ":" [+ <curator> [+ "/" + <value>]]
    pattern = re.compile(
        r"^((?P<scheme>.*)\:\/?)?(?P<curator>[\w\.]*)?(\/?(?P<value>.*)?)"
    )
    default_scheme: typing.Optional[str] = None
    scheme: typing.Optional[str] = None
    curator: typing.Optional[str] = None
    value: typing.Optional[str] = None

    def __str__(self) -> str:
        s = f"{self.scheme}:" if not None else ""
        v = f"/{self.value}" if not None else ""
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
        if scheme is None or scheme == "":
            scheme = default_scheme
        if curator == "":
            curator = None
        if value == "":
            value = None
        return Identifier(scheme=scheme, curator=curator, value=value)
