from pathlib import Path

from aiogram import F, Router, types
from aiogram.filters.command import Command
from aiogram.filters.state import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import KeyboardButton, ReplyKeyboardMarkup, ReplyKeyboardRemove

from grader.bot.lib.message.io import ContextIO, SendMessage
from grader.bot.lib.message.filter import HasReferenceFilter, VerifiedFilter
from grader.db.models.user import User
from grader.bot.lifecycle.creator import bot
from grader.core.configs.paths import DIR_NOTEBOOKS
from grader.services.user import UserService

router = Router()


class StartStates(StatesGroup):
    GetPhoneNumber = State()
    Terms = State()
    GetReferenceNotebook = State()
    GetStudentNotebook = State()


ipynb_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text="📥 Эталон"),
            KeyboardButton(text="🔍 Студент"),
        ]
    ],
    resize_keyboard=True,
)


@router.message(StateFilter(None), Command("start"), VerifiedFilter())
async def CommandStartNew(message: types.Message) -> None:
    await SendMessage(
        chat_id=message.chat.id,
        text="Выберете, чье решение в формате .ipynb вы бы хотели загрузить - эталонное или решение студента",
        reply_markup=ipynb_keyboard,
    )


@router.message(StateFilter(None), Command("start"))
async def CommandStart(message: types.Message, state: FSMContext) -> None:
    button = KeyboardButton(text="📱 Поделиться контактом", request_contact=True)
    keyboard = ReplyKeyboardMarkup(keyboard=[[button]], resize_keyboard=True)

    await SendMessage(
        chat_id=message.chat.id,
        text="Пожалуйста, поделитесь с нами своим контактом\n\nЕсли меню с кнопками скрыто, нажмите на значок 🎛 в правом нижнем углу",
        reply_markup=keyboard,
    )

    await state.set_state(StartStates.GetPhoneNumber)


@router.message(StateFilter(StartStates.GetPhoneNumber))
async def CommandStartGetPhoneNumber(message: types.Message, state: FSMContext) -> None:
    if message.contact is None:
        await SendMessage(
            chat_id=message.chat.id,
            text="❌ Пожалуйста, отправьте свой номер телефона, используя кнопку ниже.\n\nЕсли меню с кнопками скрыто, нажмите на значок 🎛 в правом нижнем углу",
            context=ContextIO.UserFailed,
        )
        return

    if message.contact.user_id is None:
        await SendMessage(
            chat_id=message.chat.id,
            text="❌ Не удалось получить ваш номер телефона, так как вы не являетесь пользователем Telegram.\nПожалуйста, попробуйте снова из своего пользовательского профиля",
            context=ContextIO.UserFailed,
        )
        return

    if message.contact.user_id != message.chat.id:
        await SendMessage(
            chat_id=message.chat.id,
            text="❌ Вы отправили чужой номер телефона.\nПожалуйста, отправьте свой собственный номер.\n\nЕсли меню с кнопками скрыто, нажмите на значок 🎛 в правом нижнем углу",
            context=ContextIO.UserFailed,
        )
        return

    srv = UserService.Create()
    await srv.UpdateUser(
        chat_id=message.chat.id,
        column=User.phone_number,
        value=message.contact.phone_number,
    )
    await srv.UpdateUser(
        chat_id=message.chat.id,
        column=User.verified,
        value=True,
    )

    _EnsureNotebookDirectories(message.chat.id)

    await SendMessage(
        chat_id=message.chat.id,
        text="✅ Спасибо!",
        reply_markup=ReplyKeyboardRemove(),
    )

    await SendMessage(
        chat_id=message.chat.id,
        text="Выберете, чье решение в формате .ipynb вы бы хотели загрузить - эталонное решение для контекста или решение студента для проверки.",
        reply_markup=ipynb_keyboard,
    )


def _EnsureNotebookDirectories(chat_id: int) -> None:
    base_dir = DIR_NOTEBOOKS / f"notebook_{chat_id}"
    (base_dir / "reference").mkdir(parents=True, exist_ok=True)
    (base_dir / "student").mkdir(parents=True, exist_ok=True)


def _GetNotebookPath(chat_id: int, folder: str) -> Path:
    return DIR_NOTEBOOKS / f"notebook_{chat_id}" / folder / "hw.ipynb"


async def _SaveNotebook(
    document: types.Document,
    destination: Path,
) -> None:
    file = await bot.get_file(document.file_id)
    await bot.download_file(file.file_path, destination=destination)


def _IsNotebook(document: types.Document | None) -> bool:
    if document is None or document.file_name is None:
        return False
    return document.file_name.lower().endswith(".ipynb")


@router.message(StateFilter(None), F.text == "📥 Эталон", VerifiedFilter())
async def CommandReferenceNotebook(message: types.Message, state: FSMContext) -> None:
    await SendMessage(
        chat_id=message.chat.id,
        text="Пожалуйста, отправьте эталонное решение в формате .ipynb.",
    )
    await state.set_state(StartStates.GetReferenceNotebook)


@router.message(StateFilter(None), F.text == "🔍 Студент", VerifiedFilter())
async def CommandStudentNotebook(message: types.Message, state: FSMContext) -> None:
    await SendMessage(
        chat_id=message.chat.id,
        text="Пожалуйста, отправьте решение студента в формате .ipynb.",
    )
    await state.set_state(StartStates.GetStudentNotebook)


@router.message(StateFilter(StartStates.GetReferenceNotebook))
async def CommandUploadReferenceNotebook(
    message: types.Message,
    state: FSMContext,
) -> None:
    if not _IsNotebook(message.document):
        await SendMessage(
            chat_id=message.chat.id,
            text="❌ Нужен файл в формате .ipynb. Пожалуйста, попробуйте еще раз.",
            context=ContextIO.UserFailed,
        )
        return

    _EnsureNotebookDirectories(message.chat.id)
    await _SaveNotebook(
        document=message.document,
        destination=_GetNotebookPath(message.chat.id, "reference"),
    )

    await SendMessage(
        chat_id=message.chat.id,
        text="✅ Эталонное решение загружено.",
        reply_markup=ipynb_keyboard,
    )
    await state.clear()


@router.message(StateFilter(StartStates.GetStudentNotebook))
async def CommandUploadStudentNotebook(
    message: types.Message,
    state: FSMContext,
) -> None:
    if not _IsNotebook(message.document):
        await SendMessage(
            chat_id=message.chat.id,
            text="❌ Нужен файл в формате .ipynb. Пожалуйста, попробуйте еще раз.",
            context=ContextIO.UserFailed,
        )
        return

    _EnsureNotebookDirectories(message.chat.id)
    await _SaveNotebook(
        document=message.document,
        destination=_GetNotebookPath(message.chat.id, "student"),
    )

    await SendMessage(
        chat_id=message.chat.id,
        text="✅ Решение студента загружено.",
        reply_markup=ipynb_keyboard,
    )
    await state.clear()
