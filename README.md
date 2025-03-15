````markdown
# Translate Bot for Discord

This Discord bot automatically translates the names of text and voice channels, as well as roles, into a chosen language.

## Features

- Automatic translation of text and voice channels.
- Translation of role names on the server.
- Commands to manage the translation of channels and roles.
- Multi-language support using the Google Translate API.
- Commands:
  - `!translate_server <source_language> <destination_language>`: Translates all channels and roles in the server.
  - `!preview_translation <source_language> <destination_language>`: Previews the translation of channels and roles.
  - `!list_channels_and_roles`: Lists the current channels and roles in the server.

## Installation

1. Clone this repository:
   ```bash
   git clone https://github.com/your-username/translate-bot.git
   cd translate-bot
   ```
````

2. Create a virtual environment:

   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows, use 'venv\Scripts\activate'
   ```

3. Install the dependencies:

   ```bash
   pip install -r requirements.txt
   ```

4. Create a `.env` file in the root directory and add your `DISCORD_TOKEN`:

   ```env
   DISCORD_TOKEN=your_discord_bot_token_here
   ```

5. Run the bot:
   ```bash
   python bot.py
   ```

## Contributing

1. Fork this repository.
2. Create a branch for your feature (`git checkout -b feature/new-feature`).
3. Commit your changes (`git commit -m 'Add a new feature'`).
4. Push the branch (`git push origin feature/new-feature`).
5. Open a Pull Request to propose your changes.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
