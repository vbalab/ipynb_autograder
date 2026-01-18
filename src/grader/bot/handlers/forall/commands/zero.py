from aiogram import Router, types

from grader.bot.lib.message.io import ContextIO, SendMessage

router = Router()


@router.message()
async def ZeroMessageText(message: types.Message) -> None:
    await SendMessage(
        chat_id=message.chat.id,
        text="Вы не находитесь в команде.\nВыберите из меню",
        context=ContextIO.ZeroMessage,
    )
