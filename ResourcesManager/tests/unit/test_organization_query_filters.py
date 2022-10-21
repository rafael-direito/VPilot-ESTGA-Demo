# -*- coding: utf-8 -*-
# @Author: Rafael Direito
# @Date:   2022-10-21 09:58:55
# @Last Modified by:   Rafael Direito
# @Last Modified time: 2022-10-21 11:25:32

# general imports
import pytest

# custom imports
from tests.configure_test_db import engine
from database.database import Base
from routers.aux import GetOrganizationFilters
from routers.aux import parse_organization_query_filters


# Create the DB before each test and delete it afterwards
@pytest.fixture(autouse=True)
def test_db():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


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
