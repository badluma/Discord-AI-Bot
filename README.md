# Discord AI Bot

A customizable Discord bot powered by Ollama that can roleplay as any character or personality you define. Configure the bot's personality, behavior, and conversation style through a simple JSON configuration file.

---

## Features

- **Fully Customizable AI Personality** - Define any character, tone, or behavior through the config file
- **Conversation Memory** - Maintains conversation history (last 6 interactions per channel)
- **Ollama Integration** - Uses local AI models (llama2-uncensored:7b by default) for natural responses
- **Extensive Command System** - 40+ utility and entertainment commands
- **Translation Support** - Translate text between 30+ languages
- **Moderation Tools** - Ban/unban functionality for admins
- **Multi-Channel Support** - Works in both DMs and server channels (when mentioned)
- **Easy Configuration** - All settings stored in a single JSON file

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

3. Make sure Ollama is installed and a model of your choice is pulled:
```bash
ollama pull dolphin3
```

4. Configure your bot's personality in `config.json` (see Configuration section below)

## Usage

Run the bot:
```bash
python main.py
```

**How to interact:**
- **Direct Chat**: Mention the bot (@Nancy) in any channel to start a conversation
- **DM**: Send direct messages to the bot for private conversations
- **Commands**: Use `!command` format for utility functions and entertainment
- **Help**: Use `!help`, `!h`, or `?` to see all available commands

The bot will respond according to your configured personality while maintaining conversation context.

## Commands

[![Discord AI Bot | Commands Showcase](https://img.youtube.com/vi/jWvS045lb6I/maxresdefault.jpg)](https://www.youtube.com/watch?v=jWvS045lb6I&t=22s)

#### Fun & Games
- `!roll` - Roll a dice (1-6)
- `!flip` or `!coinflip` - Flip a coin (heads/tails)
- `!random <low> <high>` - Generate random number between two values
- `!randomnumber` or `!randint <low> <high>` - Generate random number (alias)

- `!truth` - Get a truth question
- `!dare` - Get a dare
- `!wyr` - Get a "Would You Rather" question
- `!rizz [target]` - Get a pickup line (optionally mention someone)
- `!roast [target]` - Get a random insult (optionally mention someone)
- `!compliment [target]` - Get a random compliment (optionally mention someone)
- `!activity` - Get a random activity suggestion
- `!draw <participants...>` - Randomly choose from participants

#### Content & Media
- `!quote` - Get a random inspirational quote
- `!fact` or `!funfact` - Get a random useless fun fact
- `!joke` or `!dadjoke` - Get an unfunny dad joke
- `!chuck` or `!chucknorris` - Get a Chuck Norris joke
- `!bible` or `!verse` - Get a random Bible verse
- `!meme` - Get a random meme
- `!emote` or `!emoji` - Get a random custom emote
- `!duck` - Get a random duck picture
- `!cat` - Get a random cat picture
- `!dog` - Get a random dog picture

#### Utilities
- `!bitcoin` or `!btc <eur|usd>` - Get current Bitcoin price
- `!calc` or `!calculate <expression>` - Simple calculator (+, -, *, /)
- `!qr <link>` - Generate QR code for a link
- `!translate <source> <target> <text>` - Translate text between languages (just `!translate` to show available languages)
- `!help` - Show all available commands

#### Moderation (Admin Only)
- `!ban <user>` - Ban user from using the bot
- `!unban <user>` - Unban user to allow bot usage

## Configuration

The bot uses a `config.json` file to store all settings:

#### config.json Structure

```json
{
    "banned": [],
    "muted": [],
    "admin": ["Your discord username"],

    "youtube_playlist_url": "Your desired youtube playlist",
    "music_channel_id": "Name of the voice channel where the playlist should play",

    "ai_trigger": "<@1438358552732368918>",
    "model": "dolphin3",
    "prompt": "You are a helpful assistant.",
    "is_casual": true,
    "history": {}
}
```

#### Customizing Your Bot's Personality

Edit the `prompt` field in `config.json` to define your bot's character. You can configure:

- **Background and lore** - Who is the bot? What's their story?
- **Personality traits** - How do they behave? What's their vibe?
- **Communication style** - How do they type? What rules should they follow?
- **Reactions** - How do they respond to different situations?
- **Specific triggers** - Special responses to certain words or phrases

**Example personalities you could create:**
- A formal British butler
- A pirate captain
- A tech support expert
- A motivational coach
- A fantasy wizard
- A sarcastic AI from the future
- Or anything else you can imagine!

#### Admin Configuration

- `admin` - Users who can use moderation commands
- `admin` - Additional admin tier (currently same permissions as admin)
- `banned` - List of users banned from interacting with the bot

#### Conversation History

The bot automatically maintains conversation history per channel in the `history` object. This is limited to the last 6 interactions to maintain context while staying within model limits.

### Customization Tips

1. **Keep prompts clear and specific** - The more detailed your personality description, the better the bot will stay in character
2. **Define communication rules** - Specify capitalization, punctuation, emoji usage, response length, etc.
3. **Add examples** - Include examples of good and bad responses in your prompt
4. **Test and iterate** - Try different prompts and see what works best for your use case

### Model Configuration

The bot uses the `llama2-uncensored:7b` model by default with these settings:
- Context window: 4096 tokens
- Temperature: 0.7 (balance between creativity and consistency)
- Top-p: 0.85
- Repeat penalty: 1.1

These can be adjusted in `process.py` for different behavior.

## File Structure

- `main.py` - Bot initialization and event handlers
- `process.py` - Message processing and AI response generation
- `commands.py` - Command implementations
- `functions.py` - Utility functions for config management and API calls
- `games.py` - Game implementations (currently unused)
- `config.json` - Bot configuration and personality settings

## Contributing

Feel free to add new commands, improve the AI integration, or enhance the personality enforcement system!

## License

This project is open source and available for modification and use. (CC0 1.0 Universal)

---

**Sidenote about the use of AI**
I programmed most of the stuff myself and used [Opencode Zen](https://github.com/sst/opencode) for troubleshooting. The only thing made entirely by AI is the Music feature because I already moved on to a new project and didn't want to waste too much time on that. The README is also written mostly by Claude.

---
Made by badluma ✦