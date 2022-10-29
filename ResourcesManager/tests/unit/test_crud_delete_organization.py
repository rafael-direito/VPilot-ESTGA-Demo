# -*- coding: utf-8 -*-
# @Author: Rafael Direito
# @Date:   2022-10-17 21:13:44
# @Last Modified by:   Rafael Direito
# @Last Modified time: 2022-10-29 10:32:21

# general imports
import pytest

# custom imports
from database.crud import crud
from database.crud.exceptions import EntityDoesNotExist
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
