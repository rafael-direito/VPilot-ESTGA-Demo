# -*- coding: utf-8 -*-
# @Author: Rafael Direito
# @Date:   2022-10-17 21:13:44
# @Last Modified by:   Rafael Direito
# @Last Modified time: 2022-10-21 16:54:27

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
def test_simple_organization_get():

    # Prepare Test
    database = next(override_get_db())

    organization1 = TMF632Schemas.OrganizationCreate(
        tradingName="XXX",
        name="XXX's Testbed",
        organizationType="Testbed",
    )

    result = crud.create_organization(
        db=database,
        organization=organization1
    )

    response = test_client.get(
        f"/organization/{result.id}"
    )

    assert response.status_code == 200
    assert response.json()['name'] == "XXX's Testbed"
    assert response.json()['tradingName'] == "XXX"
    assert response.json()['organizationType'] == "Testbed"


def test_complex_organization_get():

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
        partyCharacteristic=[
            TMF632Schemas.Characteristic(
                name="ci_cd_agent_url",
                value="http://192.168.1.200:8080/",
                valueType="URL",
            ),
            TMF632Schemas.Characteristic(
                name="ci_cd_agent_username",
                value="admin",
                valueType="str",
            )
        ]
    )

    result = crud.create_organization(
        db=database,
        organization=organization
    )

    response = test_client.get(
        f"/organization/{result.id}"
    )

    # Prepare Expected Outputs
    expectedStartDateTime = datetime.datetime(2015, 10, 22, 8, 31, 52, 26000)
    expectedEndDateTime = datetime.datetime(2016, 10, 22, 8, 31, 52, 26000)

    obtainedStartDateTime = datetime.datetime.strptime(
        response.json()['existsDuring']["startDateTime"],
        '%Y-%m-%dT%H:%M:%S.%f'
    )
    obtainedEndDateTime = datetime.datetime.strptime(
        response.json()['existsDuring']["endDateTime"],
        '%Y-%m-%dT%H:%M:%S.%f'
    )

    # Test

    assert response.status_code == 200
    assert response.json()['name'] == "XXX's Testbed"
    assert response.json()['tradingName'] == "XXX"
    assert obtainedStartDateTime == expectedStartDateTime
    assert obtainedEndDateTime == expectedEndDateTime
    assert response.json()['partyCharacteristic'][0]["name"]\
        == "ci_cd_agent_url"
    assert response.json()['partyCharacteristic'][0]["valueType"]\
        == "URL"
    assert response.json()['partyCharacteristic'][0]["value"]\
        == "http://192.168.1.200:8080/"
    assert response.json()['partyCharacteristic'][1]["name"]\
        == "ci_cd_agent_username"
    assert response.json()['partyCharacteristic'][1]["valueType"]\
        == "str"
    assert response.json()['partyCharacteristic'][1]["value"]\
        == "admin"


def test_all_fields_in_organization_get():

    # Prepare Test
    database = next(override_get_db())

    organization = TMF632Schemas.OrganizationCreate(
        tradingName="XXX",
    )

    result = crud.create_organization(
        db=database,
        organization=organization
    )

    response = test_client.get(
        f"/organization/{result.id}"
    )

    assert response.status_code == 200
    assert response.json()['tradingName'] == "XXX"
    assert response.json()['name'] is None
    assert response.json()['contactMedium'] == []
    assert response.json()['creditRating'] == []
    assert response.json()['externalReference'] == []
    assert response.json()['organizationChildRelationship'] == []
    assert response.json()['organizationIdentification'] == []
    assert response.json()['otherName'] == []
    assert response.json()['partyCharacteristic'] == []
    assert response.json()['relatedParty'] == []
    assert response.json()['taxExemptionCertificate'] == []


def test_get_nonexistent_organization_from_database():

    # Test
    response = test_client.get(
        "/organization/1"
    )
    assert response.status_code == 200
    assert response.json() == {}


def test_invalid_get_organization_from_database():

    # Test
    response = test_client.get(
        "/organization/my_str"
    )
    assert response.status_code == 400
    assert "Error" in response.json()['reason']
    assert "payload_location=path/id" in response.json()['reason']
    assert "value is not a valid integer" in response.json()['reason']
