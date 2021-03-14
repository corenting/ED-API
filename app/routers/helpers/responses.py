from dataclasses import asdict
from functools import wraps
from typing import Any, Callable, Dict, Generator, Union


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
