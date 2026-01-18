from enum import Enum

from aiogram import F, Router, types
from aiogram.filters.callback_data import CallbackData
from aiogram.filters.command import Command, CommandObject
from aiogram.filters.state import StateFilter
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from grader.bot.lib.chat.block import BlockUser, CheckIfBlocked, UnblockUser
from grader.bot.lib.message.filter import AdminFilter
from grader.bot.lib.message.io import ContextIO, SendMessage
from grader.services.user import UserService

router = Router()


class BlockingAction(str, Enum):
    Block = "Заблокировать"
    Unblock = "Разблокировать"
    Leave = "Оставить как есть"


class BlockingCallbackData(CallbackData, prefix="blocking"):
    action: BlockingAction
    chat_id: int


def BlockingKeyboard(
    actions: list[BlockingAction], chat_id: int
) -> InlineKeyboardMarkup:
    def Button(action: BlockingAction) -> InlineKeyboardButton:
        nonlocal chat_id

        return InlineKeyboardButton(
            text=action.value,
            callback_data=BlockingCallbackData(action=action, chat_id=chat_id).pack(),
        )

    buttons: list[InlineKeyboardButton] = [Button(a) for a in actions]

    return InlineKeyboardMarkup(inline_keyboard=[buttons])


@router.message(Command("blocking"), StateFilter(None), AdminFilter())
async def CommandBlocking(
    message: types.Message,
    command: CommandObject,
) -> None:
    if not command.args or len(command.args.split()) != 1:
        await SendMessage(
            chat_id=message.chat.id,
            text="Укажите username в Telegram:\n/blocking @vbalab",
            context=ContextIO.UserFailed,
        )
        return

    ctx = UserService.Create()
    chat_id = await ctx.GetChatIdByUsername(command.args.replace("@", "").strip())

    if chat_id is None:
        await SendMessage(
            chat_id=message.chat.id,
            text="Пользователь не найден.",
        )
        return

    blocked = await CheckIfBlocked(chat_id)

    if blocked:
        await SendMessage(
            chat_id=message.chat.id,
            text="🔴 Пользователь заблокирован.\n\nРазблокировать?",
            reply_markup=BlockingKeyboard(
                actions=[BlockingAction.Unblock, BlockingAction.Leave],
                chat_id=chat_id,
            ),
        )
        return

    await SendMessage(
        chat_id=message.chat.id,
        text="🟢 Пользователь не заблокирован.\n\nЗаблокировать?",
        reply_markup=BlockingKeyboard(
            actions=[BlockingAction.Block, BlockingAction.Leave],
            chat_id=chat_id,
        ),
    )


@router.callback_query(BlockingCallbackData.filter(F.action == BlockingAction.Unblock))
async def CommandBlockingUnblock(
    callback_query: types.CallbackQuery,
    callback_data: BlockingCallbackData,
) -> None:
    assert isinstance(callback_query.message, types.Message)

    await UnblockUser(callback_data.chat_id)

    await callback_query.message.edit_text(
        text="🟢 Пользователь теперь не заблокирован.",
        reply_markup=None,
    )
    await callback_query.answer()


@router.callback_query(BlockingCallbackData.filter(F.action == BlockingAction.Block))
async def CommandBlockingBlock(
    callback_query: types.CallbackQuery, callback_data: BlockingCallbackData
) -> None:
    assert isinstance(callback_query.message, types.Message)

    await BlockUser(callback_data.chat_id)

    await callback_query.message.edit_text(
        text="🔴 Пользователь теперь заблокирован.",
        reply_markup=None,
    )
    await callback_query.answer()


@router.callback_query(BlockingCallbackData.filter(F.action == BlockingAction.Leave))
async def CommandBlockingCancel(callback_query: types.CallbackQuery) -> None:
    assert isinstance(callback_query.message, types.Message)

    await callback_query.message.edit_reply_markup(reply_markup=None)
    await callback_query.answer("Отменено")
