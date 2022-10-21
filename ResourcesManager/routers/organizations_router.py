# @Author: Rafael Direito
# @Date:   2022-08-03 18:45:14 (WEST)
# @Email:  rdireito@av.it.pt
# @Copyright: Insituto de Telecomunicações - Aveiro, Aveiro, Portugal
# @Last Modified by:   Rafael Direito
# @Last Modified time: 2022-10-21 11:50:56

# generic imports
from sqlalchemy.orm import Session
from fastapi import APIRouter, Depends, Query
from database.crud import crud
from http import HTTPStatus
from fastapi.encoders import jsonable_encoder
from typing import Optional

# custom imports
from routers import utils as Utils
import database.crud.exceptions as CRUDExceptions
import schemas.tmf632_party_mgmt as TMF632Schemas
import main
from routers.aux import GetOrganizationFilters
from routers.aux import filter_organization_fields
from routers.aux import parse_organization_query_filters

router = APIRouter()


# Dependency
def get_db():
    return next(main.get_db())


@router.post(
    "/organization/",
    tags=["organization"],
    summary="Creates a Organization",
    description="This operation creates a Organization entity.",
    responses={
    }
)
async def create_organization(
    organization: TMF632Schemas.OrganizationCreate,
    db: Session = Depends(get_db)
):
    try:
        created_organization = crud.create_organization(db, organization)

        return Utils.create_http_response(
            http_status=HTTPStatus.CREATED,
            content=jsonable_encoder(
                crud.get_organization_by_id(
                    db=db,
                    id=created_organization.id
                )
            )
        )

    except CRUDExceptions.ImpossibleToCreateDatabaseEntry as exception:
        return Utils.create_http_response(
            http_status=HTTPStatus.INTERNAL_SERVER_ERROR,
            content=Utils.compose_error_payload(
                code=HTTPStatus.INTERNAL_SERVER_ERROR,
                reason=exception.reason,
            )
        )
    except Exception as exception:
        return Utils.create_http_response(
            http_status=HTTPStatus.INTERNAL_SERVER_ERROR,
            content=Utils.compose_error_payload(
                code=HTTPStatus.INTERNAL_SERVER_ERROR,
                reason=str(exception),
            )
        )


@router.get(
    "/organization/",
    tags=["organization"],
    summary="List or find Organization objects",
    description="This operation list or find Organization entities",
    response_model=list[TMF632Schemas.Organization],
)
@router.get(
    "/organization/{id}",
    tags=["organization"],
    summary="List or find Organization objects",
    description="This operation list or find Organization entities",
    response_model=list[TMF632Schemas.Organization],
)
async def get_organization(
    id: Optional[int] = None,
    fields: Optional[str] = Query(
        default=None,
        regex="^(("
        + '|'.join(TMF632Schemas.Organization.__fields__.keys())
        + ")(,)?)+$"
    ),
    filter: GetOrganizationFilters = Depends(),
    db: Session = Depends(get_db)
):
    try:
        # Parse all query parameters
        fields = fields.split(",") if fields else None
        filter_dict = parse_organization_query_filters(filter)

        # Operations for when the client requests a specific organization
        # These operations ignore all query filters, since the organization is
        # already 'filtered' using its id
        if id:
            organizations = [crud.get_organization_by_id(db, id)]
            if not organizations[0]:
                organizations[0] = {}
        # Operations for when the client requests all organization
        else:
            organizations = crud.get_all_organizations(db, filter_dict)

        # General workflow for all requests

        # Parse to dict
        encoded_organizations = jsonable_encoder(organizations)
        # Apply 'fields' filter
        encoded_organizations = [
            filter_organization_fields(fields, encoded_organization)
            for encoded_organization
            in encoded_organizations
        ]

        # Response
        return Utils.create_http_response(
                http_status=HTTPStatus.OK,
                content=encoded_organizations[0]
                if id
                else encoded_organizations
        )

    except CRUDExceptions.ImpossibleToCreateDatabaseEntry as exception:
        return Utils.create_http_response(
            http_status=HTTPStatus.INTERNAL_SERVER_ERROR,
            content=Utils.compose_error_payload(
                code=HTTPStatus.INTERNAL_SERVER_ERROR,
                reason=exception.reason,
            )
        )
    except Exception as exception:
        return Utils.create_http_response(
            http_status=HTTPStatus.INTERNAL_SERVER_ERROR,
            content=Utils.compose_error_payload(
                code=HTTPStatus.INTERNAL_SERVER_ERROR,
                reason=str(exception),
            )
        )
