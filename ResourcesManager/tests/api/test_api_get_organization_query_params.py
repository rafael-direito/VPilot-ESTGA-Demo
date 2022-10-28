# -*- coding: utf-8 -*-
# @Author: Rafael Direito
# @Date:   2022-10-17 21:13:44
# @Last Modified by:   Rafael Direito
# @Last Modified time: 2022-10-28 22:17:38

# general imports
import pytest

# custom imports
from database.crud import crud
import schemas.tmf632_party_mgmt as TMF632Schemas
from tests.configure_test_idp import (
    inject_admin_user,
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
def test_fields_url_params():

    # Make request using a VPilot Admin and Testbed Admin Role
    inject_admin_user()

    # Test

    response1 = test_client.get(
        "/organization?fields=contactMedium,name"
    )
    response2 = test_client.get(
        "/organization?fields=contactMedium,name,isHeadOffice"
    )
    response3 = test_client.get(
        "/organization/1?fields=contactMedium,name"
    )
    response4 = test_client.get(
        "/organization/1?fields=contactMedium,name,isHeadOffice"
    )
    response5 = test_client.get(
        "/organization?fields=contactMedium,name,jibberish"
    )
    response6 = test_client.get(
        "/organization/1?fields=contactMedium,name,jibberish"
    )

    assert response1.status_code == 200
    assert response2.status_code == 200
    assert response3.status_code == 200
    assert response4.status_code == 200
    assert response5.status_code == 400
    assert "Error" in response5.json()['reason']
    assert "string does not match regex" in response5.json()['reason']
    assert response6.status_code == 400
    assert "Error" in response6.json()['reason']
    assert "string does not match regex" in response6.json()['reason']


def test_get_filtered_organization():

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
        status="validated"
    )

    result = crud.create_organization(
        db=database,
        organization=organization
    )

    # Test

    response1 = test_client.get(
        "/organization?fields=name"
    )
    response2 = test_client.get(
        "/organization?fields=name,tradingName,status"
    )
    response3 = test_client.get(
        f"/organization/{result.id}?fields=name"
    )
    response4 = test_client.get(
        f"/organization/{result.id}?fields=name,tradingName,status"
    )
    response5 = test_client.get(
        "/organization"
    )
    response6 = test_client.get(
        f"/organization/{result.id}"
    )

    assert response1.status_code == 200
    assert response2.status_code == 200
    assert response3.status_code == 200
    assert response4.status_code == 200
    assert response5.status_code == 200
    assert response6.status_code == 200

    assert response1.json()[0].get("name") == "XXX's Testbed"
    assert response1.json()[0].get("tradingName") is None
    assert response1.json()[0].get("status") is None

    assert response2.json()[0].get("name") == "XXX's Testbed"
    assert response2.json()[0].get("tradingName") == "XXX"
    assert response2.json()[0].get("status") == "validated"
    assert response2.json()[0].get("organizationType") is None

    assert response3.json().get("name") == "XXX's Testbed"
    assert response3.json().get("tradingName") is None
    assert response3.json().get("status") is None

    assert response4.json().get("name") == "XXX's Testbed"
    assert response4.json().get("tradingName") == "XXX"
    assert response4.json().get("status") == "validated"
    assert response4.json().get("organizationType") is None

    assert response5.json()[0].get("name") == "XXX's Testbed"
    assert response5.json()[0].get("tradingName") == "XXX"
    assert response5.json()[0].get("organizationType") == "Testbed"
    assert response5.json()[0].get("status") == "validated"

    assert response6.json().get("name") == "XXX's Testbed"
    assert response6.json().get("tradingName") == "XXX"
    assert response6.json().get("organizationType") == "Testbed"
    assert response6.json().get("status") == "validated"
