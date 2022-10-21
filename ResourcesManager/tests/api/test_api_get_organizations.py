# -*- coding: utf-8 -*-
# @Author: Rafael Direito
# @Date:   2022-10-17 21:13:44
# @Last Modified by:   Rafael Direito
# @Last Modified time: 2022-10-21 11:50:37

# general imports
import pytest
import datetime

# custom imports
from database.crud import crud
import schemas.tmf632_party_mgmt as TMF632Schemas
from tests.configure_test_db import override_get_db
from tests.configure_test_db import engine
from tests.configure_test_db import test_client
from database.database import Base


# Create the DB before each test and delete it afterwards
@pytest.fixture(autouse=True)
def test_db():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


# Tests
def test_simple_organizations_get():

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

    response = test_client.get(
        "/organization/"
    )

    assert response.status_code == 200
    assert len(response.json()) == 2
    assert response.json()[0]['name'] == "XXX's Testbed"
    assert response.json()[0]['tradingName'] == "XXX"
    assert response.json()[1]['name'] == "YYY's Testbed"
    assert response.json()[1]['tradingName'] == "YYY"


def test_organizations_with_exist_during_get():

    # Prepare Test
    database = next(override_get_db())

    organization = TMF632Schemas.OrganizationCreate(
        tradingName="XXX",
        name="XXX's Testbed",
        organizationType="Testbed",
        existsDuring=TMF632Schemas.TimePeriod(
            startDateTime="2015-10-22T08:31:52.026Z",
            endDateTime="2016-10-22T08:31:52.026Z",
        )
    )

    crud.create_organization(
        db=database,
        organization=organization
    )

    response = test_client.get(
        "/organization/"
    )

    # Prepare Expected Outputs
    expectedStartDateTime = datetime.datetime(2015, 10, 22, 8, 31, 52, 26000)
    expectedEndDateTime = datetime.datetime(2016, 10, 22, 8, 31, 52, 26000)

    obtainedStartDateTime = datetime.datetime.strptime(
        response.json()[0]['existsDuring']["startDateTime"],
        '%Y-%m-%dT%H:%M:%S.%f'
    )
    obtainedEndDateTime = datetime.datetime.strptime(
        response.json()[0]['existsDuring']["endDateTime"],
        '%Y-%m-%dT%H:%M:%S.%f'
    )

    # Test

    assert response.status_code == 200
    assert len(response.json()) == 1
    assert response.json()[0]['name'] == "XXX's Testbed"
    assert response.json()[0]['tradingName'] == "XXX"
    assert obtainedStartDateTime == expectedStartDateTime
    assert obtainedEndDateTime == expectedEndDateTime


def test_all_fields_in_organizations_get():

    # Prepare Test
    database = next(override_get_db())

    organization = TMF632Schemas.OrganizationCreate(
        tradingName="XXX",
    )

    crud.create_organization(
        db=database,
        organization=organization
    )

    response = test_client.get(
        "/organization/"
    )

    assert response.status_code == 200
    assert len(response.json()) == 1
    assert response.json()[0]['tradingName'] == "XXX"
    assert response.json()[0]['name'] is None
    assert response.json()[0]['contactMedium'] == []
    assert response.json()[0]['creditRating'] == []
    assert response.json()[0]['externalReference'] == []
    assert response.json()[0]['organizationChildRelationship'] == []
    assert response.json()[0]['organizationIdentification'] == []
    assert response.json()[0]['otherName'] == []
    assert response.json()[0]['partyCharacteristic'] == []
    assert response.json()[0]['relatedParty'] == []
    assert response.json()[0]['taxExemptionCertificate'] == []


def test_get_filtered_organizations():

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

    response_organizations_1 = test_client.get(
        "/organization?tradingName=YYY"
    )

    response_organizations_2 = test_client.get(
        "/organization?organizationType=Testbed2"
    )

    response_organizations_3 = test_client.get(
        "/organization?jibberish=xxx&jjibberish2=yyy"
    )

    # Test

    assert response_organizations_1.status_code == 200
    assert len(response_organizations_1.json()) == 2
    assert response_organizations_1.json()[0]["tradingName"] == "YYY"
    assert response_organizations_1.json()[1]["tradingName"] == "YYY"
    assert response_organizations_1.json()[0]["name"] == "YYY's Testbed"
    assert response_organizations_1.json()[1]["name"] == "YYY's Testbed2"

    assert response_organizations_2.status_code == 200
    assert len(response_organizations_2.json()) == 2
    assert response_organizations_2.json()[0]["organizationType"] == "Testbed2"
    assert response_organizations_2.json()[1]["organizationType"] == "Testbed2"
    assert response_organizations_2.json()[0]["tradingName"] == "XXX"
    assert response_organizations_2.json()[1]["tradingName"] == "YYY"

    assert response_organizations_3.status_code == 200
    assert len(response_organizations_3.json()) == 4
    assert response_organizations_3.json()[0]["tradingName"] == "XXX"
    assert response_organizations_3.json()[0]["name"] == "XXX's Testbed"
    assert response_organizations_3.json()[0]["organizationType"] == "Testbed"
    assert response_organizations_3.json()[1]["tradingName"] == "XXX"
    assert response_organizations_3.json()[1]["name"] == "XXX's Testbed2"
    assert response_organizations_3.json()[1]["organizationType"] == "Testbed2"
    assert response_organizations_3.json()[2]["tradingName"] == "YYY"
    assert response_organizations_3.json()[2]["name"] == "YYY's Testbed"
    assert response_organizations_3.json()[2]["organizationType"] == "Testbed"
    assert response_organizations_3.json()[3]["tradingName"] == "YYY"
    assert response_organizations_3.json()[3]["name"] == "YYY's Testbed2"
    assert response_organizations_3.json()[3]["organizationType"] == "Testbed2"
