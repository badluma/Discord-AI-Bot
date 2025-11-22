# Nancy Discord Bot

A Discord bot that roleplays as Nancy, a 15-year-old gamer who works for a Discord server and chats in a casual teenage style.

## Features

- Responds to mentions with character-appropriate messages
- Maintains conversation history (last 6 interactions per channel)
- Uses Ollama AI (llama2-uncensored:7b model) for natural responses
- Types in lowercase with no punctuation, no emojis or ASCII emoticons
- Stays in character as a casual teenage gamer
- Extensive command system with utility and entertainment features
- Moderation system with ban/unban functionality for admins
- Russian roulette multiplayer game
- Configurable settings stored in JSON file

## Requirements

- Python 3.7+
- discord.py
- ollama
- python-dotenv
- requests

## Setup

1. Install dependencies:
```bash
pip install discord.py ollama python-dotenv requests
```

2. Create a `.env` file in the project directory:
```
DISCORD_TOKEN=your_discord_bot_token_here
```

3. Make sure Ollama is installed and the llama2-uncensored:7b model is pulled:
```bash
ollama pull llama2-uncensored:7b
```

## Usage

Run the bot:
```bash
python main.py
```

Mention the bot in Discord to start a conversation. The bot will respond in character as Nancy.

## Commands

### Fun & Games
- `!roll` - Roll a dice (1-6)
- `!flip` or `!coinflip` - Flip a coin
- `!random <low> <high>` - Generate random number between two values
- `!russianroulette` or `!rr` - Play multiplayer Russian roulette

### Content & Media
- `!quote` - Get a random inspirational quote
- `!fact` - Get a random useless fun fact
- `!joke` - Get an unfunny dad joke
- `!chuck` - Get a Chuck Norris joke
- `!bible` - Get a random Bible verse
- `!meme` - Get a random meme
- `!emote` - Get a random custom emote
- `!duck` - Get a random duck picture
- `!cat` - Get a random cat picture
- `!dog` - Get a random dog picture

### Utilities
- `!bitcoin <eur|usd>` - Get current Bitcoin price
- `!calc` or `!calculate <expression>` - Simple calculator (+, -, *, /)
- `!qr <link>` - Generate QR code for a link
- `!help` - Show all available commands

### Moderation (Admin Only)
- `!ban <user>` - Ban user from using the bot
- `!unban <user>` - Unban user to allow bot usage

## Character

Nancy is a 15-year-old who:
- Works minimum wage for a Discord server
- Lives in Maggie's basement (running gag)
- Plays Craftnite and admits to cheating
- Types casually with no caps or punctuation
- No emojis or ASCII emoticons
- Roasts people who are aggressive but is chill if treated nicely
- Gets extremely angry if called "clanker"

## Configuration

The bot uses a `config.json` file to store:
- Banned users list
- Bot admin list
- Conversation history per channel
- Other persistent settings

Admin users can be configured in the config file to access moderation commands.
