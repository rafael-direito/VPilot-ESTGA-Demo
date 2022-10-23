# @Author: Rafael Direito
# @Date:   2022-08-03 18:45:14 (WEST)
# @Email:  rdireito@av.it.pt
# @Copyright: Insituto de Telecomunicações - Aveiro, Aveiro, Portugal
# @Last Modified by:   Rafael Direito
# @Last Modified time: 2022-10-23 18:04:29

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
        organization = crud.create_organization(db, organization)

        # Parse Organization to TM632 Organization
        tmf632_organization = Utils.organization_to_organization_schema(
            db=db,
            organization=organization
        )

        return Utils.create_http_response(
            http_status=HTTPStatus.CREATED,
            content=jsonable_encoder(tmf632_organization)
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
    description="This operation list or find Organization entities.",
    response_model=list[TMF632Schemas.Organization],
)
@router.get(
    "/organization/{id}",
    tags=["organization"],
    summary="List or find Organization objects",
    description="This operation list or find Organization entities.",
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
        # Parse Organization to TM632 Organization
        tmf632_organizations = [
            Utils.organization_to_organization_schema(
                db=db,
                organization=organization
            )
            if organization != {}
            else {}
            for organization
            in organizations
        ]

        # Apply 'fields' filter and encode/parse to dict
        encoded_organizations = [
            filter_organization_fields(
                fields,
                jsonable_encoder(encoded_organization)
            )
            for encoded_organization
            in tmf632_organizations
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


@router.delete(
    "/organization/{id}",
    tags=["organization"],
    summary="Deletes a Organization",
    description="This operation deletes a Organization entity.",
)
async def delete_organization(id: Optional[int] = None,
                              db: Session = Depends(get_db)):
    try:
        crud.delete_organization(db, id)
        # Response
        return Utils.create_http_response(
                http_status=HTTPStatus.NO_CONTENT
        )
    except CRUDExceptions.EntityDoesNotExist as exception:
        return Utils.create_http_response(
            http_status=HTTPStatus.BAD_REQUEST,
            content=Utils.compose_error_payload(
                code=HTTPStatus.BAD_REQUEST,
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


@router.patch(
    "/organization/{id}",
    tags=["organization"],
    summary="Updates partially a Organization",
    description="This operation updates partially a Organization entity.",
)
async def update_organization(id: int,
                              organization: TMF632Schemas.OrganizationCreate,
                              db: Session = Depends(get_db)):
    try:
        crud.update_organization(db, id, organization)
        updated_organization = crud.get_organization_by_id(db, id)

        # Parse Organization to TM632 Organization
        tmf632_organization = Utils.organization_to_organization_schema(
            db=db,
            organization=updated_organization
        )

        # Parse to dict
        encoded_organization = jsonable_encoder(tmf632_organization)

        # Response
        return Utils.create_http_response(
                http_status=HTTPStatus.OK,
                content=encoded_organization
        )
    except CRUDExceptions.EntityDoesNotExist as exception:
        return Utils.create_http_response(
            http_status=HTTPStatus.BAD_REQUEST,
            content=Utils.compose_error_payload(
                code=HTTPStatus.BAD_REQUEST,
                reason=exception.reason,
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
