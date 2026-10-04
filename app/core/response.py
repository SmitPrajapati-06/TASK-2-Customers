from typing import Any

from app.schemas.common import ResponseStatus


def success_response(
    *,
    code: int,
    message: str,
    data: Any = None,
) -> dict:
    return {
        "code": code,
        "status": ResponseStatus.SUCCESS,
        "message": message,
        "data": data,
    }