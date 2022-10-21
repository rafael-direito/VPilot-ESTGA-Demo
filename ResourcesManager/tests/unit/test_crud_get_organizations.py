# -*- coding: utf-8 -*-
# @Author: Rafael Direito
# @Date:   2022-10-17 21:13:44
# @Last Modified by:   Rafael Direito
# @Last Modified time: 2022-10-21 11:50:46

# general imports
import pytest
import datetime

# custom imports
from database.crud import crud
import schemas.tmf632_party_mgmt as TMF632Schemas
from tests.configure_test_db import override_get_db
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
    assert all_organizations[0].creditRating == []
    assert all_organizations[0].externalReference == []
    assert all_organizations[0].organizationChildRelationship == []
    assert all_organizations[0].organizationIdentification == []
    assert all_organizations[0].otherName == []
    assert all_organizations[0].partyCharacteristic == []
    assert all_organizations[0].relatedParty == []
    assert all_organizations[0].taxExemptionCertificate == []


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
