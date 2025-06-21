# Koko

A modular Discord bot built with PyCord.

All interactions use slash commands, e.g. `/ping`.

## Setup

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
2. Set the `DISCORD_TOKEN` environment variable with your bot token.
3. Optionally configure `logs_channel_id` in `config.json` to enable action logging.
4. Run the bot:
   ```bash
   python -m koko.bot
   ```
