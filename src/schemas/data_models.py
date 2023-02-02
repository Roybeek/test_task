from typing import List

from pydantic import BaseModel

__all__ = (
    'TestObject',
    'TestData',
)


class TestObject(BaseModel):
    name: str


class TestData(BaseModel):
    id: str
    level: int
    objects: List[TestObject]
