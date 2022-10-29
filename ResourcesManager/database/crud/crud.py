# -*- coding: utf-8 -*-
# @Author: Rafael Direito
# @Date:   2022-10-17 12:00:16
# @Last Modified by:   Rafael Direito
# @Last Modified time: 2022-10-29 13:59:06

# general imports
import logging
from sqlalchemy.orm import Session

# custom imports
from database.models import models
from schemas import tmf632_party_mgmt
from database.crud.exceptions import ImpossibleToCreateDatabaseEntry
from database.crud.exceptions import EntityDoesNotExist

# Logger
logger = logging.getLogger(__name__)

#######################################
#     Time Period CRUD Operations     #
#######################################


def delete_time_period(db: Session, time_period_id: int):
    time_period = db\
        .query(models.TimePeriod)\
        .filter(models.TimePeriod.id == time_period_id)\
        .filter(models.TimePeriod.deleted == bool(False))

    if time_period:
        time_period.delete = True
        db.commit()


def permanentely_delete_time_period(db: Session, time_period_id: int):
    return db\
        .query(models.TimePeriod)\
        .filter(models.TimePeriod.id == time_period_id)\
        .filter(models.TimePeriod.deleted == bool(False))\
        .delete()


#######################################
#    Characteristic CRUD Operations   #
#######################################


def permanentely_delete_party_characteristic_by_id(
    db: Session,
    characteristic_id: int
):
    return db\
        .query(models.Characteristic)\
        .filter(models.Characteristic.id == characteristic_id)\
        .delete()


def permanentely_delete_party_characteristic_by_organization_id(
    db: Session,
    organization_id: int
):
    return db\
        .query(models.Characteristic)\
        .filter(models.Characteristic.organization == organization_id)\
        .delete()


def delete_party_characteristic_by_id(db: Session, characteristic_id: int):
    party_characteristic = db\
        .query(models.Characteristic)\
        .filter(models.Characteristic.id == characteristic_id)\
        .first()

    if party_characteristic:
        party_characteristic.deleted = True
        db.commit()


def delete_party_characteristic_by_organization_id(
    db: Session,
    organization_id: int
):
    party_characteristics = db\
        .query(models.Characteristic)\
        .filter(models.Characteristic.organization == organization_id)\
        .filter(models.Characteristic.deleted == bool(False))\
        .all()

    for party_characteristic in party_characteristics:
        party_characteristic.deleted = True
        db.commit()


#######################################
#   Authorized Users CRUD Operations  #
#######################################


def create_authorized_user(db: Session, user_id: str, organization_id: int):
    try:
        db_authorized_user = models.OrganizationAuthorizedUsers(
            user_id=user_id,
            organization=organization_id,
        )
        db.add(db_authorized_user)
        db.commit()
        db.refresh(db_authorized_user)
        logger.info(
            "Authorized User created for Organization " +
            f"(id={db_authorized_user}): {db_authorized_user.as_dict()}"
        )
        db_authorized_user.set_db(db)
        return db_authorized_user

    except Exception as e:
        raise ImpossibleToCreateDatabaseEntry(
            entity_type="OrganizationAuthorizedUsers",
            entity_data=str(db_authorized_user),
            reason=str(e)
        )


def permanentely_delete_authorized_user(db: Session, user_id: str):
    return db\
        .query(models.OrganizationAuthorizedUsers)\
        .filter(models.OrganizationAuthorizedUsers.user_id == user_id)\
        .filter(models.OrganizationAuthorizedUsers.deleted == bool(False))\
        .delete()


def permanentely_delete_authorized_user_for_organization(
    db: Session, user_id: str, organization_id: int
):
    return db\
        .query(models.OrganizationAuthorizedUsers)\
        .filter(models.OrganizationAuthorizedUsers.user_id == user_id)\
        .filter(
            models.OrganizationAuthorizedUsers.organization == organization_id
        )\
        .filter(models.OrganizationAuthorizedUsers.deleted == bool(False))\
        .delete()


def delete_authorized_user(db: Session, user_id: str):

    db_authorized_users = db\
        .query(models.OrganizationAuthorizedUsers)\
        .filter(models.OrganizationAuthorizedUsers.user_id == user_id)\
        .filter(models.OrganizationAuthorizedUsers.deleted == bool(False))\
        .all()

    for db_authorized_user in db_authorized_users:
        db_authorized_user.deleted = True
        db.commit()


def delete_authorized_user_for_organization(
    db: Session, user_id: str, organization_id: int
):
    db_authorized_users = db\
        .query(models.OrganizationAuthorizedUsers)\
        .filter(models.OrganizationAuthorizedUsers.user_id == user_id)\
        .filter(
            models.OrganizationAuthorizedUsers.organization == organization_id
        )\
        .filter(models.OrganizationAuthorizedUsers.deleted == bool(False))\
        .all()

    for db_authorized_user in db_authorized_users:
        db_authorized_user.deleted = True
        db.commit()


def get_authorized_organizations_for_user(db: Session, user_id: str):
    return [
        get_organization_by_id(
            db=db,
            id=db_authorized_user.organization
        )
        for db_authorized_user
        in db
        .query(models.OrganizationAuthorizedUsers)
        .filter(
            models.OrganizationAuthorizedUsers.user_id == user_id
        )
        .filter(models.OrganizationAuthorizedUsers.deleted == bool(False))
        .all()
    ]


#######################################
#    Organization CRUD Operations     #
#######################################


def create_organization(db: Session,
                        organization: tmf632_party_mgmt.OrganizationCreate):
    try:
        db_time_period_id = None
        # Try to create a new TimePeriod DB Entry
        if organization.existsDuring:
            time_period = models.TimePeriod(
                **organization.existsDuring.dict()
            )
            db.add(time_period)
            db.flush()
            db.refresh(time_period)
            db_time_period_id = time_period.id

        # Check if a status was assigned to the organization
        status_value = None
        if organization.status:
            status_value = organization.status.value

        # Create the Organization Itself
        db_organization = models.Organization(
            isHeadOffice=organization.isHeadOffice,
            isLegalEntity=organization.isLegalEntity,
            name=organization.name,
            nameType=organization.nameType,
            organizationType=organization.organizationType,
            tradingName=organization.tradingName,
            existsDuring=db_time_period_id,
            status=status_value,
            _baseType=None,
            _schemaLocation=None,
            _type=None
        )

        db.add(db_organization)
        db.flush()
        db.refresh(db_organization)
        db_organization.set_db(db)
        logger.info(f"Organization created: {db_organization.as_dict()}")

        # Try to create a new partyCharacteristic DB Entry
        if organization.partyCharacteristic:
            for party_characteristic in organization.partyCharacteristic:
                db_party_characteristic = models.Characteristic(
                    **party_characteristic.dict()
                )
                db_party_characteristic.organization = db_organization.id
                db.add(db_party_characteristic)
                db.flush()

        db.commit()
        return db_organization

    except Exception as e:
        # Rollback everything we did and raise appropriate exception
        db.rollback()
        raise ImpossibleToCreateDatabaseEntry(
            entity_type="Organization",
            entity_data=str(organization),
            reason=str(e)
        )


def update_organization(db: Session,
                        organization_id: int,
                        organization: tmf632_party_mgmt.OrganizationCreate):
    try:
        # Check if organization payload contains the organization's id
        if not organization_id:
            raise EntityDoesNotExist(
                entity_type="Organization",
                reason="Organization had no id"
            )

        # Get current organization
        db_organization = get_organization_by_id(
            db=db,
            id=organization_id
        )

        if not db_organization:
            raise EntityDoesNotExist(
                entity_type="Organization",
                reason=f"Organization with id={organization_id} doesn't exist"
            )

        # Try to create a new TimePeriod DB Entry
        db_time_period_id = None
        if organization.existsDuring:
            # Delete previous one
            if db_organization.existsDuring:
                db_organization.existsDuringParsed.deleted = True
                db.flush()
            # create a new one
            db_time_period = models.TimePeriod(
                **organization.existsDuring.dict()
            )
            db.add(db_time_period)
            db.flush()
            db.refresh(db_time_period)
            db_time_period_id = db_time_period.id

        # Try to create a new partyCharacteristic DB Entry
        if organization.partyCharacteristic:
            for characteristic in db_organization.partyCharacteristicParsed:
                if characteristic:
                    characteristic.deleted = True
                    db.flush()

            for party_characteristic in organization.partyCharacteristic:
                db_party_characteristic = models.Characteristic(
                    **party_characteristic.dict()
                )
                db_party_characteristic.organization = db_organization.id
                db.add(db_party_characteristic)
                db.flush()

        # Check if a status was assigned to the organization
        status_value = None
        if organization.status:
            status_value = organization.status.value

        # Update the Organization Itself
        db_organization.isHeadOffice = organization.isHeadOffice
        db_organization.isLegalEntity = organization.isLegalEntity
        db_organization.name = organization.name
        db_organization.nameType = organization.nameType
        db_organization.organizationType = organization.organizationType
        db_organization.tradingName = organization.tradingName
        db_organization.existsDuring = db_time_period_id
        db_organization.status = status_value
        db_organization._baseType = None
        db_organization._schemaLocation = None
        db_organization._type = None

        db.flush()
        db.refresh(db_organization)
        logger.info(f"Organization updated: {db_organization.as_dict()}")

        # Finally, commit
        db.commit()
        db_organization.set_db(db)
        return db_organization

    except EntityDoesNotExist as e:
        # Rollback everything we did and raise appropriate exception
        db.rollback()
        raise e
    except Exception as e:
        # Rollback everything we did and raise appropriate exception
        db.rollback()
        raise ImpossibleToCreateDatabaseEntry(
            entity_type="Organization",
            entity_data=str(organization),
            reason=str(e)
        )


def get_organization_by_id(db: Session, id: int):
    organization_model = models.Organization
    organization_model.set_db(db)
    organization = db\
        .query(organization_model)\
        .filter(organization_model.id == id)\
        .filter(organization_model.deleted == bool(False))\
        .first()

    return organization


def get_all_organizations(db: Session, filters: dict = {}):

    organizations = db\
        .query(models.Organization)\
        .filter(models.Organization.deleted == bool(False))\
        .filter_by(**filters)\
        .all()

    return organizations


def permanentely_delete_organization(db: Session, organization_id: int):

    db_organization = get_organization_by_id(db, organization_id)

    # Delete Time Period
    permanentely_delete_time_period(db, db_organization.id)

    # Delete partyCharacteristics
    permanentely_delete_party_characteristic_by_organization_id(
        db,
        db_organization.id
    )

    # Finally, delete the organization
    db\
        .query(models.Organization)\
        .filter(models.Organization.id == organization_id)\
        .delete()


def delete_organization(db: Session, organization_id: int):

    schema_organization = get_organization_by_id(db, organization_id)

    if not schema_organization:
        raise EntityDoesNotExist(
            entity_type="Organization",
            reason=f"Organization with id={organization_id} doesn't exist"
        )

    # Delete Time Period
    delete_time_period(db, schema_organization.id)

    # Delete partyCharacteristics
    delete_party_characteristic_by_organization_id(
        db,
        schema_organization.id
    )

    # Finally, delete the organization
    db_organization = db\
        .query(models.Organization)\
        .filter(models.Organization.id == schema_organization.id)\
        .first()

    db_organization.deleted = True
    db.commit()
