# -*- coding: utf-8 -*-
# @Author: Rafael Direito
# @Date:   2022-10-17 21:13:44
# @Last Modified by:   Rafael Direito
# @Last Modified time: 2022-10-29 10:33:51

# general imports
import pytest
import datetime

# custom imports
from database.crud import crud
from routers.aux import (
    parse_organization_query_filters,
    GetOrganizationFilters
)
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

    all_exists_during = [
        crud.get_time_period_by_id(
            db=database,
            id=org.existsDuring
        )
        for org
        in all_organizations
    ]

    startDateTime = datetime.datetime(2015, 10, 22, 8, 31, 52, 26000)
    endDateTime = datetime.datetime(2016, 10, 22, 8, 31, 52, 26000)

    assert len(all_organizations) == 2
    assert all_exists_during[0].startDateTime\
        .replace(tzinfo=None) == startDateTime
    assert all_exists_during[0].endDateTime\
        .replace(tzinfo=None) == endDateTime
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

    all_party_characteristics = [
        crud.get_party_characteristics_by_organization_id(
            db=database,
            organization_id=org.id
        )
        for org
        in all_organizations
    ]

    assert len(all_organizations) == 1
    assert all_organizations[0].tradingName == "XXX"
    assert all_organizations[0].href is None
    assert not all_organizations[0].isHeadOffice
    assert not all_organizations[0].isLegalEntity == bool(False)
    assert all_organizations[0].name is None
    assert all_organizations[0].nameType is None
    assert all_organizations[0].existsDuring is None
    assert all_party_characteristics[0] == []


def test_get_filtered_organizations_from_database():

    # Prepare Test
    database = next(override_get_db())

    organization1 = TMF632Schemas.OrganizationCreate(
        tradingName="XXX",
        name="XXX's Testbed",
        organizationType="Testbed"
    )
    organization2 = TMF632Schemas.OrganizationCreate(
        tradingName="XXX",
        name="XXX's Testbed2",
        organizationType="Testbed2"
    )
    organization3 = TMF632Schemas.OrganizationCreate(
        tradingName="YYY",
        name="YYY's Testbed",
        organizationType="Testbed"
    )
    organization4 = TMF632Schemas.OrganizationCreate(
        tradingName="YYY",
        name="YYY's Testbed2",
        organizationType="Testbed2"
    )

    crud.create_organization(
        db=database,
        organization=organization1
    )
    crud.create_organization(
        db=database,
        organization=organization2
    )
    crud.create_organization(
        db=database,
        organization=organization3
    )
    crud.create_organization(
        db=database,
        organization=organization4
    )

    organization_filters_1 = GetOrganizationFilters(
        tradingName="YYY",
    )
    organization_filters_2 = GetOrganizationFilters(
        organizationType="Testbed2",
    )

    filtered_organizations_1 = crud.get_all_organizations(
        database,
        parse_organization_query_filters(organization_filters_1)
    )

    filtered_organizations_2 = crud.get_all_organizations(
        database,
        parse_organization_query_filters(organization_filters_2)
    )

    # Test

    assert len(filtered_organizations_1) == 2
    assert filtered_organizations_1[0].tradingName == "YYY"
    assert filtered_organizations_1[1].tradingName == "YYY"
    assert filtered_organizations_1[0].name == "YYY's Testbed"
    assert filtered_organizations_1[1].name == "YYY's Testbed2"

    assert len(filtered_organizations_2) == 2
    assert filtered_organizations_2[0].organizationType == "Testbed2"
    assert filtered_organizations_2[1].organizationType == "Testbed2"
    assert filtered_organizations_2[0].tradingName == "XXX"
    assert filtered_organizations_2[1].tradingName == "YYY"
