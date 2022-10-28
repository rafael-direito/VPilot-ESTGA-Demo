# -*- coding: utf-8 -*-
# @Author: Rafael Direito
# @Date:   2022-10-17 21:13:44
# @Last Modified by:   Rafael Direito
# @Last Modified time: 2022-10-28 21:42:55

# general imports
import pytest

# custom imports
from tests.configure_test_idp import (
    setup_test_idp,
    inject_admin_user,
    MockOIDCUser
)
from aux.constants import (
    IDP_ADMIN_USER,
    IDP_TESTBED_ADMIN_USER,
)


def import_modules():
    # additional custom imports
    from tests.configure_test_db import engine as imported_engine
    from tests.configure_test_db import test_client as imported_test_client
    from database.database import Base as imported_base
    global engine
    engine = imported_engine
    global Base
    Base = imported_base
    global test_client
    test_client = imported_test_client


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
def test_correct_organization_post():

    # Make request using a VPilot Admin
    inject_admin_user()

    response = test_client.post(
        "/organization/",
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

    print(response.json())
    assert response.status_code == 201
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


def test_incorrect_organization_post():

    # Make request using a VPilot Admin
    inject_admin_user()

    response = test_client.post(
        "/organization/",
        json={
            "tradingName": "ITAv",
            "isHeadOffice": True,
            "isLegalEntity": True,
            "name": "ITAv's Testbed",
            "organizationType": "Testbed",
            "existsDuring": {
                "startDateTime": "This is wrong"
            },
            "status": "This is also Wrong"
        }
    )

    assert response.status_code == 400
    assert response.json()['code'] == 400
    assert "Error" in response.json()['reason']
    assert "body/existsDuring/startDateTime" and "datetime"\
        in response.json()['reason']
    assert "body/status" and "validated" and "initialized" and "closed" \
        in response.json()['reason']


def test_unauthorized_organization_post():

    # Prepare Mocked OIDC User
    MockOIDCUser().inject_mocked_oidc_user(
        id="1111-1111-1111-1111",
        username="testbed-admin",
        roles=[IDP_TESTBED_ADMIN_USER]
    )

    response = test_client.post(
        "/organization/",
        json={
            "tradingName": "ITAv",
        }
    )

    assert response.status_code == 403
    assert response.json()['code'] == 403
    assert f'Role "{IDP_ADMIN_USER}" is required to perform this '\
        'action' in response.json()['reason']
