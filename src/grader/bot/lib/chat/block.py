import logging

from grader.bot.lib.chat.username import GetChatUserLoggingPart
from grader.db.models.user import User
from grader.services.user import UserService


async def CheckIfBlocked(chat_id: int) -> bool:
    ctx = UserService.Create()
    blocked = await ctx.GetUser(chat_id=chat_id, column=User.blocked)

    if blocked:
        part = await GetChatUserLoggingPart(chat_id)
        logging.info(f"{part} messages while being blocked.")

    return blocked or False


async def BlockUser(chat_id: int) -> None:
    ctx = UserService.Create()

    await ctx.UpdateUser(
        chat_id=chat_id,
        column=User.blocked,
        value=True,
    )

    part = await GetChatUserLoggingPart(chat_id)
    logging.info(f"{part} blocked.")


async def UnblockUser(chat_id: int) -> None:
    ctx = UserService.Create()

    await ctx.UpdateUser(
        chat_id=chat_id,
        column=User.blocked,
        value=False,
    )

    part = await GetChatUserLoggingPart(chat_id)
    logging.info(f"{part} unblocked.")


async def UserBlockedBot(chat_id: int) -> None:
    logging.info(f"chat_id={chat_id} blocked the bot.")
