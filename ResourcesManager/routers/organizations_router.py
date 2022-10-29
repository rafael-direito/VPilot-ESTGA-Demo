# @Author: Rafael Direito
# @Date:   2022-08-03 18:45:14 (WEST)
# @Email:  rdireito@av.it.pt
# @Copyright: Insituto de Telecomunicações - Aveiro, Aveiro, Portugal
# @Last Modified by:   Rafael Direito
# @Last Modified time: 2022-10-29 16:42:23

# generic imports
from fastapi import (
    APIRouter,
    Depends,
    Query,
    HTTPException,
)
from fastapi.encoders import jsonable_encoder
from sqlalchemy.orm import Session
from database.crud import crud
from http import HTTPStatus
from typing import Optional
import logging

# custom imports
from routers import utils as Utils
import database.crud.exceptions as CRUDExceptions
import schemas.tmf632_party_mgmt as TMF632Schemas
import schemas.authorized_users as AuthorizedUsersSchemas
from idp.idp import idp
import main
from routers.aux import (
    GetOrganizationFilters,
    filter_organization_fields,
    parse_organization_query_filters,
    check_if_user_is_authorized_to_access_an_organization
)
from aux.constants import (
    IDP_ADMIN_USER,
    IDP_TESTBED_ADMIN_USER,
)

# Logger
logger = logging.getLogger(__name__)


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
    db: Session = Depends(get_db),
    user=Depends(idp.get_current_user(required_roles=[IDP_ADMIN_USER]))
):
    try:
        organization = crud.create_organization(db, organization)

        return Utils.create_http_response(
            http_status=HTTPStatus.CREATED,
            # Return parsed
            content=jsonable_encoder(
                Utils.organization_to_organization_schema(organization)
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
    db: Session = Depends(get_db),
    user=Depends(idp.get_current_user(required_roles=[IDP_TESTBED_ADMIN_USER]))
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
            else:
                # If the user is not also an admin user, we have to verify if
                # it has the permissions to get the organization he requested
                # If the user doesn't possess the needed permissions, this
                # function will raise an exception and the method will return a
                # 403 FORBIDDEN
                check_if_user_is_authorized_to_access_an_organization(
                    user=user,
                    organization=organizations[0]
                )

        # Operations for when the client requests all organization
        else:
            organizations = crud.get_all_organizations(db, filter_dict)

        # Parse to Pydantic Model
        tmf632_organizations = []
        for organization in organizations:
            if organization != {}:
                tmf632_organizations.append(
                    Utils.organization_to_organization_schema(organization)
                )
            else:
                tmf632_organizations.append(organization)

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
    # Propagate HTTP exceptions
    except HTTPException as exception:
        raise exception
    # For other exceptions
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
async def delete_organization(
    id: Optional[int] = None,
    db: Session = Depends(get_db),
    user=Depends(idp.get_current_user(required_roles=[IDP_ADMIN_USER]))
):
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
async def update_organization(
    id: int,
    organization: TMF632Schemas.OrganizationCreate,
    db: Session = Depends(get_db),
    user=Depends(idp.get_current_user(required_roles=[IDP_TESTBED_ADMIN_USER]))
):
    try:
        current_organization = crud.get_organization_by_id(db, id)
        # If the user is not also an admin user, we have to verify if
        # it has the permissions to get the organization he requested
        # If the user doesn't possess the needed permissions, this
        # function will raise an exception and the method will return a
        # 403 FORBIDDEN

        check_if_user_is_authorized_to_access_an_organization(
            user=user,
            organization=current_organization
        )

        updated_organization = crud.update_organization(db, id, organization)

        # Response
        return Utils.create_http_response(
                http_status=HTTPStatus.OK,
                # Parse Organization to TM632 Organization
                # And encode it
                content=jsonable_encoder(
                    Utils.organization_to_organization_schema(
                        updated_organization
                    )
                )
        )
    # The user tried to update and organization that doesn't exist
    except CRUDExceptions.EntityDoesNotExist as exception:
        return Utils.create_http_response(
            http_status=HTTPStatus.BAD_REQUEST,
            content=Utils.compose_error_payload(
                code=HTTPStatus.BAD_REQUEST,
                reason=exception.reason,
            )
        )
    # Something wrong happened durin the organization update
    except CRUDExceptions.ImpossibleToCreateDatabaseEntry as exception:
        return Utils.create_http_response(
            http_status=HTTPStatus.INTERNAL_SERVER_ERROR,
            content=Utils.compose_error_payload(
                code=HTTPStatus.INTERNAL_SERVER_ERROR,
                reason=exception.reason,
            )
        )
    # Propagate HTTP exceptions
    except HTTPException as exception:
        return Utils.create_http_response(
            http_status=HTTPStatus.FORBIDDEN,
            content=Utils.compose_error_payload(
                code=HTTPStatus.FORBIDDEN,
                reason=exception.detail,
            )
        )
    # For other exceptions
    except Exception as exception:
        return Utils.create_http_response(
            http_status=HTTPStatus.INTERNAL_SERVER_ERROR,
            content=Utils.compose_error_payload(
                code=HTTPStatus.INTERNAL_SERVER_ERROR,
                reason=str(exception),
            )
        )


@router.get(
    "/organization/{id}/authorized-users",
    tags=["organization"],
    summary="Lists all Organization's Authorized Users",
    description="This operation list or find all Organization's " +
    "Authorized Users.",
    response_model=AuthorizedUsersSchemas.OrganizationAuthorizedUsers,
)
async def get_organization_authorized_users(
    id: int = None,
    db: Session = Depends(get_db),
    user=Depends(idp.get_current_user(required_roles=[IDP_TESTBED_ADMIN_USER]))
):
    try:
        # Operations for when the client requests a specific organization
        # These operations ignore all query filters, since the organization is
        # already 'filtered' using its id

        # Get the organization, if it exists. Else, raise exception
        organization = crud.get_organization_by_id(db, id)
        if not organization:
            raise CRUDExceptions.EntityDoesNotExist(
                entity_type="Organization",
                reason="The requested organization doesn't exist."
            )

        # If the user is not also an admin user, we have to verify if
        # it has the permissions to get the organization he requested
        # If the user doesn't possess the needed permissions, this
        # function will raise an exception and the method will return a
        # 403 FORBIDDEN
        print("---")
        check_if_user_is_authorized_to_access_an_organization(
            user=user,
            organization=organization
        )
        print("---")

        # Response
        return Utils.create_http_response(
                http_status=HTTPStatus.OK,
                content=jsonable_encoder(
                    Utils.organization_authorized_users_to_schema(
                        organization=organization
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
    # Propagate HTTP exceptions
    except HTTPException as exception:
        return Utils.create_http_response(
            http_status=HTTPStatus.FORBIDDEN,
            content=Utils.compose_error_payload(
                code=HTTPStatus.FORBIDDEN,
                reason=exception.detail,
            )
        )
    # Propagate exception
    except CRUDExceptions.EntityDoesNotExist as exception:
        return Utils.create_http_response(
            http_status=HTTPStatus.BAD_REQUEST,
            content=Utils.compose_error_payload(
                code=HTTPStatus.BAD_REQUEST,
                reason=exception.reason,
            )
        )
    # For other exceptions
    except Exception as exception:
        return Utils.create_http_response(
            http_status=HTTPStatus.INTERNAL_SERVER_ERROR,
            content=Utils.compose_error_payload(
                code=HTTPStatus.INTERNAL_SERVER_ERROR,
                reason=str(exception),
            )
        )
# @router.get("/user")  # Requires logged in
# def current_users(user: OIDCUser = Depends(idp.get_current_user())):
#     return user
#
# @router.get("/admin")  # Requires the admin role
# def company_admin(user=Depends(idp.get_current_user(
#     required_roles=["VPilot-Admin"]
#     ))):
#     print(user)
#     print(user.sub)
#     print(user.preferred_username)
#     print(user.roles)
#     print(user.extra_fields)
#     return f'Hi admin {user}'
# @router.get("/login")
# def login_redirect():
#     return RedirectResponse(idp.login_uri)
#
# @router.get("/callback")
# def callback(session_state: str, code: str):
#     # This will return an access token
#     return idp.exchange_authorization_code(
#         session_state=session_state,
#         code=code
#     )
#
#
# @router.post("/login2", tags=["example-user-request"])
# def login(user: UsernamePassword = Body(...)):
#     return idp.user_login(
#         username=user.username, password=user.password.get_secret_value()
#     )
