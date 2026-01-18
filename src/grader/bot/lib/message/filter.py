from aiogram import types
from aiogram.filters import Filter

from grader.core.configs.constants import ADMIN_CHAT_IDS
from grader.db.models.user import User
from grader.services.user import UserService


class AdminFilter(Filter):
    async def __call__(self, message: types.Message) -> bool:
        return message.chat.id in ADMIN_CHAT_IDS


class VerifiedFilter(Filter):
    async def __call__(self, message: types.Message) -> bool:
        srv = UserService.Create()

        verified = await srv.GetUser(
            chat_id=message.chat.id,
            column=User.verified,
        )

        return verified if verified else False


class HasReferenceFilter(Filter):
    async def __call__(self, message: types.Message) -> bool:
        srv = UserService.Create()

        has_reference = await srv.GetUser(
            chat_id=message.chat.id,
            column=User.has_reference,
        )
        assert has_reference is not None
        return has_reference
