# -*- coding: utf-8 -*-
# @Author: Rafael Direito
# @Date:   2022-10-17 21:13:44
# @Last Modified by:   Rafael Direito
# @Last Modified time: 2022-10-22 11:30:04

# general imports
import pytest

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
def test_simple_organization_database_deletion():

    database = next(override_get_db())

    organization1 = TMF632Schemas.OrganizationCreate(
        tradingName="ITAv"
    )
    organization2 = TMF632Schemas.OrganizationCreate(
        tradingName="ITAv"
    )

    db_organization1 = crud.create_organization(
        db=database,
        organization=organization1
    )
    db_organization2 = crud.create_organization(
        db=database,
        organization=organization2
    )

    crud.delete_organization(
        db=database,
        organization_id=db_organization1.id
    )

    assert db_organization1.deleted
    assert not db_organization2.deleted


def test_unexistent_organization_deletion():

    database = next(override_get_db())

    with pytest.raises(EntityDoesNotExist) as exception:
        crud.delete_organization(
            db=database,
            organization_id=100
        )
    assert "Impossible to obtain entity"\
        and "Organization with id=100 doesn't exist"\
        in str(exception)
