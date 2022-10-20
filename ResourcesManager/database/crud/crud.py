# -*- coding: utf-8 -*-
# @Author: Rafael Direito
# @Date:   2022-10-17 12:00:16
# @Last Modified by:   Rafael Direito
# @Last Modified time: 2022-10-20 10:01:16

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


def create_organization(db: Session,
                        organization: tmf632_party_mgmt.Organization):

    # Try to create a new TimePeriod DB Entry
    time_period_id = None
    if organization.existsDuring:
        time_period = create_time_period(db, organization.existsDuring)
        time_period_id = time_period.id

    # Check if a status was assigned to the organization
    status_value = None
    if organization.status:
        status_value = organization.status.value

    # Create the organization
    try:
        created_organization = models.Organization(
            isHeadOffice=organization.isHeadOffice,
            isLegalEntity=organization.isLegalEntity,
            name=organization.name,
            nameType=organization.nameType,
            organizationType=organization.organizationType,
            tradingName=organization.tradingName,
            existsDuring=time_period_id,
            status=status_value,
            _baseType=None,
            _schemaLocation=None,
            _type=None
        )

        db.add(created_organization)
        db.commit()
        db.refresh(created_organization)
        logger.info(f"Organization created: {created_organization.as_dict()}")
        return created_organization

    except Exception as e:
        raise ImpossibleToCreateDatabaseEntry(
            entity_type="Organization",
            entity_data=str(organization),
            reason=str(e)
        )


def get_time_period_by_id(db: Session, id: int):
    time_period = db\
        .query(models.TimePeriod)\
        .filter(models.TimePeriod.id == id)\
        .first()

    if not time_period:
        return

    return tmf632_party_mgmt.TimePeriod.from_orm(time_period)


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

    return organization_schema


def get_all_organizations(db: Session):
    organizations = db\
        .query(models.Organization)\
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

        organizations_standardized.append(organization_schema)

    return organizations_standardized