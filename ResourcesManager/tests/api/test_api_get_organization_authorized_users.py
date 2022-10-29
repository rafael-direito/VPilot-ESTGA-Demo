# -*- coding: utf-8 -*-
# @Author: Rafael Direito
# @Date:   2022-10-17 21:13:44
# @Last Modified by:   Rafael Direito
# @Last Modified time: 2022-10-29 16:43:09

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
def test_correct_organization_get_authorized_users():

    # Prepare Test

    # Make request using a VPilot Admin and Testbed Admin Role
    inject_admin_user()

    database = next(override_get_db())

    db_organization = crud.create_organization(
        db=database,
        organization=TMF632Schemas.OrganizationCreate(
            tradingName="XXX",
            name="XXX's Testbed",
            organizationType="Testbed",
        )
    )
    # Create Authorized Users
    crud.create_authorized_user(
        db=database,
        user_id="XXXX",
        organization_id=db_organization.id
    )

    response = test_client.get(
        f"/organization/{db_organization.id}/authorized-users"
    )

    assert response.status_code == 200
    assert response.json()['organization_id'] == "1"
    assert isinstance(response.json()['authorized_users'], list)
    assert response.json()['authorized_users'][0]["user_id"] == "XXXX"


def test_correct_organization_get_authorized_users_no_users():

    # Prepare Test

    # Make request using a VPilot Admin and Testbed Admin Role
    inject_admin_user()

    database = next(override_get_db())

    db_organization = crud.create_organization(
        db=database,
        organization=TMF632Schemas.OrganizationCreate(
            tradingName="XXX",
            name="XXX's Testbed",
            organizationType="Testbed",
        )
    )

    response = test_client.get(
        f"/organization/{db_organization.id}/authorized-users"
    )

    assert response.status_code == 200
    assert response.json()['organization_id'] == "1"
    assert isinstance(response.json()['authorized_users'], list)
    assert len(response.json()['authorized_users']) == 0


def test_get_nonexistente_organization_authorized_users():

    # Make request using a VPilot Admin and Testbed Admin Role
    inject_admin_user()

    # Test
    response = test_client.get("/organization/0/authorized-users")

    assert response.status_code == 400
    assert "The requested organization doesn't exist."\
        in response.json()['reason']


def test_get_organization_authorized_users_without_required_roles():

    # Prepare Test

    # Prepare Mocked OIDC User
    user_id = "1111-1111-1111-1111"
    MockOIDCUser().inject_mocked_oidc_user(
        id=user_id,
        username="random_user",
        roles=[]
    )

    response = test_client.get("/organization/0/authorized-users")

    assert response.status_code == 403
    assert response.json()['code'] == 403
    assert response.json()['reason'] == f'Role "{IDP_TESTBED_ADMIN_USER}" is '\
        'required to perform this action'


def test_get_organization_authorized_users_without_permissions():

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
        f"/organization/{result.id}/authorized-users"
    )

    assert response.status_code == 403
    assert response.json()['code'] == 403
    assert response.json()['reason'] == 'User not authorized to access data '\
        f'related with organization {result.id}'
