# -*- coding: utf-8 -*-
# @Author: Rafael Direito
# @Date:   2022-10-17 17:21:10
# @Last Modified by:   Rafael Direito
# @Last Modified time: 2022-10-29 13:48:14

from http import HTTPStatus
from fastapi.responses import JSONResponse
from typing import Any
from schemas import tmf632_party_mgmt as TMF632
from database.models import models


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
