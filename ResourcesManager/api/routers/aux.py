# -*- coding: utf-8 -*-
# @Author: Rafael Direito
# @Date:   2022-10-20 18:16:45
# @Last Modified by:   Rafael Direito
# @Last Modified time: 2022-11-03 13:19:48

# general imports
from fastapi import (
    Query,
    HTTPException,
    status,
)
from fastapi.params import Query as QueryParam
from fastapi.responses import JSONResponse
from http import HTTPStatus
import logging
from typing import (
    Any,
    Optional
)

# custom imports
from database.crud import exceptions as CRUDExceptions
from database.models import models
from aux.constants import IDP_ADMIN_USER
from schemas import (
    tmf632_party_mgmt as TMF632,
    authorized_users as AuthorizedUsersSchemas
)

# Logger
logger = logging.getLogger(__name__)


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
        and filter_key in models.Organization.__table__.columns.keys()
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


def compose_error_payload(code: str, reason: str, message: str = None,
                          status: str = None, reference_error: str = None,
                          base_type: str = None, schema_location: str = None,
                          type: str = None):

    payload = {
        "code": code,
        "reason": reason,
    }

    if message:
        payload["message"] = message
    if status:
        payload["status"] = message
    if reference_error:
        payload["referenceError"] = message
    if message:
        payload["message"] = message
    if base_type:
        payload["@baseType"] = message
    if schema_location:
        payload["@schemaLocation"] = message
    if type:
        payload["@type"] = message

    return payload


def create_http_response(http_status: HTTPStatus = HTTPStatus.OK,
                         content: Any = {}):
    return JSONResponse(
        status_code=http_status.value,
        content=content,
        # headers={"Access-Control-Allow-Origin": "*"}
        )


def organization_to_organization_schema(organization: models.Organization):

    # Parse Organization Model to TMF632 Organization Schema
    schema = TMF632.Organization.from_orm(organization)

    # Add TimePeriod, if needed
    if organization.existsDuringParsed:
        schema.existsDuring = TMF632.TimePeriod\
            .from_orm(organization.existsDuringParsed)

    # Add Characteristics, if needed
    schema.partyCharacteristic = []
    for pc in organization.partyCharacteristicParsed:
        schema.partyCharacteristic.append(
            TMF632.Characteristic.from_orm(pc)
        )

    return schema


def organization_authorized_users_to_schema(organization: models.Organization):
    return AuthorizedUsersSchemas.OrganizationAuthorizedUsers(
        organization_id=organization.id,
        authorized_users=[
            AuthorizedUsersSchemas.AuthorizedUser(user_id=user.user_id)
            for user
            in organization.authorizedUsersParsed
        ]
    )


def exception_to_http_response(exception):
    logger.error(f"The following exception was raised: {exception}")

    if isinstance(exception, CRUDExceptions.ImpossibleToCreateDatabaseEntry):
        return create_http_response(
            http_status=HTTPStatus.INTERNAL_SERVER_ERROR,
            content=compose_error_payload(
                code=HTTPStatus.INTERNAL_SERVER_ERROR,
                reason=exception.reason,
            )
        )
    elif isinstance(exception, CRUDExceptions.EntityDoesNotExist):
        return create_http_response(
            http_status=HTTPStatus.BAD_REQUEST,
            content=compose_error_payload(
                code=HTTPStatus.BAD_REQUEST,
                reason=exception.reason,
            )
        )
    elif isinstance(exception, HTTPException):
        return create_http_response(
            http_status=HTTPStatus.FORBIDDEN,
            content=compose_error_payload(
                code=HTTPStatus.FORBIDDEN,
                reason=exception.detail,
            )
        )
    else:
        return create_http_response(
            http_status=HTTPStatus.INTERNAL_SERVER_ERROR,
            content=compose_error_payload(
                code=HTTPStatus.INTERNAL_SERVER_ERROR,
                reason=str(exception),
            )
        )
