# -*- coding: utf-8 -*-
# @Author: Rafael Direito
# @Date:   2022-10-17 21:13:44
# @Last Modified by:   Rafael Direito
# @Last Modified time: 2022-10-19 23:29:37

# general imports
import pytest
import datetime

# custom imports
from database.crud import crud
import schemas.tmf632_party_mgmt as TMF632Schemas
from tests.configure_test_db import override_get_db
from tests.configure_test_db import engine
from database.database import Base


# Create the DB before each test and delete it afterwards
@pytest.fixture(autouse=True)
def test_db():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


# Tests
def test_get_simple_organizations_from_database():

    # Prepare Test
    database = next(override_get_db())

    organization1 = TMF632Schemas.OrganizationCreate(
        tradingName="XXX",
        name="XXX's Testbed",
        organizationType="Testbed"
    )
    organization2 = TMF632Schemas.OrganizationCreate(
        tradingName="YYY",
        name="YYY's Testbed",
        organizationType="Testbed"
    )

    crud.create_organization(
        db=database,
        organization=organization1
    )
    crud.create_organization(
        db=database,
        organization=organization2
    )

    # Test

    all_organizations = crud.get_all_organizations(database)
    assert len(all_organizations) == 2
    assert all_organizations[0].tradingName == "XXX"
    assert all_organizations[1].tradingName == "YYY"


def test_get_organizations_from_database_with_starts_during():

    # Prepare Test
    database = next(override_get_db())

    organization1 = TMF632Schemas.OrganizationCreate(
        tradingName="XXX",
        name="XXX's Testbed",
        organizationType="Testbed",
        existsDuring=TMF632Schemas.TimePeriod(
            startDateTime="2015-10-22T08:31:52.026Z",
            endDateTime="2016-10-22T08:31:52.026Z",
        ),
    )
    organization2 = TMF632Schemas.OrganizationCreate(
        tradingName="YYY",
        name="YYY's Testbed",
        organizationType="Testbed"
    )

    crud.create_organization(
        db=database,
        organization=organization1
    )
    crud.create_organization(
        db=database,
        organization=organization2
    )

    # Test

    all_organizations = crud.get_all_organizations(database)

    startDateTime = datetime.datetime(2015, 10, 22, 8, 31, 52, 26000)
    endDateTime = datetime.datetime(2016, 10, 22, 8, 31, 52, 26000)

    assert len(all_organizations) == 2
    assert all_organizations[0].existsDuring\
        .startDateTime.replace(tzinfo=None) == startDateTime
    assert all_organizations[0].existsDuring\
        .endDateTime.replace(tzinfo=None) == endDateTime
    assert all_organizations[1].existsDuring is None


def test_get_almost_empty_organizations_from_database():

    # Prepare Test
    database = next(override_get_db())

    organization = TMF632Schemas.OrganizationCreate(
        tradingName="XXX",
    )
    crud.create_organization(
        db=database,
        organization=organization
    )

    # Test

    all_organizations = crud.get_all_organizations(database)
    assert len(all_organizations) == 1
    assert all_organizations[0].contactMedium == []
    assert all_organizations[0].contactMedium == []
    assert all_organizations[0].contactMedium == []
    assert all_organizations[0].contactMedium == []
    assert all_organizations[0].contactMedium == []
    assert all_organizations[0].contactMedium == []
