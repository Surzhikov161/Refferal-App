import re

from fastapi import HTTPException
from sqlalchemy import Column, ForeignKey, Integer, String, Table
from sqlalchemy.orm import relationship, validates
from starlette import status

from app.database.database import Base


def check_email(email: str):
    pattern = re.compile(
        r"([A-Za-z0-9]+[.-_])*[A-Za-z0-9]+@[A-Za-z0-9-]+(\.[A-Z|a-z]{2,})+"
    )
    try:
        assert re.fullmatch(pattern, email)
        return email
    except AssertionError:
        email_validation_exception = HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Invalid email",
        )
        raise email_validation_exception


class Users(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    username = Column(String(50), nullable=False, unique=True)
    password = Column(String(), nullable=False, unique=True)
    email = Column(String(40), nullable=False, unique=True)
    ref_users = relationship(
        "Users",
        secondary="refferals",
        primaryjoin="Users.id==refferals.c.user_id",
        secondaryjoin="Users.id==refferals.c.ref_id==id",
        back_populates="ref_users",
        lazy="joined",
        join_depth=2,
    )
    refferal_code = relationship(
        "RefferalCode",
        cascade="all, delete-orphan",
        backref="user",
        lazy="selectin",
        uselist=False,
    )

    @validates("email")
    def validate_email(self, key, value):
        return check_email(value)

    @validates("username")
    def validate_username(self, key, value):
        try:
            assert len(value) >= 5
            return value
        except AssertionError:
            username_validation_exception = HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="username length must be 5 or above.",
            )
            raise username_validation_exception


class RefferalCode(Base):
    __tablename__ = "refferal_code"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    code = Column(String(), unique=True)


refferals = Table(
    "refferals",
    Base.metadata,
    Column(
        "user_id",
        Integer,
        ForeignKey(Users.id),
        primary_key=True,
    ),
    Column(
        "ref_id",
        Integer,
        ForeignKey(Users.id),
        primary_key=True,
    ),
)
