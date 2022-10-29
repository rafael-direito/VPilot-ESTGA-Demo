# -*- coding: utf-8 -*-
# @Author: Rafael Direito
# @Date:   2022-10-17 21:13:44
# @Last Modified by:   Rafael Direito
# @Last Modified time: 2022-10-29 12:23:23

# general imports
import pytest
from pydantic import ValidationError
import datetime

# custom imports
from database.crud import crud
import schemas.tmf632_party_mgmt as TMF632Schemas
from tests.configure_test_idp import (
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
def test_simple_organization_database_creation():

    # Prepare Test
    result = crud.create_organization(
        db=next(override_get_db()),
        organization=TMF632Schemas.OrganizationCreate(
            tradingName="ITAv"
        )
    )
    # Test
    assert result.tradingName == "ITAv"


def test_medium_organization_database_creation():

    # Prepare Test
    result = crud.create_organization(
        db=next(override_get_db()),
        organization=TMF632Schemas.OrganizationCreate(
            tradingName="ITAv",
            isHeadOffice=True,
            isLegalEntity=True,
            name="ITAv's Testbed",
            organizationType="Testbed",
        )
    )

    # Test
    assert result.tradingName == "ITAv"
    assert result.isHeadOffice
    assert result.isLegalEntity
    assert result.name == "ITAv's Testbed"
    assert result.organizationType == "Testbed"


def test_complex_organization_database_creation():

    # Prepare Test
    db_organization = crud.create_organization(
        db=next(override_get_db()),
        organization=TMF632Schemas.OrganizationCreate(
            tradingName="ITAv",
            isHeadOffice=True,
            isLegalEntity=True,
            name="ITAv's Testbed",
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
            ],
            status="validated"
        )
    )

    startDateTime = datetime.datetime(2015, 10, 22, 8, 31, 52, 26000)
    endDateTime = datetime.datetime(2016, 10, 22, 8, 31, 52, 26000)

    # Test
    assert db_organization.tradingName == "ITAv"
    assert db_organization.isHeadOffice
    assert db_organization.isLegalEntity
    assert db_organization.name == "ITAv's Testbed"
    assert db_organization.organizationType == "Testbed"
    assert db_organization.existsDuringParsed.startDateTime\
        .replace(tzinfo=None) == startDateTime
    assert db_organization.existsDuringParsed.endDateTime\
        .replace(tzinfo=None) == endDateTime
    assert len(db_organization.partyCharacteristicParsed)\
        == 2
    assert db_organization.partyCharacteristicParsed[0].name\
        == "ci_cd_agent_url"
    assert db_organization.partyCharacteristicParsed[0].value\
        == "http://192.168.1.200:8080/"
    assert db_organization.partyCharacteristicParsed[0].valueType\
        == "URL"
    assert db_organization.partyCharacteristicParsed[1].name\
        == "ci_cd_agent_username"
    assert db_organization.partyCharacteristicParsed[1].value\
        == "admin"
    assert db_organization.partyCharacteristicParsed[1].valueType\
        == "str"


def test_error_organization_database_creation_invalid_schema():

    with pytest.raises(ValidationError) as exception:
        TMF632Schemas.OrganizationCreate(
            tradingName="ITAv",
            isHeadOffice=True,
            isLegalEntity=True,
            name="ITAv's Testbed",
            organizationType="Testbed",
            existsDuring=TMF632Schemas.TimePeriod(
                startDateTime="2015-10-22T08:31:52.026Z",
                endDateTime="2016-10-22T08:31:52.026Z",
            ),
            status="BAD_STATUS"
        )
    assert "OrganizationCreate" and "validated" and "initialized" and "closed"\
        in str(exception)
