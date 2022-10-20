# @Author: Rafael Direito
# @Date:   2022-08-03 18:45:14 (WEST)
# @Email:  rdireito@av.it.pt
# @Copyright: Insituto de Telecomunicações - Aveiro, Aveiro, Portugal
# @Last Modified by:   Rafael Direito
# @Last Modified time: 2022-10-20 10:06:19

# generic imports
from database.database import SessionLocal
from sqlalchemy.orm import Session
from fastapi import APIRouter
from fastapi import Depends
from database.crud import crud
from http import HTTPStatus
from fastapi.encoders import jsonable_encoder

# custom imports
from routers import utils as Utils
import database.crud.exceptions as CRUDExceptions
import schemas.tmf632_party_mgmt as TMF632Schemas

router = APIRouter()


# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.post(
    "/organization/",
    tags=["organization"],
    summary="Creates a Organization",
    description="This operation creates a Organization entity.",
    responses={
    }
)
async def create_organization(organization: TMF632Schemas.OrganizationCreate,
                              db: Session = Depends(get_db)):
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
async def get_organization(db: Session = Depends(get_db)):
    try:
        organizations = crud.get_all_organizations(db)
        return Utils.create_http_response(
            http_status=HTTPStatus.OK,
            content=jsonable_encoder(organizations)
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