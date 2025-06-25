# Koko

A modular Discord bot built with PyCord.

All interactions use slash commands, e.g. `/ping`.
Use `/help` to see a list of commands available to you.
Administrators can enable or disable features using `/settings`.

Every message received by the bot is printed to the console in the format
`[#channel] (timestamp) username: message` to aid debugging.
Koko also prints a short note explaining how events can be registered each time
a message is received.

## Setup

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
2. Set the `DISCORD_TOKEN` environment variable with your bot token.
3. Optionally adjust `settings_path` to control where feature toggles are stored.
4. Run the bot:
   ```bash
   python -m koko.bot
   ```

When Koko joins a new server it will ask you to run `/setup` to configure a logs channel and other settings.
