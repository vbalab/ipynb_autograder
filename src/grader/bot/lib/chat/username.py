import logging

from grader.bot.lifecycle.creator import bot
from grader.db.models.user import User
from grader.services.user import UserService


async def GetTgUsername(chat_id: int) -> str | None:
    try:
        chat = await bot.get_chat(chat_id)
        username = chat.username

        ctx = UserService.Create()
        db_username = await ctx.GetUser(
            chat_id=chat_id,
            column=User.username,
        )

        if username != db_username:
            await ctx.UpdateUser(
                chat_id=chat_id,
                column=User.username,
                value=username,
            )

        return username

    except Exception as e:
        logging.warning(f"Failed to get chat info for chat_id={chat_id}: {e}")
        return None


async def GetChatUserLoggingPart(chat_id: int) -> str:
    username = await GetTgUsername(chat_id) or "-/-"
    username = "(" + username + ")"

    return f"chat_id={chat_id:<10} {username:<25}"
