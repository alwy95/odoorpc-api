from fastapi import HTTPException, status
from fastapi.exceptions import RequestValidationError, ResponseValidationError
from fastapi.responses import JSONResponse

from core.logger import log
from core.types import ResponseStatus


def handling_exception(app):
    """Register global exception handlers for consistent API error responses."""
    @app.exception_handler(RequestValidationError)
    def request_validation_handler(req, exc: RequestValidationError):
        """Handle Pydantic validation errors for incoming request data."""
        msg = exc.errors()[0]["msg"]
        code = status.HTTP_422_UNPROCESSABLE_ENTITY

        log.error(msg, code)

        return JSONResponse(
            status_code=code, content={"status": ResponseStatus.ERROR, "message": msg}
        )

    @app.exception_handler(ResponseValidationError)
    def response_validation_handler(req, exc: ResponseValidationError):
        """Handle internal server errors when the API response fails validation."""
        msg = exc.errors()[0]["msg"]
        code = status.HTTP_500_INTERNAL_SERVER_ERROR

        log.error(msg, code)

        return JSONResponse(
            status_code=code, content={"status": ResponseStatus.ERROR, "message": msg}
        )

    @app.exception_handler(HTTPException)
    def http_exception_handler(req, exc: HTTPException):
        """Handle explicit FastAPI HTTPExceptions (e.g., 404, 401)."""
        msg = exc.detail
        code = exc.status_code

        log.error(msg, code)

        return JSONResponse(
            status_code=code, content={"status": ResponseStatus.ERROR, "message": msg}
        )

    @app.exception_handler(Exception)
    def exception_handler(req, exc: Exception):
        """Handle unexpected system errors and prevent sensitive data leaks."""
        msg = "Something went wrong"
        code = status.HTTP_500_INTERNAL_SERVER_ERROR

        log.error(msg, code)

        return JSONResponse(
            status_code=code,
            content={
                "status": ResponseStatus.ERROR,
                "message": msg,
            },
        )
