# neura

## Getting started

Install [poetry](https://python-poetry.org/) and run:

```bash
poetry install
# ... packages are being installed

poetry shell
```

Fill `.env` file with environment values:

```bash
# paste actual token here
TELEGRAM_BOT_API_TOKEN=
PORT=3000
HOST=localhost
```

Then, run

```bash
poetry run python3 main.py
```

to start the bot in its virtual environment.
