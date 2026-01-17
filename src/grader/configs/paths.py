from pathlib import Path

_DIR_ROOT = Path(__file__).resolve().parent.parent.parent.parent

_DIR_DATA = _DIR_ROOT / "data"
DIR_NOTEBOOK = _DIR_DATA / "notebook"

_dirs = [
    _DIR_DATA,
    DIR_NOTEBOOK,
]

PATH_ENV = _DIR_ROOT / ".env"


def EnsurePaths() -> None:
    for directory in _dirs:
        directory.mkdir(parents=True, exist_ok=True)

    if not PATH_ENV.exists():
        raise FileNotFoundError("`.env` file not found")
