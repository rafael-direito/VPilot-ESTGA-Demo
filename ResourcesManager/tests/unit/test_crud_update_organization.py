# -*- coding: utf-8 -*-
# @Author: Rafael Direito
# @Date:   2022-10-17 21:13:44
# @Last Modified by:   Rafael Direito
# @Last Modified time: 2022-10-22 14:37:36

# general imports
import pytest
import datetime

# custom imports
from database.crud import crud
import schemas.tmf632_party_mgmt as TMF632Schemas
from tests.configure_test_db import override_get_db
from tests.configure_test_db import engine
from database.database import Base
from database.crud.exceptions import EntityDoesNotExist


# Create the DB before each test and delete it afterwards
@pytest.fixture(autouse=True)
def test_db():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


# Tests
def test_complex_organization_database_update():

    database = next(override_get_db())

    organization = TMF632Schemas.OrganizationCreate(
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

    db_organization = crud.create_organization(
        db=database,
        organization=organization
    )

    # Prepare Update
    organization.tradingName = "XXX"
    organization.name = "XXX's Testbed"
    organization.existsDuring = TMF632Schemas.TimePeriod(
        startDateTime="2020-10-22T08:31:52.026Z",
        endDateTime="2021-10-22T08:31:52.026Z",
    )
    organization.partyCharacteristic = [
        TMF632Schemas.Characteristic(
                name="test_name",
                value="test_value",
                valueType="test_value_type",
            ),
    ]

    # Update Organization
    db_updated_organization = crud.update_organization(
        db=database,
        organization_id=db_organization.id,
        organization=organization
    )

    updated_organization = crud.get_organization_by_id(
        database,
        db_updated_organization.id
    )

    db_time_period = crud.get_time_period_by_id(
        db=database,
        id=db_updated_organization.existsDuring
    )

    db_characteristics = crud.get_party_characteristics_by_organization_id(
        db=database,
        organization_id=db_updated_organization.id
    )

    startDateTime = datetime.datetime(2020, 10, 22, 8, 31, 52, 26000)
    endDateTime = datetime.datetime(2021, 10, 22, 8, 31, 52, 26000)

    assert updated_organization.tradingName == "XXX"
    assert updated_organization.isHeadOffice
    assert updated_organization.isLegalEntity
    assert updated_organization.name == "XXX's Testbed"
    assert db_updated_organization.organizationType == "Testbed"

    assert db_time_period.startDateTime.replace(tzinfo=None) == startDateTime
    assert db_time_period.endDateTime.replace(tzinfo=None) == endDateTime

    assert len(db_characteristics) == 1
    assert db_characteristics[0].name == "test_name"
    assert db_characteristics[0].value == "test_value"
    assert db_characteristics[0].valueType == "test_value_type"


def test_nonexistent_organization_database_update():

    database = next(override_get_db())

    with pytest.raises(EntityDoesNotExist) as exception:
        crud.update_organization(
            db=database,
            organization_id=999,
            organization=None
        )

    assert "Impossible to obtain entity"\
        and "Organization with id=999 doesn't exist"\
        in str(exception)
