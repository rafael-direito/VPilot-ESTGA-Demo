# -*- coding: utf-8 -*-
# @Author: Rafael Direito
# @Date:   2022-10-17 21:13:44
# @Last Modified by:   Rafael Direito
# @Last Modified time: 2022-10-23 18:03:40

# general imports
import pytest
import datetime

# custom imports
from database.crud import crud
import schemas.tmf632_party_mgmt as TMF632Schemas
from tests.configure_test_db import override_get_db
from tests.configure_test_db import engine
from database.database import Base
from database.models import models


# Create the DB before each test and delete it afterwards
@pytest.fixture(autouse=True)
def test_db():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


# Tests
def test_get_organization_from_database():

    # Prepare Test
    database = next(override_get_db())

    organization = TMF632Schemas.OrganizationCreate(
        tradingName="XXX",
        name="XXX's Testbed",
        organizationType="Testbed",
        existsDuring=TMF632Schemas.TimePeriod(
            startDateTime="2015-10-22T08:31:52.026Z",
            endDateTime="2016-10-22T08:31:52.026Z",
        ),
    )

    result = crud.create_organization(
        db=database,
        organization=organization
    )

    # Expected Outputs
    startDateTime = datetime.datetime(2015, 10, 22, 8, 31, 52, 26000)
    endDateTime = datetime.datetime(2016, 10, 22, 8, 31, 52, 26000)

    # Test

    retrieved_organization = crud.get_organization_by_id(database, result.id)

    party_characteristics = crud.get_party_characteristics_by_organization_id(
        db=database,
        organization_id=retrieved_organization.id
    )

    exists_during = crud.get_time_period_by_id(
            db=database,
            id=retrieved_organization.existsDuring
    )

    assert type(retrieved_organization) == models.Organization
    assert retrieved_organization.tradingName == "XXX"
    assert retrieved_organization.name == "XXX's Testbed"
    assert party_characteristics == []
    assert exists_during.startDateTime.replace(tzinfo=None) == startDateTime
    assert exists_during.endDateTime.replace(tzinfo=None) == endDateTime


def test_get_nonexistent_organization_from_database():

    # Prepare Test
    database = next(override_get_db())

    # Test

    retrieved_organization = crud.get_organization_by_id(database, 1)
    assert retrieved_organization is None
