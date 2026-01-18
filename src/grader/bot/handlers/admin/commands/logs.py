from aiogram import Router, types
from aiogram.filters.command import Command

from grader.bot.lib.message.filter import AdminFilter
from grader.bot.lib.message.io import SendDocument
from grader.core.configs.paths import PATH_BOT_LOGS

router = Router()


@router.message(Command("logs"), AdminFilter())
async def CommandLogs(message: types.Message) -> None:
    await SendDocument(
        chat_id=message.chat.id, document=types.FSInputFile(PATH_BOT_LOGS)
    )
