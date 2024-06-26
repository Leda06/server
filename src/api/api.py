# Standard library imports
from typing import List, Optional

# Related third party imports
from fastapi import APIRouter, Depends
from pydantic import BaseModel
from starlette.responses import JSONResponse

# Local application/library specific imports
from auth.service import get_index_id

# Local application/library specific imports
from users.controller import router as user_router
from extract.controller import router as extract_router
from workflows.controller import router as workflow_router
from generate.controller import router as generate_router
from embed.controller import router as embed_router
from pipelines.controller import router as pipeline_router
from storage.controller import router as storage_router

api_router = APIRouter()


class ErrorMessage(BaseModel):
    msg: str


class ErrorResponse(BaseModel):
    detail: Optional[List[ErrorMessage]]


api_router = APIRouter(
    default_response_class=JSONResponse,
    responses={
        400: {"model": ErrorResponse},
        401: {"model": ErrorResponse},
        403: {"model": ErrorResponse},
        404: {"model": ErrorResponse},
        500: {"model": ErrorResponse},
    },
)


# unauthenticated
api_router.include_router(user_router, prefix="/users", tags=["Users"])

# authenticated
# fmt: off
api_router.include_router(extract_router, prefix="/extract", tags=["Extract"], dependencies=[Depends(get_index_id)])
api_router.include_router(generate_router, prefix="/generate", tags=["Generate"], dependencies=[Depends(get_index_id)])
api_router.include_router(embed_router, prefix="/embed", tags=["Embed"], dependencies=[Depends(get_index_id)])

api_router.include_router(pipeline_router, prefix="/pipelines", tags=["Pipelines"], dependencies=[Depends(get_index_id)])
api_router.include_router(workflow_router, prefix="/workflows", tags=["Workflows"], dependencies=[Depends(get_index_id)])
api_router.include_router(storage_router, prefix="/storage", tags=["Storage"], dependencies=[Depends(get_index_id)])


# fmt: on
@api_router.get("/", include_in_schema=False)
def hello_world():
    return {
        "message": "welcome to the Mixpeek api, check out the docs for more: docs.mixpeek.com"
    }


@api_router.get("/healthcheck", include_in_schema=False)
def healthcheck():
    return {"status": "ok"}
