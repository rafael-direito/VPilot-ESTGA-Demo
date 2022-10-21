# -*- coding: utf-8 -*-
# @Author: Rafael Direito
# @Date:   2022-10-17 21:13:44
# @Last Modified by:   Rafael Direito
# @Last Modified time: 2022-10-21 15:58:33

# general imports
import pytest

# custom imports
from database.crud import crud
import schemas.tmf632_party_mgmt as TMF632Schemas
from tests.configure_test_db import override_get_db
from tests.configure_test_db import engine
from database.database import Base
from database.crud.exceptions import ImpossibleToCreateDatabaseEntry


# Create the DB before each test and delete it afterwards
@pytest.fixture(autouse=True)
def test_db():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


# Tests
def test_characteristic_correct_database_creation_only_mandatory_values():

    database = next(override_get_db())

    # Prepare Test

    organization = TMF632Schemas.OrganizationCreate(
        tradingName="ITAv"
    )
    party_characteristic = TMF632Schemas.Characteristic(
        name="ci_cd_agent_url",
        value="http://192.168.1.200:8080/",
    )

    db_organization = crud.create_organization(
        db=database,
        organization=organization
    )

    db_party_characteristic = crud.create_party_characteristic(
        db=database,
        party_characteristic=party_characteristic,
        organization_id=db_organization.id
    )

    print(db_party_characteristic.__dict__)
    assert db_party_characteristic.name == "ci_cd_agent_url"
    assert db_party_characteristic.value == "http://192.168.1.200:8080/"
    assert db_party_characteristic.organization == db_organization.id
    assert db_party_characteristic.valueType is None


def test_characteristic_correct_database_creation_all_values():

    database = next(override_get_db())

    # Prepare Test

    organization = TMF632Schemas.OrganizationCreate(
        tradingName="ITAv"
    )
    party_characteristic = TMF632Schemas.Characteristic(
        name="ci_cd_agent_url",
        value="http://192.168.1.200:8080/",
        valueType="URL",
    )

    db_organization = crud.create_organization(
        db=database,
        organization=organization
    )

    db_party_characteristic = crud.create_party_characteristic(
        db=database,
        party_characteristic=party_characteristic,
        organization_id=db_organization.id
    )

    assert db_party_characteristic.name == "ci_cd_agent_url"
    assert db_party_characteristic.value == "http://192.168.1.200:8080/"
    assert db_party_characteristic.valueType == "URL"
    assert db_party_characteristic.organization == db_organization.id


def test_characteristic_incorrect_database_creation():

    database = next(override_get_db())

    # Prepare Test

    party_characteristic = TMF632Schemas.Characteristic(
        name="ci_cd_agent_url",
        value="http://192.168.1.200:8080/",
        valueType="URL",
    )

    with pytest.raises(ImpossibleToCreateDatabaseEntry) as exception1:
        crud.create_party_characteristic(
            db=database,
            party_characteristic=party_characteristic,
            organization_id=None
        )

    with pytest.raises(ImpossibleToCreateDatabaseEntry) as exception2:
        crud.create_party_characteristic(
            db=database,
            party_characteristic=party_characteristic,
            organization_id=2
        )

    assert "Impossible to create a database entry" in str(exception1)
    assert "Impossible to create a database entry" in str(exception2)
