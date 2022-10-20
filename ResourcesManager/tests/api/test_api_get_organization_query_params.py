# -*- coding: utf-8 -*-
# @Author: Rafael Direito
# @Date:   2022-10-17 21:13:44
# @Last Modified by:   Rafael Direito
# @Last Modified time: 2022-10-20 23:05:43

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
def test_fields_while_requesting_organizations():

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


def test_filters_while_requesting_organizations():

    # Test

    # TODO: Implement later, when the full business logic has been implemented

    # response1 = test_client.get(
    #     "/organization?taxExemptionCertificate.id=1"
    # )
    # response2 = test_client.get(
    #     "/organization?taxExemptionCertificate.id=1&name=XXX"
    # )
    # response3 = test_client.get(
    #     "/organization/1?taxExemptionCertificate.id=1"
    # )
    # response4 = test_client.get(
    #     "/organization/1?taxExemptionCertificate.id=1&name=XXX"
    # )
    # response5 = test_client.get(
    #     "/organization/?jibberish=1"
    # )
    # response6 = test_client.get(
    #     "/organization/1?jibberish=1"
    # )
    # response7 = test_client.get(
    #     "/organization?taxExemptionCertificate.id=1&name=XXX&jibberish=a"
    # )
    # response8 = test_client.get(
    #     "/organization/1?taxExemptionCertificate.id=1&name=XXX&jibberish=a"
    # )
    # assert response1.status_code == 200
    # assert response2.status_code == 200
    # assert response3.status_code == 200
    # assert response4.status_code == 200
    # assert response5.status_code == 400
    # assert "Error" in response5.json()['reason']
    # assert "string does not match regex" in response5.json()['reason']

    return
