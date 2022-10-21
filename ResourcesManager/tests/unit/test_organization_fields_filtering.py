# -*- coding: utf-8 -*-
# @Author: Rafael Direito
# @Date:   2022-10-21 09:58:55
# @Last Modified by:   Rafael Direito
# @Last Modified time: 2022-10-21 10:06:57

# general imports
import pytest
from fastapi.encoders import jsonable_encoder

# custom imports
from tests.configure_test_db import engine
from database.database import Base
import schemas.tmf632_party_mgmt as TMF632Schemas
from routers.aux import filter_organization_fields


# Create the DB before each test and delete it afterwards
@pytest.fixture(autouse=True)
def test_db():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


def test_organization_fields_filtering():

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
