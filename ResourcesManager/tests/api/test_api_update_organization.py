# -*- coding: utf-8 -*-
# @Author: Rafael Direito
# @Date:   2022-10-17 21:13:44
# @Last Modified by:   Rafael Direito
# @Last Modified time: 2022-10-29 11:12:29

# general imports
import pytest

# custom imports
from database.crud import crud
import schemas.tmf632_party_mgmt as TMF632Schemas
from tests.configure_test_idp import (
    inject_admin_user,
    setup_test_idp,
    MockOIDCUser
)
from aux.constants import (
    IDP_TESTBED_ADMIN_USER,
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
def test_correct_organization_update_by_global_admin():

    # Prepare Test

    # Make request using a VPilot Admin and Testbed Admin Role
    inject_admin_user()

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
    print(response.json())
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


def test_incorrect_organization_update_by_global_admin():

    # Prepare Test

    # Make request using a VPilot Admin and Testbed Admin Role
    inject_admin_user()

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


def test_correct_organization_update_by_authorized_testbed_admin():

    # Prepare Test

    # Make request using a VPilot Admin and Testbed Admin Role
    # Prepare Mocked OIDC User
    user_id = "1111-1111-1111-1111"
    MockOIDCUser().inject_mocked_oidc_user(
        id=user_id,
        username="testbed-admin",
        roles=[IDP_TESTBED_ADMIN_USER]
    )

    database = next(override_get_db())

    organization = TMF632Schemas.OrganizationCreate(
        tradingName="ITAv",
    )

    db_organization = crud.create_organization(
        db=database,
        organization=organization
    )

    crud.create_authorized_user(
        db=database,
        user_id=user_id,
        organization_id=db_organization.id
    )

    response = test_client.patch(
        f"/organization/{db_organization.id}",
        json={
            "tradingName": "ITAv",
            "isHeadOffice": True,
            "isLegalEntity": True,
            "name": "ITAv's Testbed",
            "organizationType": "Testbed",
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


def test_correct_organization_update_by_unauthorized_testbed_admin():

    # Prepare Test

    # Make request using a VPilot Admin and Testbed Admin Role
    # Prepare Mocked OIDC User
    user_id = "1111-1111-1111-1111"
    MockOIDCUser().inject_mocked_oidc_user(
        id=user_id,
        username="testbed-admin",
        roles=[IDP_TESTBED_ADMIN_USER]
    )

    database = next(override_get_db())

    organization = TMF632Schemas.OrganizationCreate(
        tradingName="ITAv",
    )

    db_organization = crud.create_organization(
        db=database,
        organization=organization
    )

    crud.create_authorized_user(
        db=database,
        user_id="2222-2222-2222-2222",
        organization_id=db_organization.id
    )

    response = test_client.patch(
        f"/organization/{db_organization.id}",
        json={
            "tradingName": "ITAv",
            "isHeadOffice": True,
            "isLegalEntity": True,
            "name": "ITAv's Testbed",
            "organizationType": "Testbed",
        }
    )

    db_organization_after_update = crud.get_organization_by_id(
        db=database,
        id=db_organization.id
    )

    # Before the Update
    assert db_organization.name is None
    assert db_organization.organizationType is None
    assert db_organization.existsDuring is None
    # After the Update
    assert response.status_code == 403
    assert response.json()['code'] == 403
    assert response.json()['reason'] == 'User not authorized to access data '\
        f'related with organization {db_organization.id}'
    assert db_organization_after_update.name is None
    assert db_organization_after_update.organizationType is None
    assert db_organization_after_update.existsDuring is None
