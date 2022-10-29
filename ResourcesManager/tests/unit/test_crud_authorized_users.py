# -*- coding: utf-8 -*-
# @Author: Rafael Direito
# @Date:   2022-10-25 21:45:04
# @Last Modified by:   Rafael Direito
# @Last Modified time: 2022-10-29 12:39:06


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
def test_create_authorized_user_for_organization():

    # Prepare Test
    database = next(override_get_db())

    db_organization = crud.create_organization(
        db=database,
        organization=TMF632Schemas.OrganizationCreate(
            tradingName="ITAv"
        )
    )

    db_authorized_user = crud.create_authorized_user(
        db=database,
        user_id="1111-2222-3333",
        organization_id=db_organization.id
    )

    # Test
    assert db_authorized_user.id == 1
    assert db_authorized_user.user_id == "1111-2222-3333"
    assert db_authorized_user.organization == db_organization.id
    assert not db_authorized_user.deleted


def test_get_authorized_users_for_organization():

    # Prepare Test
    database = next(override_get_db())

    db_organization = crud.create_organization(
        db=database,
        organization=TMF632Schemas.OrganizationCreate(
            tradingName="ITAv"
        )
    )
    crud.create_authorized_user(
        db=database,
        user_id="1111-2222-3333",
        organization_id=db_organization.id
    )
    crud.create_authorized_user(
        db=database,
        user_id="4444-5555-4444",
        organization_id=db_organization.id
    )

    # Test
    assert len(db_organization.authorizedUsersParsed) == 2
    assert db_organization.authorizedUsersParsed[0].user_id == "1111-2222-3333"
    assert db_organization.authorizedUsersParsed[1].user_id == "4444-5555-4444"
    assert db_organization.authorizedUsersParsed[0].organization\
        == db_organization.authorizedUsersParsed[1].organization\
        == db_organization.id


def test_get_organizations_for_user():

    # Prepare Test
    database = next(override_get_db())

    db_organization1 = crud.create_organization(
        db=database,
        organization=TMF632Schemas.OrganizationCreate(
            tradingName="XXX"
        )
    )
    db_organization2 = crud.create_organization(
        db=database,
        organization=TMF632Schemas.OrganizationCreate(
            tradingName="YYY"
        )
    )
    db_user = crud.create_authorized_user(
        db=database,
        user_id="1111-2222-3333",
        organization_id=db_organization1.id
    )
    db_user = crud.create_authorized_user(
        db=database,
        user_id="1111-2222-3333",
        organization_id=db_organization2.id
    )

    # Test
    assert len(db_user.authorizedOriganizations) == 2
    assert db_user.authorizedOriganizations[0].id == 1
    assert db_user.authorizedOriganizations[1].id == 2
    assert db_user.authorizedOriganizations[0].tradingName == "XXX"
    assert db_user.authorizedOriganizations[1].tradingName == "YYY"


def test_delete_of_authorized_user_for_all_organizations():

    # Prepare Test
    database = next(override_get_db())

    db_organization = crud.create_organization(
        db=database,
        organization=TMF632Schemas.OrganizationCreate(
            tradingName="XXX"
        )
    )
    crud.create_authorized_user(
        db=database,
        user_id="XXXX",
        organization_id=db_organization.id
    )

    db_user = crud.create_authorized_user(
        db=database,
        user_id="XXXX",
        organization_id=db_organization.id
    )

    crud.delete_authorized_user(
        db=database,
        user_id="XXXX",
    )

    # Test
    assert len(db_user.authorizedOriganizations) == 0


def test_delete_of_authorized_user_for_an_organizations():

    # Prepare Test
    database = next(override_get_db())

    db_organization1 = crud.create_organization(
        db=database,
        organization=TMF632Schemas.OrganizationCreate(
            tradingName="XXX"
        )
    )
    db_organization2 = crud.create_organization(
        db=database,
        organization=TMF632Schemas.OrganizationCreate(
            tradingName="YYY"
        )
    )
    crud.create_authorized_user(
        db=database,
        user_id="11111",
        organization_id=db_organization1.id
    )

    db_user = crud.create_authorized_user(
        db=database,
        user_id="11111",
        organization_id=db_organization2.id
    )

    crud.delete_authorized_user_for_organization(
        db=database,
        user_id="11111",
        organization_id=db_organization1.id
    )

    # Test
    assert len(db_user.authorizedOriganizations) == 1
    assert db_user.authorizedOriganizations[0].id == db_organization2.id
    assert db_user.authorizedOriganizations[0].tradingName == "YYY"
