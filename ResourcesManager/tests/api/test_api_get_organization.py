# -*- coding: utf-8 -*-
# @Author: Rafael Direito
# @Date:   2022-10-17 21:13:44
# @Last Modified by:   Rafael Direito
# @Last Modified time: 2022-10-28 22:47:13

# general imports
import pytest
import datetime

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
def test_simple_organization_get_by_global_admin():

    # Prepare Test

    # Make request using a VPilot Admin and Testbed Admin Role
    inject_admin_user()

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


def test_complex_organization_get_by_global_admin():

    # Prepare Test

    # Make request using a VPilot Admin and Testbed Admin Role
    inject_admin_user()

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


def test_all_fields_in_organization_get_by_global_admin():

    # Prepare Test

    # Make request using a VPilot Admin and Testbed Admin Role
    inject_admin_user()

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


def test_get_nonexistent_organization_from_database_by_admin():

    # Make request using a VPilot Admin and Testbed Admin Role
    inject_admin_user()

    # Test
    response = test_client.get(
        "/organization/1"
    )
    assert response.status_code == 200
    assert response.json() == {}


def test_invalid_get_organization_from_database_by_global_admin():

    # Make request using a VPilot Admin and Testbed Admin Role
    inject_admin_user()

    # Test
    response = test_client.get(
        "/organization/my_str"
    )
    assert response.status_code == 400
    assert "Error" in response.json()['reason']
    assert "payload_location=path/id" in response.json()['reason']
    assert "value is not a valid integer" in response.json()['reason']


def test_simple_organization_get_by_testbed_admin():

    # Prepare Test

    # Prepare Mocked OIDC User
    user_id = "1111-1111-1111-1111"
    MockOIDCUser().inject_mocked_oidc_user(
        id=user_id,
        username="testbed-admin",
        roles=[IDP_TESTBED_ADMIN_USER]
    )

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

    crud.create_authorized_user(
        db=database,
        user_id=user_id,
        organization_id=result.id
    )

    response = test_client.get(
        f"/organization/{result.id}"
    )

    assert response.status_code == 200
    assert response.json()['name'] == "XXX's Testbed"
    assert response.json()['tradingName'] == "XXX"
    assert response.json()['organizationType'] == "Testbed"


def test_simple_organization_get_by_unauthorized_testbed_admin_1():

    # Prepare Test

    # Prepare Mocked OIDC User
    user_id = "1111-1111-1111-1111"
    MockOIDCUser().inject_mocked_oidc_user(
        id=user_id,
        username="testbed-admin",
        roles=[IDP_TESTBED_ADMIN_USER]
    )

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

    assert response.status_code == 403
    assert response.json()['code'] == 403
    assert response.json()['reason'] == 'User not authorized to access data '\
        f'related with organization {result.id}'


def test_simple_organization_get_by_unauthorized_testbed_admin_2():

    # Prepare Test

    # Prepare Mocked OIDC User
    user_id = "1111-1111-1111-1111"
    MockOIDCUser().inject_mocked_oidc_user(
        id=user_id,
        username="testbed-admin",
        roles=[IDP_TESTBED_ADMIN_USER]
    )

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

    crud.create_authorized_user(
        db=database,
        user_id="different_user_id",
        organization_id=result.id
    )

    response = test_client.get(
        f"/organization/{result.id}"
    )

    assert response.status_code == 403
    assert response.json()['code'] == 403
    assert response.json()['reason'] == 'User not authorized to access data '\
        f'related with organization {result.id}'
