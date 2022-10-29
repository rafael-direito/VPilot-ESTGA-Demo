# -*- coding: utf-8 -*-
# @Author: Rafael Direito
# @Date:   2022-10-17 21:13:44
# @Last Modified by:   Rafael Direito
# @Last Modified time: 2022-10-29 12:19:56

# general imports
import pytest

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
def test_characteristic_correct_database_creation_only_mandatory_values():

    database = next(override_get_db())

    # Prepare Test
    db_organization = crud.create_organization(
        db=database,
        organization=TMF632Schemas.OrganizationCreate(
            tradingName="ITAv",
            partyCharacteristic=[
                TMF632Schemas.Characteristic(
                    name="ci_cd_agent_url",
                    value="http://192.168.1.200:8080/",
                )
            ]
        )
    )

    # Test
    assert db_organization.partyCharacteristicParsed[0].name\
        == "ci_cd_agent_url"
    assert db_organization.partyCharacteristicParsed[0].value\
        == "http://192.168.1.200:8080/"
    assert db_organization.partyCharacteristicParsed[0].organization\
        == db_organization.id
    assert db_organization.partyCharacteristicParsed[0].valueType\
        is None


def test_characteristic_correct_database_creation_all_values():

    database = next(override_get_db())

    # Prepare Test
    db_organization = crud.create_organization(
        db=database,
        organization=TMF632Schemas.OrganizationCreate(
            tradingName="ITAv",
            partyCharacteristic=[
                TMF632Schemas.Characteristic(
                    name="ci_cd_agent_url",
                    value="http://192.168.1.200:8080/",
                    valueType="URL",
                )
            ]
        )
    )

    # Test
    assert db_organization.partyCharacteristicParsed[0].name\
        == "ci_cd_agent_url"
    assert db_organization.partyCharacteristicParsed[0].value\
        == "http://192.168.1.200:8080/"
    assert db_organization.partyCharacteristicParsed[0].valueType\
        == "URL"
    assert db_organization.partyCharacteristicParsed[0].organization\
        == db_organization.id
