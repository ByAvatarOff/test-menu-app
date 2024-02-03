"""
Pytest utils
"""
from typing import Callable

from main import app


async def reverse(
        foo: Callable,
        **kwargs
) -> str:
    """Get router name and return url for this router"""
    return app.url_path_for(foo.__name__, **kwargs)
