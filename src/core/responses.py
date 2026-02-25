from typing import Generic, Optional, TypeVar

from pydantic import BaseModel

from core.types import ResponseStatus

T = TypeVar("T")


class BaseResponse(BaseModel):
    status: str = ResponseStatus.SUCCESS
    message: Optional[str] = None


class PaginationResponse(BaseResponse, Generic[T]):
    offset: int
    limit: int
    total: int
    data: list[T] | list


class ListResponse(BaseResponse, Generic[T]):
    data: list[T]


class SingleResponse(BaseResponse, Generic[T]):
    data: Optional[T]
