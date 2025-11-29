print("Importing typing...")
from typing import Final
print("Typing imported.")

print("Importing dotenv...")
from dotenv import load_dotenv
print("dotenv imported.")

print("Importing discord.ext.commands...")
from discord.ext import commands
print("discord.ext.commands imported.")

print("Importing functions...")
import functions as function
print("functions imported.")

print("Importing process...")
import process
print("process imported.")

print("Importing os...")
import os
print("os imported.")

print("Importing re...")
import re
print("re imported.")

print("Importing json...")
import json
print("json imported.")

print("Importing time...")
import time
print("time imported.")

print("Importing random...")
import random
print("random imported.")

print("Importing discord...")
import discord
print("discord imported.")

print("Importing ollama...")
import ollama
print("ollama imported.")

print("Importing requests...")
import requests
print("requests imported.")

print("Importing music...")
import music
print("music imported.")


# Load Discord Token from a safe file
load_dotenv()
TOKEN: Final[str] = os.getenv("DISCORD_TOKEN") or ""

config_path = 'config.json'
config = function.load_config(config_path)

# Bot Setup
intents: discord.Intents = discord.Intents.default()
intents.message_content = True
intents.voice_states = True
client: discord.Client = discord.Client(intents=intents)

# Music setup
@client.event
async def on_ready() -> None:
    print(f"Logged in as {client.user}")
    # Initialize music player
    music.init_music_player(client)
    print("Music player initialized")
    print(random.choice([
        f"Bot is ready!"]))



# Handle incoming messages
@client.event
async def on_message(message: discord.Message) -> None:
    if message.author == client.user:
        return
    
    username: str = str(message.author)
    user_message: str = message.content
    channel: str = str(message.channel)

    print(f"[{channel}] {username}: {user_message}")
    await process.send_message(message, user_message)

# Main entry point
def main() -> None:
    if not TOKEN:
        print("No DISCORD_TOKEN found in environment. Did you create a .env file in this folder?")
        return

    print("Starting Discord client…")
    client.run(token=TOKEN)

if __name__ == "__main__":
    print("Starting main function...")
    main()