from aiogram import Dispatcher

from grader.bot.handlers.client.commands import start_order, start_register


def RegisterClientHandlers(dp: Dispatcher) -> None:
    dp.include_routers(
        # order matters
        start_order.router,
        start_register.router,
    )
