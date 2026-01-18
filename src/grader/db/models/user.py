from __future__ import annotations

from sqlalchemy import BigInteger, Boolean, Text
from sqlalchemy.orm import Mapped, mapped_column

from grader.db.base import Base
from grader.db.models.common.time import TimestampMixin


class User(Base, TimestampMixin):
    __tablename__ = "users"

    # --- primary key ---
    chat_id: Mapped[int] = mapped_column(
        BigInteger,
        primary_key=True,
    )

    # --- secondary keys ---
    username: Mapped[str | None] = mapped_column(
        Text,
        index=True,
        nullable=True,
    )
    phone_number: Mapped[str | None] = mapped_column(
        Text,
        index=True,
        nullable=True,
    )

    # --- reference ipynb ---
    has_reference: Mapped[bool] = mapped_column(
        nullable=True,
        default=False,
    )

    # --- state ---
    verified: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
    )
    blocked: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
    )
