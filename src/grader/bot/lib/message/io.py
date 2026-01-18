import asyncio
import logging
from dataclasses import dataclass
from enum import Enum

from aiogram import types
from aiogram.exceptions import (
    TelegramBadRequest,
    TelegramForbiddenError,
    TelegramNetworkError,
)
from aiogram.filters.callback_data import CallbackData
from aiolimiter import AsyncLimiter

from grader.bot.lib.chat.block import UserBlockedBot
from grader.bot.lib.chat.username import GetChatUserLoggingPart
from grader.bot.lifecycle.creator import bot
from grader.services.user import UserService


class ContextIO(str, Enum):
    No = ""

    Error = " \033[91m[Error]\033[0m"
    ForbiddenError = " \033[91m[ForbiddenError]\033[0m"
    BadRequest = " \033[91m[BadRequest]\033[0m"
    NetworkError = " \033[91m[NetworkError]\033[0m"

    UserFailed = " \033[91m[UserFailed]\033[0m"

    Callback = " \033[92m[Callback]\033[0m"
    Doc = " \033[92m[Document]\033[0m"

    Pending = " \033[96m[Pending]\033[0m"
    ZeroMessage = " \033[96m[ZeroMessage]\033[0m"
    NoText = " \033[96m[NoText]\033[0m"


class SignIO(str, Enum):
    In = "\033[35m>>\033[0m"
    Out = "\033[36m<<\033[0m"
    On = "\033[37m<>\033[0m"


async def SendDocument(
    chat_id: int,
    document: types.FSInputFile,
    caption: str | None = None,
    reply_markup: (
        types.ReplyKeyboardMarkup
        | types.ReplyKeyboardRemove
        | types.InlineKeyboardMarkup
        | None
    ) = None,
) -> types.Message | None:
    add = ContextIO.No

    message: types.Message | None = None
    try:
        message = await bot.send_document(
            chat_id=chat_id,
            document=document,
            caption=caption,
            reply_markup=reply_markup,
        )

    except TelegramForbiddenError:
        add = ContextIO.ForbiddenError
        await UserBlockedBot(chat_id)

    except TelegramBadRequest as e:
        logging.error(e)
        add = ContextIO.BadRequest

    part = await GetChatUserLoggingPart(chat_id)
    logging.info(f"{part} {SignIO.Out.value}{add.value}{ContextIO.Doc.value} {caption}")

    return message


async def _SendMedia(
    chat_id: int,
    media: types.InputMediaPhoto,
    reply_markup: (
        types.ReplyKeyboardMarkup
        | types.ReplyKeyboardRemove
        | types.InlineKeyboardMarkup
        | None
    ) = None,
    context: ContextIO = ContextIO.No,
) -> types.Message | None:
    add = ContextIO.No

    message: types.Message | None = None
    try:
        message = await bot.send_photo(
            chat_id=chat_id,
            photo=media.media,
            caption=media.caption,
            reply_markup=reply_markup,
        )

    except TelegramForbiddenError:
        add = ContextIO.ForbiddenError
        await UserBlockedBot(chat_id)
    except TelegramBadRequest as e:
        logging.error(e)
        add = ContextIO.BadRequest
    except TelegramNetworkError as e:
        logging.error(e)
        add = ContextIO.NetworkError

    part = await GetChatUserLoggingPart(chat_id)
    logging.info(
        f"{part} {SignIO.Out.value}{add.value}{context.value} {repr(media.caption)}"
    )

    return message


async def SendMessage(
    chat_id: int,
    text: str,
    reply_markup: (
        types.ReplyKeyboardMarkup
        | types.ReplyKeyboardRemove
        | types.InlineKeyboardMarkup
        | None
    ) = None,
    context: ContextIO = ContextIO.No,
) -> types.Message | None:
    add = ContextIO.No

    message: types.Message | None = None
    try:
        message = await bot.send_message(
            chat_id=chat_id,
            text=text,
            reply_markup=reply_markup,
        )

    except TelegramForbiddenError:
        add = ContextIO.ForbiddenError
        await UserBlockedBot(chat_id)

    except TelegramBadRequest as e:
        logging.error(e)
        add = ContextIO.BadRequest

    part = await GetChatUserLoggingPart(chat_id)
    logging.info(f"{part} {SignIO.Out.value}{add.value}{context.value} {repr(text)}")

    return message


@dataclass
class PersonalMsg:
    chat_id: int
    text: str


async def SendMessagesToGroup(messages: list[PersonalMsg]) -> None:
    limiter = AsyncLimiter(max_rate=30, time_period=1)

    async def SendMessageLimited(message: PersonalMsg) -> None:
        nonlocal limiter

        async with limiter:
            await SendMessage(
                chat_id=message.chat_id,
                text=message.text,
            )

    tasks = []
    for message in messages:
        tasks.append(SendMessageLimited(message))

    await asyncio.gather(*tasks)


async def _CheckNewUser(chat_id: int) -> None:
    ctx = UserService.Create()
    exists = await ctx.CheckUserExists(chat_id)

    if not exists:
        await ctx.CreateUser(chat_id=chat_id)


async def ReceiveMessage(
    message: types.Message,
    context: ContextIO = ContextIO.No,
) -> None:
    chat_id = message.chat.id
    await _CheckNewUser(chat_id)

    part = await GetChatUserLoggingPart(chat_id)
    logging.info(f"{part} {SignIO.In.value}{context.value} {repr(message.text)}")


async def ReceiveCallback(query: types.CallbackQuery, data: CallbackData) -> None:
    chat_id = query.from_user.id
    await _CheckNewUser(chat_id)

    part = await GetChatUserLoggingPart(chat_id)
    logging.info(
        f"{part} {SignIO.In.value} {ContextIO.Callback.value} {data.__prefix__}, model_dump={data.model_dump()}"
    )


async def DeleteMessage(chat_id: int, message_id: int) -> None:
    add = ContextIO.No

    try:
        await bot.delete_message(chat_id=chat_id, message_id=message_id)
    except TelegramForbiddenError:
        add = ContextIO.ForbiddenError
        await UserBlockedBot(chat_id)

    except TelegramBadRequest:
        add = ContextIO.BadRequest

    part = await GetChatUserLoggingPart(chat_id)
    logging.info(f"{part}{add.value} Message(message_id={message_id}) deleted.")
