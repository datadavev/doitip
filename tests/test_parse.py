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


test_arbitrary_cases = (
    ("https://ror.org/04p8xrf95", "ror:04p8xrf95"),
    ("ror.org/04p8xrf95", "ror:04p8xrf95"),
    ("ror:04p8xrf95", "ror:04p8xrf95"),
    ("04p8xrf95", "ror:04p8xrf95"),
    ("https://doi.org/10.48321/D1F88S", "doi:10.48321/D1F88S"),
    ("doi.org/10.48321/D1F88S", "doi:10.48321/D1F88S"),
    ("https://doi.org/10.1007/s10393-016-1188-7", "doi:10.1007/s10393-016-1188-7"),
    ("10.1111/mec.16391", "doi:10.1111/mec.16391"),
    ("doi:10.1111/mec.16391", "doi:10.1111/mec.16391"),
    ("https://doi.org/10.1007/s10393-015-1071-y", "doi:10.1007/s10393-015-1071-y"),
    (
        "https://doi.org/10.1371/journal.pone.0023179",
        "doi:10.1371/journal.pone.0023179",
    ),
    (
        "https://doi.org/10.1371/journal.pone.0197710",
        "doi:10.1371/journal.pone.0197710",
    ),
    ("http://127.0.0.1/foo", "foo"),
    ("https://n2t.net/ark:12345/foozle", "ark:12345/foozle"),
    ("n2t.net/ark:12345/foozle", "ark:12345/foozle"),
    ("ark:12345/foozle", "ark:12345/foozle"),
    ("https://fake.XN--VERMGENSBERATUNG-PWB/foo", "foo"),
    ("10.48321/D1F88S", "doi:10.48321/D1F88S"),
    ("6094817", "geo:6094817"),
    ("geo:6094817", "geo:6094817"),
    ("https://geonames.org/6094817", "geo:6094817"),
    ("12345/foo", "ark:12345/foo"),
    ("https://orcid.org/0000-0002-6513-4996", "orcid:0000-0002-6513-4996"),
    ("0000-0002-6513-4996", "orcid:0000-0002-6513-4996"),
    ("orcid:0000-0002-6513-4996", "orcid:0000-0002-6513-4996"),
)


@pytest.mark.parametrize("original,expected", test_arbitrary_cases)
def test_arbitrary(original, expected):
    pid = doitip.model.infer_identifier(original)
    print(pid)
    assert str(pid) == str(expected)
