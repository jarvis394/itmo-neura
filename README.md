<p align="left"><img  src="./.github/images/text_logo_neura.png" alt="neura logo" /></p>

## About

**neura** is a fun Telegram bot that generates messages based on the message history

Invite: [t.me/itmo_neura_bot](https://t.me/itmo_neura_bot)

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
PORT=4000
HOST=0.0.0.0
WEBHOOK_HOST=********.ngrok.io
```

Then, run

```bash
poetry run python3 main.py
```

to start the bot in its virtual environment.
