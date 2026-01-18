import asyncio

from grader.bot.handlers.admin.register import RegisterAdminHandlers
from grader.bot.handlers.client.register import RegisterClientHandlers
from grader.bot.handlers.forall.register import (
    RegisterHandlerCancel,
    RegisterHandlerZeroMessage,
)
from grader.bot.handlers.middleware import SetBotMiddleware
from grader.bot.lib.notification import admin
from grader.bot.lib.notification.erroring import SetExceptionHandlers
from grader.bot.lib.notification.pending import ProcessPendingUpdates
from grader.bot.lifecycle.creator import bot, dp
from grader.bot.lifecycle.menu import SetMenu
from grader.core.configs.paths import EnsurePaths
from grader.core.logs import flow as logs
from grader.core.logs.bot import LoggerSetup
from grader.db.session import EnsureDB


async def EnsureDependencies() -> None:
    await EnsureDB()


async def OnStartup() -> None:
    await SetMenu()
    RegisterHandlerCancel(dp)
    RegisterAdminHandlers(dp)
    RegisterClientHandlers(dp)
    RegisterHandlerZeroMessage(dp)
    SetBotMiddleware(dp)

    await admin.NotifyOnStartup()
    await ProcessPendingUpdates()


async def OnShutdown() -> None:
    await admin.NotifyOnShutdown()

    await logs.LoggerShutdown()


async def main() -> None:
    EnsurePaths()
    await logs.LoggerStart(LoggerSetup)

    await EnsureDependencies()

    dp.startup.register(OnStartup)
    dp.shutdown.register(OnShutdown)

    SetExceptionHandlers()

    await dp.start_polling(bot, drop_pending_updates=True)


# $ python -m grader
if __name__ == "__main__":
    asyncio.run(main())
