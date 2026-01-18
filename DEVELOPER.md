# Notes for Developers

## Local Environment Setup

Being in repository directory:

```bash
python -m venv venv
vim venv/bin/activate
# Then add line at the end of file:
# export PYTHONPATH="$VIRTUAL_ENV/../src"

source venv/bin/activate

pip install --no-cache-dir -r requirements.txt -r requirements-dev.txt
```

## Pre-Commit Actions

```bash
black src/

ruff check src/ --fix

mypy src/
```

## Launch Bot

Be sure to have `.env` file similar to `.env.example`

Being in repository directory, give permissions:

Being in repository directory, launch:

```bash
sudo systemctl start docker

docker compose build #--no-cache
docker compose up --detach --remove-orphans

docker compose stop
docker compose down
```

Note that the bot started in docker _synchronizes_ Postgres DB & logs with local directory via channeling.

### View logs

You can view logs from docker via:

```bash
docker compose logs -f bot
docker compose logs -f <bot/db>
```

Or logs in files at `./data/logs` path locally.

### Enter container

```bash
docker compose run -it bot bash
docker compose run -it <bot/db> bash
```
