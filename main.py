from typing import Final
from dotenv import load_dotenv
from discord.ext import commands

import functions as function
import process

import os
import re
import json
import time
import random
import discord
import ollama
import requests

# Load Discord Token from a safe file
load_dotenv()
TOKEN: Final[str] = os.getenv("DISCORD_TOKEN") or ""

config_path = 'config.json'
config = function.load_config(config_path)

# Bot Setup
intents: discord.Intents = discord.Intents.default()
intents.message_content = True
client: discord.Client = discord.Client(intents=intents)

# Handle startup
@client.event
async def on_ready() -> None:
    print(random.choice([
        f"Logged in as {client.user}"]))

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
    client.run(token=TOKEN)

if __name__ == "__main__":
    main()