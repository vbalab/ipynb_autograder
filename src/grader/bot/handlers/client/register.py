from aiogram import Dispatcher

from grader.bot.handlers.client.commands import start


def RegisterClientHandlers(dp: Dispatcher) -> None:
    dp.include_routers(
        # order matters
        start.router,
    )
