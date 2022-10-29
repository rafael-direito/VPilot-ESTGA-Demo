# -*- coding: utf-8 -*-
# @Author: Rafael Direito
# @Date:   2022-10-21 09:58:55
# @Last Modified by:   Rafael Direito
# @Last Modified time: 2022-10-29 10:35:02

# general imports
import pytest

# custom imports
from routers.aux import (
    GetOrganizationFilters,
    parse_organization_query_filters
)
from tests.configure_test_idp import (
    setup_test_idp,
)


def import_modules():
    # additional custom imports
    from tests.configure_test_db import (
        engine as imported_engine,
        test_client as imported_test_client,
        override_get_db as imported_override_get_db
    )
    from database.database import Base as imported_base
    global engine
    engine = imported_engine
    global Base
    Base = imported_base
    global test_client
    test_client = imported_test_client
    global override_get_db
    override_get_db = imported_override_get_db


# Create the DB and IDP before each test and delete it afterwards
@pytest.fixture(autouse=True)
def setup(monkeypatch, mocker):
    # Setup Test IDP.
    # This is required before loading the other modules
    setup_test_idp(monkeypatch, mocker)
    import_modules()
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


# Tests
def test_organization_fields_filtering():
    # Prepare Test

    organization_filters_1 = GetOrganizationFilters(
        href="http://example.org",
        isHeadOffice=True,
        isLegalEntity=True,
        name="XXX",
        organizationType="Testbed"
    )

    # Test

    results1 = parse_organization_query_filters(organization_filters_1)

    assert results1.get("href") == "http://example.org"
    assert results1.get("isHeadOffice")
    assert results1.get("isLegalEntity")
    assert results1.get("name") == "XXX"
    assert results1.get("organizationType") == "Testbed"
    assert results1.get("tradingName") is None
    assert results1.get("existDuring") is None
