from aiogram import Dispatcher

from grader.bot.handlers.admin.commands import (
    admin,
    blocking,
    logs,
    send,
    senda,
)


def RegisterAdminHandlers(dp: Dispatcher) -> None:
    dp.include_routers(
        admin.router,
        logs.router,
        send.router,
        senda.router,
        blocking.router,
    )
