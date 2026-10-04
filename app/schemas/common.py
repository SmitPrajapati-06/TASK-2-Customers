from enum import Enum
from typing import Generic, TypeVar

from pydantic import BaseModel
from pydantic.generics import GenericModel


T = TypeVar("T")


class ResponseStatus(str, Enum):
    SUCCESS = "success"
    ERROR = "error"


class ApiResponse(GenericModel, Generic[T]):
    code: int
    status: ResponseStatus
    message: str
    data: T | None = None