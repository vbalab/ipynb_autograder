# Notes for Developers

## Setup

### Via Local Environment

Being in repository directory:

```bash
python -m venv venv
vim venv/bin/activate
# Then add line at the end of file:
# export PYTHONPATH="$VIRTUAL_ENV/../src"

source venv/bin/activate

pip install --no-cache-dir -r requirements.txt -r requirements-dev.txt
```

### Via Docker

[TODO]

## Pre-Commit Actions

```bash
black src/

ruff check src/ --fix

mypy src/
```
