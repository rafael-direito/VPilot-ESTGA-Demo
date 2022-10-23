# -*- coding: utf-8 -*-
# @Author: Rafael Direito
# @Date:   2022-10-17 21:13:44
# @Last Modified by:   Rafael Direito
# @Last Modified time: 2022-10-23 18:06:07

# general imports
import pytest

# custom imports
from tests.configure_test_db import engine
from tests.configure_test_db import test_client
from database.database import Base
from database.crud import crud
import schemas.tmf632_party_mgmt as TMF632Schemas
from tests.configure_test_db import override_get_db


# Create the DB before each test and delete it afterwards
@pytest.fixture(autouse=True)
def test_db():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


# Tests
def test_fields_url_params():

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
