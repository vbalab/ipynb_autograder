from pathlib import Path

_DIR_ROOT = Path(__file__).resolve().parent.parent.parent.parent.parent
_DIR_DATA = _DIR_ROOT / "data"
_DIR_LOGS = _DIR_DATA / "logs"
_DIR_PROMPTS = _DIR_ROOT / "prompts"

DIR_TEMP = _DIR_DATA / "temp"
DIR_NOTEBOOKS = _DIR_DATA / "notebooks"

_dirs = [
    _DIR_DATA,
    _DIR_LOGS,
    DIR_TEMP,
    DIR_NOTEBOOKS,
]

PATH_ENV = _DIR_ROOT / ".env"
PATH_BOT_LOGS = _DIR_LOGS / "bot" / "bot.log"
PATH_STRUCTURE_PROMPT = _DIR_PROMPTS / "structure.md"


def EnsurePaths() -> None:
    for directory in _dirs:
        directory.mkdir(parents=True, exist_ok=True)

    if not PATH_ENV.exists():
        raise FileNotFoundError("`.env` file not found")
