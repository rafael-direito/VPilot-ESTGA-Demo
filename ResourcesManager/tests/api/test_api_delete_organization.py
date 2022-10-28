# -*- coding: utf-8 -*-
# @Author: Rafael Direito
# @Date:   2022-10-17 21:13:44
# @Last Modified by:   Rafael Direito
# @Last Modified time: 2022-10-28 21:52:31

# general imports
import pytest

# custom imports
from database.crud import crud
import schemas.tmf632_party_mgmt as TMF632Schemas
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
def test_correct_organization_deletion():

    # Prepare Test

    # Make request using a VPilot Admin
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

    response = test_client.delete(
        f"/organization/{result.id}"
    )

    assert response.status_code == 204


def test_unexistent_organization_deletion():

    # Make request using a VPilot Admin
    inject_admin_user()

    response = test_client.delete("/organization/999")

    assert response.status_code == 400
    assert "Organization with id=999 doesn't exist"\
        in response.json()['reason']


def test_unauthorized_organization_deletion():

    # Prepare Mocked OIDC User
    MockOIDCUser().inject_mocked_oidc_user(
        id="1111-1111-1111-1111",
        username="testbed-admin",
        roles=[IDP_TESTBED_ADMIN_USER]
    )

    response = test_client.delete("/organization/999")

    assert response.status_code == 403
    assert response.json()['code'] == 403
    assert f'Role "{IDP_ADMIN_USER}" is required to perform this '\
        'action' in response.json()['reason']
