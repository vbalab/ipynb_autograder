from pathlib import Path

_DIR_ROOT = Path(__file__).resolve().parent.parent.parent.parent

_DIR_DATA = _DIR_ROOT / "data"
_DIR_NOTEBOOK = _DIR_DATA / "notebook"
DIR_NOTEBOOK_IPYNB = _DIR_NOTEBOOK / "ipynb"
DIR_NOTEBOOK_PROCESSED = _DIR_NOTEBOOK / "processed"

_dirs = [
    _DIR_DATA,
    _DIR_NOTEBOOK,
    DIR_NOTEBOOK_IPYNB,
    DIR_NOTEBOOK_PROCESSED,
]

PATH_ENV = _DIR_ROOT / ".env"

def EnsurePaths() -> None:
    for directory in _dirs:
        directory.mkdir(parents=True, exist_ok=True)

    if not PATH_ENV.exists():
        raise FileNotFoundError("`.env` file not found")

if __name__ == "__main__":
    EnsurePaths()

    print(_DIR_ROOT)
