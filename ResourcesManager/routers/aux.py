# -*- coding: utf-8 -*-
# @Author: Rafael Direito
# @Date:   2022-10-20 18:16:45
# @Last Modified by:   Rafael Direito
# @Last Modified time: 2022-10-29 16:40:41

from typing import Optional
from fastapi import (
    Query,
    HTTPException,
    status,
)
from fastapi.params import Query as QueryParam
from database.models.models import Organization
from aux.constants import IDP_ADMIN_USER


class GetOrganizationFilters:
    def __init__(
        self,
        href: Optional[str] = Query(default=None),
        isHeadOffice: Optional[bool] = Query(default=None),
        isLegalEntity: Optional[bool] = Query(default=None),
        name: Optional[str] = Query(default=None),
        nameType: Optional[str] = Query(default=None),
        organizationType: Optional[str] = Query(default=None),
        tradingName: Optional[str] = Query(default=None),
        contactMedium: Optional[int] = Query(
            default=None,
            alias="contactMedium.id"
        ),
        creditRating: Optional[int] = Query(
            default=None,
            alias="creditRating.id"
        ),
        existsDuring: Optional[int] = Query(
            default=None,
            alias="existsDuring.id"
        ),
        externalReference: Optional[int] = Query(
            default=None,
            alias="externalReference.id"
        ),
        organizationChildRelationship: Optional[int] = Query(
            default=None,
            alias="organizationChildRelationship.id"
        ),
        organizationIdentification: Optional[int] = Query(
            default=None,
            alias="organizationIdentification.id"
        ),
        organizationParentRelationship: Optional[int] = Query(
            default=None,
            alias="organizationParentRelationship.id"
        ),
        otherName: Optional[int] = Query(
            default=None,
            alias="organizationParentRelationship.id"
        ),
        partyCharacteristic: Optional[int] = Query(
            default=None,
            alias="partyCharacteristic.id"
        ),
        relatedParty: Optional[int] = Query(
            default=None,
            alias="relatedParty.id"
        ),
        status: Optional[str] = Query(
            default=None,
            regex="^(initialized|validated|closed){1}$"
        ),
        taxExemptionCertificate: Optional[int] = Query(
            default=None,
            alias="taxExemptionCertificate.id"
        )
    ):
        self.href = href
        self.isHeadOffice = isHeadOffice
        self.isLegalEntity = isLegalEntity
        self.name = name
        self.nameType = nameType
        self.organizationType = organizationType
        self.tradingName = tradingName
        self.contactMedium = contactMedium
        self.creditRating = creditRating
        self.existsDuring = existsDuring
        self.externalReference = externalReference
        self.organizationChildRelationship = organizationChildRelationship
        self.organizationIdentification = organizationIdentification
        self.organizationParentRelationship = organizationParentRelationship
        self.otherName = otherName
        self.partyCharacteristic = partyCharacteristic
        self.relatedParty = relatedParty
        self.status = status
        self.taxExemptionCertificate = taxExemptionCertificate


def filter_organization_fields(allowed_fields, organization):
    if not allowed_fields:
        return organization

    for key in set(organization.keys()).difference(set(allowed_fields)):
        del organization[key]

    return organization


def parse_organization_query_filters(filter: GetOrganizationFilters):
    return {
        filter_key: filter_value
        for filter_key, filter_value in filter.__dict__.items()
        if
        filter_value
        and not isinstance(filter_value, QueryParam)
        and filter_key in Organization.__table__.columns.keys()
    }


def check_if_user_is_authorized_to_access_an_organization(user, organization):
    if IDP_ADMIN_USER not in user.roles:
        if user.sub not in [
            authorized_user.user_id
            for authorized_user
            in organization.authorizedUsersParsed
        ]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail='User not authorized to access data ' +
                f'related with organization {organization.id}',
            )
