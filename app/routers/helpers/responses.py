
from app.routers.error_responses import HTTPError


def get_error_response_doc(status_code: int, exception: type[Exception]) -> dict:
    """Get the OpenAPI documentation for an exception to use in FastAPI doc decorator."""
    error_code = getattr(exception, "error_code", "Unknown error")

    return {
        status_code: {
            "detail": error_code,
            "model": HTTPError,
            "content": {
                "application/json": {"example": HTTPError(detail=error_code).json()}
            },
        }
    }
