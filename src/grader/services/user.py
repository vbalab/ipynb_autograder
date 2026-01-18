from __future__ import annotations

from grader.db.models.user import User
from grader.db.repositories.user import UserRepository
from grader.db.session import AsyncSessionLocal


class UserService:
    def __init__(self, user_repo: UserRepository):
        self._user = user_repo

        # --- Create ---
        self.CreateUser = self._user.CreateUser

        # --- Read ---
        self.GetUser = self._user.GetUser

        # --- Update ---
        self.UpdateUser = self._user.UpdateUser

    # --- Read ---
    async def CheckUserExists(self, chat_id: int) -> bool:
        result = await self.GetUser(
            chat_id=chat_id,
            column=User.chat_id,
        )

        return result is not None

    async def GetVerifiedUsersChatId(self) -> list[int]:
        result = await self._user.GetUsersOnCondition(
            condition=User.verified.is_(True),
            column=User.chat_id,
        )

        return result

    async def GetChatIdByUsername(self, username: str) -> int | None:
        result = await self._user.GetUsersOnCondition(
            condition=User.username == username,
            column=User.chat_id,
        )

        return int(result[0]) if result else None

    @staticmethod
    def Create() -> UserService:
        return UserService(UserRepository(AsyncSessionLocal))
