from aiogram import Router, types
from aiogram.filters.command import Command
from aiogram.fsm.context import FSMContext

from grader.bot.lib.message.io import SendMessage

router = Router()


@router.message(Command("cancel"))
async def CommandCancel(message: types.Message, state: FSMContext) -> None:
    await SendMessage(
        chat_id=message.chat.id,
        text="Отменено",
        reply_markup=types.ReplyKeyboardRemove(),
    )

    await state.clear()
