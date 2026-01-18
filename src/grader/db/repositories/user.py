import logging
from typing import TypeVar, overload

from sqlalchemy import select, update
from sqlalchemy.exc import IntegrityError, NoResultFound
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker
from sqlalchemy.orm.attributes import InstrumentedAttribute
from sqlalchemy.sql.elements import ColumnElement

from grader.db.models.user import User

T = TypeVar("T")


class UserRepository:
    def __init__(self, session: async_sessionmaker[AsyncSession]):
        self.session = session

    # --- Create ---
    async def CreateUser(self, chat_id: int) -> None:
        async with self.session() as session:
            try:
                session.add(User(chat_id=chat_id))

                await session.commit()
                logging.info(f"User(chat_id={chat_id}) created successfully.")

            except IntegrityError:
                await session.rollback()
                logging.error(
                    f"User(chat_id={chat_id}) already exists. Creation failed."
                )

    # --- Read ---
    @overload
    async def GetUsersOnCondition(
        self,
        condition: ColumnElement[bool] | InstrumentedAttribute[bool],
        column: None = None,
    ) -> list[User]: ...

    @overload
    async def GetUsersOnCondition(
        self,
        condition: ColumnElement[bool] | InstrumentedAttribute[bool],
        column: InstrumentedAttribute[T],
    ) -> list[T]: ...

    async def GetUsersOnCondition(
        self,
        condition: ColumnElement[bool] | InstrumentedAttribute[bool],
        column: InstrumentedAttribute[T] | None = None,
    ) -> list[User] | list[T]:
        selection = User
        if column is not None:
            selection = getattr(User, column.key)

        async with self.session() as session:
            result = await session.execute(select(selection).where(condition))

            return list(result.scalars().all())

    @overload
    async def GetUser(
        self,
        chat_id: int,
        column: None = None,
    ) -> User | None: ...

    @overload
    async def GetUser(
        self,
        chat_id: int,
        column: InstrumentedAttribute[T],
    ) -> T | None: ...

    async def GetUser(
        self,
        chat_id: int,
        column: InstrumentedAttribute[T] | None = None,
    ) -> User | T | None:
        result = await self.GetUsersOnCondition(
            condition=User.chat_id == chat_id,
            column=column,
        )
        return result[0] if result else None

    # --- Update ---
    async def UpdateUser(
        self,
        chat_id: int,
        column: InstrumentedAttribute[T],
        value: T,
    ) -> None:
        async with self.session() as session:
            result = await session.execute(
                update(User).where(User.chat_id == chat_id).values({column.key: value})
            )

            if result.rowcount == 0:
                logging.error(
                    f"Failed to update: '{column}={value}'. No User(chat_id={chat_id}) found."
                )
                raise NoResultFound()

            await session.commit()
            logging.info(
                f"User(chat_id={chat_id}) updated: '{column}={value}' successfully."
            )
