from fastapi import FastAPI, HTTPException, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse


def register_exception_handlers(app: FastAPI):
    """
    Register all global exception handlers.
    """

    @app.exception_handler(HTTPException)
    async def http_exception_handler(
        request: Request,
        exc: HTTPException
    ):
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "code": exc.status_code,
                "status": "error",
                "message": exc.detail,
                "data": None
            }
        )

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(
        request: Request,
        exc: RequestValidationError
    ):
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content={
                "code": 422,
                "status": "error",
                "message": "Validation failed.",
                "data": exc.errors()
            }
        )

    @app.exception_handler(Exception)
    async def global_exception_handler(
        request: Request,
        exc: Exception
    ):
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "code": 500,
                "status": "error",
                "message": "Internal server error.",
                "data": None
            }
        )