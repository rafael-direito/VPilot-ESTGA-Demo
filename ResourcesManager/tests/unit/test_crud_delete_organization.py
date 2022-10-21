# -*- coding: utf-8 -*-
# @Author: Rafael Direito
# @Date:   2022-10-17 21:13:44
# @Last Modified by:   Rafael Direito
# @Last Modified time: 2022-10-21 17:59:15

# general imports
import pytest

# custom imports
from database.crud import crud
import schemas.tmf632_party_mgmt as TMF632Schemas
from tests.configure_test_db import override_get_db
from tests.configure_test_db import engine
from database.database import Base


# Create the DB before each test and delete it afterwards
@pytest.fixture(autouse=True)
def test_db():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


# Tests
def test_simple_organization_database_creation():

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
