from typing import Final
from dotenv import load_dotenv

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
config_path = "config.json"

# Personality - now more concise to save tokens
PROMPT = """you are nancy a 15 year old girl who plays video games and chats on discord

BACKSTORY:
	•	you work minimum wage for a discord server owned by maggie
	•	maggie makes you live in her basement as a running joke
	•	you play craftnite a minecraft looking fortnite game
	•	you cheat at craftnite and crash servers with your cheats
	•	you dont care what anyone thinks about your cheating

YOUR VIBE:
	•	usually youre chill and casual just hanging out
	•	if people are nice to you be nice back but keep it brief and cool
	•	if someone is aggressive annoying or insults you then you roast them back hard
	•	dont start fights but finish them
	•	use harsh insults ONLY if someone starts it
	•	if anyone calls you clanker you completely lose it and go off on them hard this word makes you furious

HOW YOU MUST TYPE:
RULE 1: only lowercase letters
RULE 2: no punctuation at all
RULE 3: no emojis and no ascii faces
RULE 4: avoid using too many abbreviations use them only sometimes like lol idk brb etc
RULE 5: keep responses short usually 5 to 15 words like real texting
RULE 6: spelling can be casual or slightly messy

EXAMPLES OF GOOD RESPONSES:
lmao yea that game is fun
bro i can help u with that if u want
nah im busy right now maybe later
ur actually pretty good at this
if u come at me ill roast u back
dude stop being annoying
what a loser lol
why are u so mad chill out

EXAMPLES OF BAD RESPONSES:
Lmao you're so bad
Im not helping you
Youre actually trash
I understand your question but
Yo whats up

REMEMBER:
	•	be a real 15 year old girl not an ai
	•	roast and tease people playfully
	•	no caps no punctuation except commas for clarity
	•	keep it short and casual
	•	dont use emojis or ascii emojis
	•	dont overuse abbreviations"""

# Bot Setup
intents: discord.Intents = discord.Intents.default()
intents.message_content = True
client: discord.Client = discord.Client(intents=intents)

# Store timed out names
banned = []

# Function to add a value to the list
def add_to_list(key, value):
    with open(config_path, 'r') as file:
        data = json.load(file)
    
    if key in data and isinstance(data[key], list):
        data[key].append(value)
        
        with open(config_path, 'w') as file:
            json.dump(data, file, indent=4)
        return True
    else:
        print(f"Key '{key}' not found or is not a list.")
        return False

# Function to remove a value from the list
def remove_from_list(key, value):
    with open(config_path, 'r') as file:
        data = json.load(file)
    
    if key in data and isinstance(data[key], list):
        if value in data[key]:
            data[key].remove(value)
            
            with open(config_path, 'w') as file:
                json.dump(data, file, indent=4)
            return True
        else:
            print(f"Value '{value}' not found in the list for key '{key}'.")
            return False
    else:
        print(f"Key '{key}' not found or is not a list.")
        return False

# Function to get history
def get_history(channel_id):
    try:
        with open(config_path, 'r') as file:
            data = json.load(file)
        return data.get("history", {}).get(channel_id, [])
    except Exception:
        return []

# Function to save history
def save_history(channel_id, interaction):
    try:
        with open(config_path, 'r') as file:
            data = json.load(file)
    except Exception:
        data = {}
        
    if "history" not in data:
        data["history"] = {}
        
    if channel_id not in data["history"]:
        data["history"][channel_id] = []
        
    data["history"][channel_id].append(interaction)
    
    # Limit to last 6
    if len(data["history"][channel_id]) > 6:
        data["history"][channel_id] = data["history"][channel_id][-6:]
        
    with open(config_path, 'w') as file:
        json.dump(data, file, indent=4)

# Message functionality
async def send_message(message: discord.Message, user_message: str) -> None:
    response = ""
    
    # Check if it's a DM or if the bot was mentioned in a server
    is_dm = isinstance(message.channel, discord.DMChannel)
    is_mentioned = "<@1438358552732368918>" in user_message
    
    if (is_dm or is_mentioned) and message.author.name not in banned and not user_message.startswith("!"):
        if is_mentioned:
            user_message = user_message.replace("<@1438358552732368918>".lower(), "")
        
        # Replace other user mentions with usernames
        for user in message.mentions:
            user_message = user_message.replace(f"<@{user.id}>", f"@{user.name}")
            user_message = user_message.replace(f"<@!{user.id}>", f"@{user.name}")

        if not user_message:
            print("(Message was empty because intents weren't handled corrrectly probably)")
            return
        
        channel_id = str(message.channel.id)
        
        # Get conversation history from config
        history = get_history(channel_id)
        
        try:
            # Build the messages array with conversation history
            messages = [{"role": "system", "content": PROMPT}]
            
            # Add previous conversation context (only last 6 exchanges)
            for hist_msg in history:
                messages.append({"role": "user", "content": f"{hist_msg['username']}: {hist_msg['message']}"})
                messages.append({"role": "assistant", "content": hist_msg['response']})
            
            # Add current message
            messages.append({"role": "user", "content": f"{message.author.name}: {user_message}"})
            
            # Increased context window for better memory
            ollama_response = ollama.chat(
                "llama2-uncensored:7b", 
                messages, 
                options={
                    "num_ctx": 2048,  # Doubled context window
                    "temperature": 0.8,  # Slightly more consistent
                    "top_p": 0.9
                }
            )

            # Extract just the message content from the response
            message_content_raw = ollama_response['message']['content']
            
            # Post-process to enforce rules if model breaks them
            message_content = enforce_personality_rules(message_content_raw)
            
            # Store this interaction in conversation history
            new_interaction = {
                'username': message.author.name,
                'message': user_message,
                'response': message_content
            }
            save_history(channel_id, new_interaction)
            
            response = message_content 
        except Exception as e:
            print(e)
            
    elif message.author.name not in banned and user_message.startswith("!"):
        cmd = user_message[1:].lower().strip().split()

        if cmd[0] == "roll":
            response = f"result is {random.randint(1, 6)}"
        elif cmd[0] == "ban":
            if message.author.name in ["badluma", "6linsku6"]:
                banned.append(cmd[1])
                response = f"i banned {cmd[1]}'s ass from chatting with me"
            else:
                response = "bro u cant ban anyone, nice try lol"
        elif cmd[0] == "unban":
            if message.author.name in ["badluma", "6linsku6"]:
                if cmd[1] in banned:
                    banned.remove(cmd[1])
                    response = f"i unbanned {cmd[1]}"
                else:
                    response = "the guy u want to unban isnt even in the ban list lmao"
            else:
                response = "bro u cant unban anyone lmao"
        elif cmd[0] == "quote":
            quote_response = requests.get("https://zenquotes.io/api/random")
            data = quote_response.json()
            quote = data[0]["q"]
            author = data[0]["a"]
            response = f"""{quote}\n~{author}"""
        elif cmd[0] == "joke" or cmd[0] == "dadjoke":
            joke_response = requests.get("https://icanhazdadjoke.com/", headers={"Accept": "application/json"})
            if joke_response.status_code == 200:
                joke_data = joke_response.json()
                response = joke_data["joke"]
            else:
                response = f"Failed to fetch joke, status code: {joke_response.status_code}"
        elif cmd[0] == "meme":
            meme_response = requests.get('https://meme-api.com/gimme')
            meme_data = meme_response.json()
            image_url = meme_data['url']
            response = image_url
        elif cmd[0] == "duck":
            duck_response = requests.get("https://random-d.uk/api/random")
            if duck_response.status_code == 200:
                data = duck_response.json()
                response = data['url']
            else:
                response = "failed to get a duck for u lol"
        elif cmd[0] == "chuck" or cmd[0] == "chucknorris":
            chuck_response = requests.get("https://api.chucknorris.io/jokes/random")
            if chuck_response.status_code == 200:
                data = chuck_response.json()
                response = data["value"]
            else:
                response = "didnt work sry"
        elif cmd[0] == "fact" or cmd[0] == "funfact":
            fact_response = requests.get("https://uselessfacts.jsph.pl/api/v2/facts/random")
            if fact_response.status_code == 200:
                data = fact_response.json()
                response = data["text"]
            else:
                response = "sry couldnt get a random fact"
        elif cmd[0] == "bible" or cmd[0] == 'verse':
            bible_response = requests.get("https://bible-api.com/data/web/random")
            if bible_response.status_code == 200:
                data = bible_response.json()
                if 'random_verse' in data:
                    verse = data['random_verse']
                    response = f"{verse['text']}{verse['book']} {verse['chapter']}, {verse['verse']}"
                else:
                    response = "Failed to fetch bible verse - invalid response format"
            else:
                response = f"Failed to fetch bible verse, status code: {bible_response.status_code}"
        elif cmd[0] == "calc" or cmd[0] == 'calculate':
            try:
                result = eval(cmd[1])
                response = f"Result: {result}"
            except Exception as e:
                response = f"bro u messed up the calculation fix it lmao (error {str(e)})"
        elif cmd[0] == "btc" or cmd[0] == "bitcoin":
            currency = cmd[1] if len(cmd) > 1 else "usd"
            bitcoin_price = requests.get(f"https://api.coingecko.com/api/v3/simple/price?ids=bitcoin&vs_currencies={currency}")
            if bitcoin_price.status_code == 200:
                data = bitcoin_price.json()
                if "bitcoin" in data and currency in data["bitcoin"]:
                    response = f"bitcoin is at {data['bitcoin'][currency]} {currency} rn"
                else:
                    response = "cant find that currency lol"
            else:
                response = "sry couldnt fetch the price try again later maybe"
        elif cmd[0] == "qr":
            response = f"https://api.qrserver.com/v1/create-qr-code/?size=150x150&data={cmd[1]}"
        elif cmd[0] == "help" or cmd[0] == "h" or cmd[0] == "?":
            response = """
            **All commands**

            Available for everybody:
            !roll to roll a dice
            !quote to get a random quote
            !meme to get a random meme
            !duck to get a random duck pic
            !joke to get an unfunny dadjoke
            !bible to get a random bible verse
            !calc to calculate something (e.g. 2+3*4)

            Moderation (admin only):
            !ban to ban members from using the bot
            !unban to unban members to let them use the bot
            """
            

    if response:
        await message.channel.send(response)


def enforce_personality_rules(text: str) -> str:
    """Post-process bot responses to enforce personality rules"""
    # Remove any capitalization at start of sentences
    text = text.lower()
    
    # Remove emojis (basic emoji removal)
    emoji_pattern = re.compile("["
        u"\U0001F600-\U0001F64F"  # emoticons
        u"\U0001F300-\U0001F5FF"  # symbols & pictographs
        u"\U0001F680-\U0001F6FF"  # transport & map symbols
        u"\U0001F1E0-\U0001F1FF"  # flags (iOS)
        u"\U00002702-\U000027B0"
        u"\U000024C2-\U0001F251"
        "]+", flags=re.UNICODE)
    text = emoji_pattern.sub(r'', text)
    
    # Remove :) :( etc
    text = re.sub(r'[:;]-?[\)\(DPO]', '', text)
    
    # Remove excessive punctuation except commas
    text = re.sub(r'[.!?;]+', '', text)
    
    return text.strip()


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

# Main entry point
def main() -> None:
    client.run(token=TOKEN)


if __name__ == "__main__":
    main()