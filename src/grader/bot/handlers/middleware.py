from collections.abc import Awaitable, Callable
from typing import Any

from aiogram import BaseMiddleware, Dispatcher
from aiogram.filters.callback_data import CallbackData
from aiogram.types import CallbackQuery, Message

from grader.bot.lib.chat.block import CheckIfBlocked
from grader.bot.lib.message.io import (
    ReceiveCallback,
    ReceiveMessage,
    SendMessage,
)
from grader.bot.lifecycle.active import bot_state


class LoggingMessageMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[Message, dict[str, Any]], Awaitable[Any]],
        message: Message,  # type: ignore[override]
        data: dict[str, Any],
    ) -> Any:
        if await CheckIfBlocked(message.chat.id):
            return

        await ReceiveMessage(message)

        return await handler(message, data)


class ClientMessageMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[Message, dict[str, Any]], Awaitable[Any]],
        message: Message,  # type: ignore[override]
        data: dict[str, Any],
    ) -> Any:
        if not bot_state.active and message.text == "/start":
            await SendMessage(
                chat_id=message.chat.id,
                text="Бот не активен.",
            )
            return

        return await handler(message, data)


class LoggingCallbackMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[CallbackQuery, dict[str, Any]], Awaitable[Any]],
        callback_query: CallbackQuery,  # type: ignore[override]
        data: dict[str, Any],
    ) -> Any:
        assert isinstance(callback_query.message, Message)

        if await CheckIfBlocked(callback_query.message.chat.id):
            await callback_query.answer()
            return

        callback_data = data.get("callback_data")
        assert isinstance(callback_data, CallbackData)

        await ReceiveCallback(
            query=callback_query,
            data=callback_data,
        )

        return await handler(callback_query, data)


class ClientCallbackMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[CallbackQuery, dict[str, Any]], Awaitable[Any]],
        callback_query: CallbackQuery,  # type: ignore[override]
        data: dict[str, Any],
    ) -> Any:
        assert isinstance(callback_query.message, Message)

        callback_data = data.get("callback_data")
        assert isinstance(callback_data, CallbackData)

        if not bot_state.active and "client" in callback_data.__prefix__:
            await SendMessage(
                chat_id=callback_query.message.chat.id,
                text="Бот не активен.",
            )
            await callback_query.answer()
            return

        return await handler(callback_query, data)


def SetBotMiddleware(dp: Dispatcher) -> None:
    dp.message.middleware(LoggingMessageMiddleware())
    dp.message.middleware(ClientMessageMiddleware())

    dp.callback_query.middleware(LoggingCallbackMiddleware())
    dp.callback_query.middleware(ClientCallbackMiddleware())
