# @Author: Rafael Direito
# @Date:   2022-08-03 18:45:14 (WEST)
# @Email:  rdireito@av.it.pt
# @Copyright: Insituto de Telecomunicações - Aveiro, Aveiro, Portugal
# @Last Modified by:   Rafael Direito
# @Last Modified time: 2022-10-21 17:01:08

# generic imports
from fastapi import FastAPI
import logging
from logging.handlers import RotatingFileHandler
from fastapi.exceptions import RequestValidationError
from http import HTTPStatus

# custom imports
from database.database import SessionLocal
from database.database import engine
from database.models import models
from routers import organizations_router
from routers import utils as RouterUtils

# Logger
logger = logging.getLogger()
logger.setLevel(logging.INFO)
ch = logging.StreamHandler()
fh = RotatingFileHandler(
    filename='./server.log',
    maxBytes=10485760,  # 10 MBytes
    backupCount=5
    )
formatter = logging.Formatter(
    "%(asctime)s - %(module)s - %(funcName)s - line:%(lineno)d " +
    "- %(levelname)s - %(message)s"
)
ch.setFormatter(formatter)
fh.setFormatter(formatter)

# Exporting logs to the screen
# logger.addHandler(ch)
# Exporting logs to a file
logger.addHandler(fh)
logger = logging.getLogger(__name__)


fast_api_tags_metadata = [
    {
        "name": "organization",
        "description": "Operations related with the organizations.",
    },
]

fast_api_description = "REST API of VPilot"

# Start Fast API
app = FastAPI(
    title="VPilot",
    description=fast_api_description,
    version="0.0.1",
    contact={
        "name": "Rafael Direito",
        "email": "rdireito@av.it.pt",
    },
    openapi_tags=fast_api_tags_metadata
)

# Load Routers
app.include_router(organizations_router.router)


# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# __init__
@app.on_event("startup")
async def startup_event():
    models.Base.metadata.create_all(bind=engine)
    pass


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request, exc):

    error_messages = [
        f"Error=(payload_location={'/'.join(error['loc'])}, " +
        f"message='{error['msg']}')"
        for error
        in exc.errors()
    ]

    logger.error("Exception Occurred in Payload's Validation: " +
                 ", ".join(error_messages))

    return RouterUtils.create_http_response(
            http_status=HTTPStatus.BAD_REQUEST,
            content=RouterUtils.compose_error_payload(
                code=HTTPStatus.BAD_REQUEST,
                reason=", ".join(error_messages),
            )
        )