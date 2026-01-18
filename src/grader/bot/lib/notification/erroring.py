import asyncio
import logging
from typing import Any

from aiogram import types
from aiogram.fsm.context import FSMContext
from aiogram.fsm.storage.base import StorageKey
from aiogram.types.error_event import ErrorEvent

from grader.bot.lib.message.io import ContextIO, SendDocument, SendMessage
from grader.bot.lifecycle.creator import BOT_ID, dp
from grader.core.configs.constants import ADMIN_CHAT_IDS
from grader.core.configs.paths import PATH_BOT_LOGS


async def NotifyAdminsOfError(exc: BaseException) -> None:
    for admin in ADMIN_CHAT_IDS:
        await SendDocument(
            chat_id=admin,
            document=types.FSInputFile(PATH_BOT_LOGS),
            caption=f"🚨 Error: {exc}.\n\nCheck logs for details.",
        )


def AsyncioExceptionHandler(
    loop: asyncio.AbstractEventLoop, context: dict[str, Any]
) -> None:
    exc = context.get("exception") or RuntimeError(context.get("message"))

    if not loop.is_closed():
        loop.create_task(NotifyAdminsOfError(exc))

    loop.default_exception_handler(context)  # default: do own handling


@dp.error()
async def AiogramExceptionHandler(event: ErrorEvent) -> bool:
    logging.exception(
        f"Cause exception while processing update:\n{event.model_dump()}",
        exc_info=event.exception,
    )

    if event.update.message:
        chat_id = event.update.message.chat.id

        # Clear FSM state for this user
        if event.update.message.from_user:
            user_id = event.update.message.from_user.id

            key = StorageKey(bot_id=BOT_ID, chat_id=chat_id, user_id=user_id)
            context = FSMContext(storage=dp.storage, key=key)

            await context.clear()

        await SendMessage(
            chat_id,
            text="Ой, что-то пошло не так.\nМы записали ошибку.\n\nЕсли проблема не решится вскоре, свяжитесь с @vbalab",
            context=ContextIO.Error,
        )

    await NotifyAdminsOfError(event.exception)

    return True


def SetExceptionHandlers() -> None:
    asyncio.get_running_loop().set_exception_handler(AsyncioExceptionHandler)
