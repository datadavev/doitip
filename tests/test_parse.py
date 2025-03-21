import re
import pytest
import doitip.model

test_re = (
    ("doi:10.12345/some/stuff", None, ("doi", "10.12345", "some/stuff")),
    ("ark:/12345/some/stuff", None, ("ark", "12345", "some/stuff")),
    ("doi:", None, ("doi", None, None)),
    ("", None, (None, None, None)),
    ("", "doi", ("doi", None, None)),
    ("10.12345/foo/bar", None, (None, "10.12345", "foo/bar")),
    ("10.12345/foo/bar", "doi", ("doi", "10.12345", "foo/bar")),
)


@pytest.mark.parametrize("guid,default_scheme,expected", test_re)
def test_parse(guid, default_scheme, expected):
    match = re.fullmatch(doitip.model.Identifier.pattern, guid)
    if guid == "":
        assert match.group("scheme") is None
    else:
        assert match.group("scheme") in [expected[0], None]
        assert match.group("curator") in [expected[1], ""]
        assert match.group("value") in [expected[2], ""]


@pytest.mark.parametrize("guid,default_scheme,expected", test_re)
def test_identifier_parse(guid, default_scheme, expected):
    pid = doitip.model.Identifier.parse(guid, default_scheme=default_scheme)
    assert pid.scheme == expected[0]
    assert pid.curator == expected[1]
    assert pid.value == expected[2]


test_str = (
    ("doi:12345/foo?bar", "doi", "doi:12345/foo?bar"),
    ("12345/foo?bar", "doi", "doi:12345/foo?bar"),
    (" 12345/foo?bar ", "doi", "doi:12345/foo?bar"),
)


@pytest.mark.parametrize("guid,default_scheme,expected", test_str)
def test_identifier_parse2(guid, default_scheme, expected):
    pid = doitip.model.Identifier.parse(guid, default_scheme=default_scheme)
    assert str(pid) == expected
