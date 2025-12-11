print("Importing packages: ", end="")
print("typing, ", end="")
from typing import Final
print("dotenv, ", end="")
from dotenv import load_dotenv
print("discord.ext, ", end="")
from discord.ext import commands
print("functions, ", end="")
import functions as function
print("process, ", end="")
import process
print("os, ", end="")
import os
print("re, ", end="")
import re
print("json, ", end="")
import json
print("time, ", end="")
import time
print("random, ", end="")
import random
print("discord, ", end="")
import discord
print("ollama, ", end="")
import ollama
print("requests, ", end="")
import requests
print("music, ", end="")
import music


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