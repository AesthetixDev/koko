# Koko

A modular Discord bot built with PyCord.

All interactions use slash commands, e.g. `/ping`.
Use `/help` to see a list of commands available to you.
Administrators can enable or disable features using `/settings`.

## Setup

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
2. Set the `DISCORD_TOKEN` environment variable with your bot token.
3. Optionally configure `logs_channel_id` in `config.json` to enable action logging.
4. Optionally adjust `settings_path` to control where feature toggles are stored.
5. Run the bot:
   ```bash
   python -m koko.bot
   ```
