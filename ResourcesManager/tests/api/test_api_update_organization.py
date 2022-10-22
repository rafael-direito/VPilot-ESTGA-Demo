# -*- coding: utf-8 -*-
# @Author: Rafael Direito
# @Date:   2022-10-17 21:13:44
# @Last Modified by:   Rafael Direito
# @Last Modified time: 2022-10-22 14:39:20

# general imports
import pytest

# custom imports
from tests.configure_test_db import engine
from tests.configure_test_db import test_client
from database.database import Base
from tests.configure_test_db import override_get_db
from schemas import tmf632_party_mgmt as TMF632Schemas
from database.crud import crud


# Create the DB before each test and delete it afterwards
@pytest.fixture(autouse=True)
def test_db():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


# Tests
def test_correct_organization_update():

    database = next(override_get_db())

    organization = TMF632Schemas.OrganizationCreate(
        tradingName="ITAv",
    )

    db_organization = crud.create_organization(
        db=database,
        organization=organization
    )

    response = test_client.patch(
        f"/organization/{db_organization.id}",
        json={
            "tradingName": "ITAv",
            "isHeadOffice": True,
            "isLegalEntity": True,
            "name": "ITAv's Testbed",
            "organizationType": "Testbed",
            "existsDuring": {
                "startDateTime": "2015-10-22T08:31:52.026Z"
            },
            "status": "validated",
            "partyCharacteristic": [
                {
                    "name": "ci_cd_agent_url",
                    "valueType": "URL",
                    "value": "http://192.168.1.200:8080",
                },
                {
                    "name": "ci_cd_agent_username",
                    "valueType": "str",
                    "value": "admin",
                }
            ],
        }
    )

    # Befor the Update
    assert db_organization.name is None
    assert db_organization.organizationType is None
    assert db_organization.existsDuring is None
    # After the Update
    assert response.status_code == 200
    assert response.json()['name'] == "ITAv's Testbed"
    assert response.json()['tradingName'] == "ITAv"
    assert response.json()['isHeadOffice']
    assert response.json()['isLegalEntity']
    assert response.json()['organizationType'] == "Testbed"
    assert response.json()['status'] == "validated"
    assert "2015-10-22T08:31:52.026"\
        in response.json()['existsDuring']["startDateTime"]
    assert response.json()['partyCharacteristic'][0]["name"]\
        == "ci_cd_agent_url"
    assert response.json()['partyCharacteristic'][0]["valueType"]\
        == "URL"
    assert response.json()['partyCharacteristic'][0]["value"]\
        == "http://192.168.1.200:8080"
    assert response.json()['partyCharacteristic'][1]["name"]\
        == "ci_cd_agent_username"
    assert response.json()['partyCharacteristic'][1]["valueType"]\
        == "str"
    assert response.json()['partyCharacteristic'][1]["value"]\
        == "admin"


def test_incorrect_organization_update():
    resp = test_client.patch(
        "/organization/999",
        json={
            "tradingName": "ITAv",
            "isHeadOffice": True,
            "isLegalEntity": True,
            "name": "ITAv's Testbed",
            "organizationType": "Testbed",
        }
    )

    assert resp.status_code == 400
    assert resp.json()['code'] == 400
    assert "Organization with id=999 doesn't exist" in resp.json()['reason']
