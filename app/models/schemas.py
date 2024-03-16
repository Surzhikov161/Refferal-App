from typing import List, Optional

from pydantic import BaseModel


class BaseUser(BaseModel):
    username: str
    email: str
    password: str
    refferal_code: Optional[str] = None


class ActiveUser(BaseModel):
    username: str
    email: Optional[str]
    disabled: Optional[bool] = None


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: Optional[str] = None


class ReturnModel(BaseModel):
    result: bool
    msg: str


class ReturnRefCode(BaseModel):
    refferal_code: Optional[str]


class Refferal(BaseModel):
    id: int
    username: str


class ReturnRefferals(BaseModel):
    refferals: List["Refferal"]
