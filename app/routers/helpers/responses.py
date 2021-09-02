from dataclasses import asdict
from functools import wraps
from typing import Any, Callable, Dict, Generator, Type, Union

from app.routers.error_responses import HTTPError


def dataclass_response(original_func: Callable) -> Callable:
    """Wrap a function returning a dataclass to return dicts.

    As needed for an API function for FastAPI.
    """

    @wraps(original_func)
    async def wrapped_func(
        *args: Any, **kwargs: Any
    ) -> Union[Generator[Dict, None, None], Dict]:

        res = await original_func(*args, **kwargs)

        # Check if iterable
        iterable = True
        try:
            _ = iter(res)
        except TypeError:
            iterable = False

        return (asdict(x) for x in res) if iterable else asdict(res)

    return wrapped_func


def get_error_response_doc(status_code: int, exception: Type[Exception]) -> Dict:
    """Get the OpenAPI documentation for an exception to use in FastAPI doc decorator."""
    error_code = getattr(exception, "error_code", "Unknown error")

    return {
        status_code: {
            "detail": error_code,
            "content": {
                "application/json": {"example": HTTPError(detail=error_code).json()}
            },
        }
    }
