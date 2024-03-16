import re

from sqlalchemy import Column, ForeignKey, Integer, String, Table
from sqlalchemy.orm import relationship, validates

from app.database.database import Base


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
        pattern = re.compile(
            r"([A-Za-z0-9]+[.-_])*[A-Za-z0-9]+@[A-Za-z0-9-]+(\.[A-Z|a-z]{2,})+"
        )
        assert re.fullmatch(pattern, value)
        return value


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
