# -*- coding: utf-8 -*-
# @Author: Rafael Direito
# @Date:   2022-10-21 09:58:55
# @Last Modified by:   Rafael Direito
# @Last Modified time: 2022-10-29 13:21:38

# general imports
import pytest
from fastapi.encoders import jsonable_encoder

# custom imports
from routers.aux import filter_organization_fields
import schemas.tmf632_party_mgmt as TMF632Schemas
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
def test_query_filtering_parsing():

    # Prepare Test
    organization = TMF632Schemas.Organization(
        id=1,
        tradingName="XXX",
        name="XXX's Testbed",
        organizationType="Testbed",
        existsDuring=TMF632Schemas.TimePeriod(
            startDateTime="2015-10-22T08:31:52.026Z",
            endDateTime="2016-10-22T08:31:52.026Z",
        ),
        status="validated"
    )

    fields = ['name', 'tradingName', 'status']

    # Test

    filtered_organization1 = filter_organization_fields(
        fields,
        jsonable_encoder(organization)
    )

    filtered_organization2 = filter_organization_fields(
        None,
        jsonable_encoder(organization)
    )

    assert filtered_organization1.get("name") == "XXX's Testbed"
    assert filtered_organization1.get("tradingName") == "XXX"
    assert filtered_organization1.get("status") == "validated"
    assert filtered_organization1.get("organizationType") is None
    assert filtered_organization1.get("existsDuring") is None

    assert filtered_organization2.get("name") == "XXX's Testbed"
    assert filtered_organization2.get("tradingName") == "XXX"
    assert filtered_organization2.get("organizationType") == "Testbed"
    assert filtered_organization2.get("status") == "validated"
