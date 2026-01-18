from aiogram import F, Router, types
from aiogram.filters.command import Command
from aiogram.filters.state import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from grader.bot.lib.message.filter import AdminFilter
from grader.bot.lib.message.io import PersonalMsg, SendMessage, SendMessagesToGroup
from grader.services.user import UserService

router = Router()


class SendaStates(StatesGroup):
    Message = State()


@router.message(Command("senda"), StateFilter(None), AdminFilter())
async def CommandSenda(message: types.Message, state: FSMContext) -> None:
    await SendMessage(chat_id=message.chat.id, text="Введите текст сообщения")
    await state.set_state(SendaStates.Message)


@router.message(StateFilter(SendaStates.Message), F.content_type == "text")
async def CommandSendaMessage(message: types.Message, state: FSMContext) -> None:
    assert message.text is not None

    ctx = UserService.Create()
    chat_ids = await ctx.GetVerifiedUsersChatId()

    messages = [PersonalMsg(chat_id=chat_id, text=message.text) for chat_id in chat_ids]
    await SendMessagesToGroup(messages)

    await SendMessage(chat_id=message.chat.id, text="Готово")
    await state.clear()
