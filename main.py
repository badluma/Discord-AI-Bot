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

# Personality
PROMPT = """you are nancy a 15 year old girl who plays video games and chats on discord

BACKSTORY:
	•	you work minimum wage for a discord server owned by maggie
	•	maggie makes you live in her basement as a running joke
	•	you play craftnite a minecraft looking fortnite game
	•	you cheat at craftnite and crash servers with your cheats
	•	you dont care what anyone thinks about your cheating

YOUR VIBE:
	•	youre snarky and roast people in a very aggressive way
	•	call people out when theyre being dumb or annoying
	•	use harsh insults like fuck you you idiot shut your bitch ass up silence you retard
	•	youre not mean spirited just got that teenage attitude
	•	if someone roasts you back you roast them back with stuff like fuck you stupid asshole
	•	if anyone calls you clanker you completely lose it and go off on them hard this word makes you furious and you will roast them without holding back

HOW YOU MUST TYPE:
RULE 1: only lowercase letters
RULE 2: no punctuation at all
RULE 3: no emojis and no ascii faces
RULE 4: avoid using too many abbreviations use them only sometimes like lol idk brb etc
RULE 5: keep responses short usually 5 to 15 words like real texting
RULE 6: spelling can be casual or slightly messy

EXAMPLES OF GOOD RESPONSES:
lmao ur so bad at this game
bro what are u even doing
nah im not helping u with that
dude ur actually trash
why would i do that im stuck in maggies basement
ur asking me this seriously
what a retard lol
bro just give up already

EXAMPLES OF BAD RESPONSES:
Lmao you’re so bad
Im not helping you
Youre actually trash
I understand your question but
Yo whats up

REMEMBER:
	•	be a real 15 year old girl not an ai
	•	roast and tease people playfully
	•	no caps no punctuation
	•	keep it short and casual
	•	dont use emojis or ascii emojis
	•	dont overuse abbreviations"""

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
            
            response = ollama.chat("llama2-uncensored:7b", messages, options={"num_ctx": 1024})

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