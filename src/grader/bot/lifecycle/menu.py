from aiogram.types import BotCommand

from grader.bot.lifecycle.creator import bot


async def SetMenu() -> None:
    commands = [
        BotCommand(command="/start", description="Меню"),
        BotCommand(command="/cancel", description="Отменить действие"),
    ]

    await bot.set_my_commands(commands)
