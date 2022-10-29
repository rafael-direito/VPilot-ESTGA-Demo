# -*- coding: utf-8 -*-
# @Author: Rafael Direito
# @Date:   2022-10-17 21:13:44
# @Last Modified by:   Rafael Direito
# @Last Modified time: 2022-10-29 12:46:50

# general imports
import pytest
import datetime

# custom imports
from database.crud import crud
from database.models import models
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
def test_get_organization_from_database():

    # Prepare Test
    db_organization = crud.create_organization(
        db=next(override_get_db()),
        organization=TMF632Schemas.OrganizationCreate(
            tradingName="XXX",
            name="XXX's Testbed",
            organizationType="Testbed",
            existsDuring=TMF632Schemas.TimePeriod(
                startDateTime="2015-10-22T08:31:52.026Z",
                endDateTime="2016-10-22T08:31:52.026Z",
            ),
        )
    )
    # Expected Outputs
    startDateTime = datetime.datetime(2015, 10, 22, 8, 31, 52, 26000)
    endDateTime = datetime.datetime(2016, 10, 22, 8, 31, 52, 26000)

    # Test
    assert type(db_organization) == models.Organization
    assert db_organization.tradingName == "XXX"
    assert db_organization.name == "XXX's Testbed"
    assert db_organization.partyCharacteristicParsed == []
    assert db_organization.existsDuringParsed.startDateTime\
        .replace(tzinfo=None) == startDateTime
    assert db_organization.existsDuringParsed.endDateTime\
        .replace(tzinfo=None) == endDateTime


def test_get_nonexistent_organization_from_database():

    # Prepare Test
    retrieved_organization = crud.get_organization_by_id(
        db=next(override_get_db()),
        id=1
    )

    # Test
    assert retrieved_organization is None
