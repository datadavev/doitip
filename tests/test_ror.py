import json
import pytest

import doitip.ror


test_search_cases = (("NCEAS", "foo"),)


@pytest.mark.parametrize("term,expected", test_search_cases)
def test_ror_search(term, expected):
    ror = doitip.ror.Ror()
    result = ror.searchByOrganization(term)
    print(json.dumps(result, indent=2))
