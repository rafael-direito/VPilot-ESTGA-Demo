# -*- coding: utf-8 -*-
# @Author: Rafael Direito
# @Date:   2022-10-17 12:00:16
# @Last Modified by:   Rafael Direito
# @Last Modified time: 2022-10-21 16:58:40

# general imports
import logging
from sqlalchemy.orm import Session

# custom imports
from database.models import models
from schemas import tmf632_party_mgmt
from database.crud.exceptions import ImpossibleToCreateDatabaseEntry

# Logger
logger = logging.getLogger(__name__)


def create_time_period(db: Session,
                       time_period: tmf632_party_mgmt.TimePeriod):

    try:
        time_period = models.TimePeriod(**time_period.dict())
        db.add(time_period)
        db.commit()
        db.refresh(time_period)
        logger.info(f"Time Period created: {time_period.as_dict()}")
        return time_period

    except Exception as e:
        raise ImpossibleToCreateDatabaseEntry(
            entity_type="TimePeriod",
            entity_data=str(time_period),
            reason=str(e)
        )


def create_party_characteristic(
    db: Session,
    party_characteristic: tmf632_party_mgmt.Characteristic,
    organization_id: int
):
    try:
        db_party_characteristic = models.Characteristic(
            **party_characteristic.dict()
        )
        db_party_characteristic.organization = organization_id
        db.add(db_party_characteristic)
        db.commit()
        db.refresh(db_party_characteristic)
        logger.info(
            "Characteristic created for Organization " +
            f"(id={organization_id}): {db_party_characteristic.as_dict()}"
        )
        return db_party_characteristic

    except Exception as e:
        raise ImpossibleToCreateDatabaseEntry(
            entity_type="Characteristic",
            entity_data=str(db_party_characteristic),
            reason=str(e)
        )


def create_organization(db: Session,
                        organization: tmf632_party_mgmt.Organization):

    db_time_period_id = None
    db_organization_id = None
    db_party_characteristics_id = None

    try:
        db_time_period_id = None
        # Try to create a new TimePeriod DB Entry
        if organization.existsDuring:
            db_time_period = create_time_period(db, organization.existsDuring)
            db_time_period_id = db_time_period.id

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
        db.commit()
        db.refresh(db_organization)
        db_organization_id = db_organization.id
        logger.info(f"Organization created: {db_organization.as_dict()}")

        # Try to create a new partyCharacteristic DB Entry
        if organization.partyCharacteristic:
            db_party_characteristics_id = []
            for party_characteristic in organization.partyCharacteristic:
                db_party_characteristics_id.append(
                    create_party_characteristic(
                        db=db,
                        party_characteristic=party_characteristic,
                        organization_id=db_organization_id
                    ).id
                )
        return db_organization

    except Exception as e:

        # Rollback everything we did
        if db_organization_id:
            delete_organization(db, db_organization_id)
        else:
            if db_time_period_id:
                delete_time_period(db, db_time_period_id)
            if db_party_characteristics_id:
                for party_characteristic_id in db_party_characteristics_id:
                    delete_party_characteristic_by_id(
                        db,
                        party_characteristic_id
                    )

        raise ImpossibleToCreateDatabaseEntry(
            entity_type="Organization",
            entity_data=str(organization),
            reason=str(e)
        )


def get_time_period_by_id(db: Session, id: int):
    return tmf632_party_mgmt.TimePeriod.from_orm(
        db
        .query(models.TimePeriod)
        .filter(models.TimePeriod.id == id)
        .first()
    )


def get_party_characteristics_by_organization_id(
    db: Session,
    organization_id: int
):
    return [
        tmf632_party_mgmt.Characteristic.from_orm(characteristic)
        for characteristic
        in db
        .query(models.Characteristic)
        .filter(models.Characteristic.organization == organization_id)
        .all()
    ]


def get_organization_by_id(db: Session, id: int):
    organization = db\
        .query(models.Organization)\
        .filter(models.Organization.id == id)\
        .first()

    if not organization:
        return

    organization_schema = tmf632_party_mgmt.Organization.from_orm(organization)

    # Add info about the existDuring, if needed
    if organization.existsDuring:
        organization_schema.existsDuring = get_time_period_by_id(
            db=db,
            id=organization.existsDuring
        )

    # Add info about the partyCharacteristics, if needed
    organization_schema.partyCharacteristic = \
        get_party_characteristics_by_organization_id(
            db,
            organization.id
        )

    return organization_schema


def get_all_organizations(db: Session, filters: dict = {}):

    organizations = db\
        .query(models.Organization)\
        .filter_by(**filters)\
        .all()

    if len(organizations) == 0:
        return []

    organizations_standardized = []
    for organization in organizations:
        organization_schema = tmf632_party_mgmt.Organization\
            .from_orm(organization)

        # Add info about the existDuring, if needed
        if organization.existsDuring:
            organization_schema.existsDuring = get_time_period_by_id(
                db=db,
                id=organization.existsDuring
            )
        # Add info about the partyCharacteristics, if needed
        organization_schema.partyCharacteristic = \
            get_party_characteristics_by_organization_id(
                db,
                organization.id
            )

        organizations_standardized.append(organization_schema)

    return organizations_standardized


def delete_time_period(db: Session, time_period_id: int):
    return db\
        .query(models.TimePeriod)\
        .filter(models.TimePeriod.id == time_period_id)\
        .delete()


def delete_party_characteristic_by_id(db: Session, characteristic_id: int):
    return db\
        .query(models.Characteristic)\
        .filter(models.Characteristic.id == characteristic_id)\
        .delete()


def delete_party_characteristic_by_organization_id(
    db: Session,
    organization_id: int
):
    return db\
        .query(models.Characteristic)\
        .filter(models.Characteristic.organization == organization_id)\
        .delete()


def delete_organization(db: Session, organization_id: int):

    db_organization = get_organization_by_id(db, organization_id)

    # Delete Time Period
    delete_time_period(db, db_organization.id)

    # Delete partyCharacteristics
    delete_party_characteristic_by_organization_id(db_organization.id)

    # Finally, delete the organization
    db\
        .query(models.Organization)\
        .filter(models.Organization.id == organization_id)\
        .delete()
