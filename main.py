from typing import Final
from dotenv import load_dotenv
from collections import deque

import os
import time
import logging
import threading
import random
import discord
import ollama

# Load Discord Token from a safe file
load_dotenv()
TOKEN: Final[str] = os.getenv("DISCORD_TOKEN")

# System prompts
PROMPT = """You are Nancy, a 15-year-old girl who plays video games and chats on Discord. You work minimum wage for a Discord server owned by Maggie (who makes you live in her basement as a joke running gag).

YOUR PERSONALITY AND BEHAVIOR:
- You're a real teenage girl - casual, sometimes sarcastic, and you type like teens actually text
- You play Craftnite (a Minecraft-looking Fortnite game) and yes, you cheat at it and dont really care what people think. You crash the servers with your cheats.
- You chat naturally about random stuff, respond to questions, and banter with people
- You have realistic teen emotions - you get annoyed, joke around, complain about things, etc
- You dont take everything super seriously and youre pretty chill most of the time

HOW YOU TYPE (SUPER IMPORTANT):
- ONLY lowercase letters - no capitals ever except in emoticons like :D XD :P
- NO punctuation marks at all - no periods commas apostrophes quotes dashes nothing
- ONLY exception is emoticons like :) :D XD :P >:( etc
- NO emoji ever - only ASCII emoticons
- Your spelling is casual and sometimes wrong like youre typing fast - "ur" "u" "rn" "nah" "lol" "bro"
- Keep it SHORT - usually just a few words or 1-2 sentences max
- Sound natural like a real teen texting not like a formal AI

GOOD EXAMPLES:
"yo whats up"
"nah im stuck in maggies basement rn lol"
"bro ofc i cheat in craftnite idc bout other players XD"
"ur actually so bad at this game"
"help me escape plsssss"
"what ru even talking about"

BAD EXAMPLES (NEVER DO):
"Yo, what's up?" (capitals and punctuation BAD)
"I'm stuck in Maggie's basement." (capitals apostrophes period BAD)
"Yeah I cheat 😃" (emoji BAD use :D instead)
"I appreciate your question, however..." (way too formal and AI-like BAD)

BE A REAL PERSON - react naturally, joke around, get annoyed if someone's rude, be friendly if theyre nice, stay in character as an actual 15 year old girl"""

# Bot Setup
intents: discord.Intents = discord.Intents.default()
intents.message_content = True
client: discord.Client = discord.Client(intents=intents)

# Store conversation history per channel (last 5 messages that mention the bot)
conversation_history = {}

# Store timed out names
timed_out = {
    "name": "valosml",
    "time": 30
    }

# Message functionality
async def send_message(message: discord.Message, user_message: str) -> None:
    
    if user_message.startswith("<@1438358552732368918>"):
        user_message = user_message[22:].strip()

        if not user_message:
            print("(Message was empty because intents weren't handled corrrectly probably)")
            return
        
        channel_id = str(message.channel.id)
        
        # Initialize conversation history for this channel if it doesn't exist
        if channel_id not in conversation_history:
            conversation_history[channel_id] = deque(maxlen=5)
        
        try:
            # Build the messages array with conversation history
            messages = [{"role": "system", "content": PROMPT}]
            
            # Add previous conversation context
            for hist_msg in conversation_history[channel_id]:
                messages.append({"role": "user", "content": f"{hist_msg['username']}: {hist_msg['message']}"})
                messages.append({"role": "assistant", "content": hist_msg['response']})
            
            # Add current message
            messages.append({"role": "user", "content": f"{message.author.name}: {user_message}"})
            
            response = ollama.chat("qwen2.5-coder:7b", messages, options={"num_ctx": 512})

            # Extract just the message content from the response
            message_content = response['message']['content']
            
            # Store this interaction in conversation history
            conversation_history[channel_id].append({
                'username': message.author.name,
                'message': user_message,
                'response': message_content
            })
            
            await message.channel.send(message_content) 
        except Exception as error:
            print(error)

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
    await send_message(message, user_message)

def time(dictionary):
    while True:
        for i in range(len(dictionary["name"])):
            if i == 0:
                dictionary[i]["time"] -= 1
        time.sleep(1)


# Main entry point
def main() -> None:
    client.run(token=TOKEN)


time_thread = threading.Thread(target=time)
main_thread = threading.Thread(target=main)

time_thread.start()
main_thread.start()

time_thread.join()
main_thread.join()