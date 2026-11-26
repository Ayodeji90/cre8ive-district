"""Shared response wrappers."""

from pydantic import BaseModel


class Page[T](BaseModel):
    items: list[T]
    total: int
    page: int
    limit: int


class MessageResponse(BaseModel):
    message: str
