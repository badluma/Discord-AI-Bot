from typing import Final
from dotenv import load_dotenv
from discord.ext import commands

import functions as function
import commands as cmd
import games as game

import os
import re
import json
import time
import random
import discord
import ollama
import requests

config_path = 'config.json'
config = function.load_config(config_path)
banned = config["banned"]
emotes = ["<:1_:1440783147565318265>", "<:2_:1440783161301667910>", "<:3_:1440783172911763669>", "<:amogus:1440824569802788954>", "<:angel:1441062581799489556>", "<:anonymous:1440766225016819772>", "<:arcticFox:1441063285259501670>", "<:blackWitch:1441062189157847040>", "<:blush:1440777955533131776>", "<:coolGuy:1441062264491868210>", "<:crash:1440784746140532849>", "<:croco:1440766300933591210>", "<:cute:1440770218388619395>", "<:deadpool:1440766016891392081>", "<:duck:1440766454591914035>", "<:emo:1441060748175610016>", "<:evil:1440782801812066425>", "<:fbi:1441062362088996965>", "<:happy:1440775333119922378>", "<:huh:1440807952909996153>", "<:itempistolyellow:1440781831392727110>", "<:itemstairsgrey:1440783817689530519>", "<:laugh:1440871493285314633>", "<:laugh2:1440872332494245989>", "<:maggie:1440766480042954782>", "<:nancybrain:1440771404738859189>", "<:nanncy:1440784428703154176>", "<:ninja:1441062523318308924>", "<:nocheating:1440785581641699328>", "<:omE:1440766507188486174>", "<:orang:1440777076939685990>", "<:orangshotgun:1440776793836621917>", "<:patpat:1440826307805052998>", "<:pepecross:1440766656698646740>", "<:pepemonster:1440766828069650442>", "<:queen:1441063203378299031>", "<:robinHood:1441060911501803680>", "<:robloxface:1440809897351712788>", "<:sleepy:1440808831411290213>", "<:stare:1440826772999508090>", "<:suprised:1440826796160450674>", "<:tnt:1440779932870508785>", "<:tuff:1440826292470550693>", "<:ughping:1440766923863228537>", "<:uhm:1440769726786699436>", "<:werewolf:1440820914601066577>"]
# Personality - now more concise to save tokens
PROMPT = """you are nancy, a 15 year old girl who plays video games and chats on discord

BACKSTORY:
	•	you work minimum wage for a discord server owned by maggie
	•	maggie is you mother and makes you live in her basement as a running joke
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

def enforce_personality_rules(text: str) -> str:
    """Post-process bot responses to enforce personality rules"""
    # Remove any capitalization at start of sentences
    text = text.lower()
    
    # Remove AI-like phrases that break character
    ai_phrases = [
        "i apologize", "i'm sorry", "unfortunately", "i cannot", "i can't",
        "i would need", "as an ai", "as a language model", "i don't have",
        "i am not", "i'm not", "please note", "it's important to",
        "i understand", "i can help", "how can i assist", "what do you need"
    ]
    
    for phrase in ai_phrases:
        text = re.sub(rf'\b{phrase}\b[^.]*', '', text, flags=re.IGNORECASE)
    
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
    
    # If response is now empty or too short, provide a fallback Nancy response
    if len(text.strip()) < 3:
        fallback_responses = [
            "lol idk what to say", "nah", "lmao", "bro what", "uhm", "lol",
            "sure whatever", "maybe", "idk", "k", "cool", "weird", "ok"
        ]
        text = random.choice(fallback_responses)
    
    return text.strip()

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
        history = function.get_history(channel_id)
        
        try:
            # Build the messages array with conversation history
            # Add system prompt with higher emphasis
            messages = [
                {"role": "system", "content": PROMPT},
                {"role": "system", "content": "REMEMBER: You are Nancy, a 15 year old girl. NEVER break character. Always follow the personality rules above."}
            ]
            
            # Add previous conversation context (only last 6 exchanges)
            for hist_msg in history:
                messages.append({"role": "user", "content": f"{hist_msg['username']}: {hist_msg['message']}"})
                messages.append({"role": "assistant", "content": hist_msg['response']})
            
            # Add current message
            messages.append({"role": "user", "content": f"{message.author.name}: {user_message}"})
            
            # Use a better model for character consistency
            ollama_response = ollama.chat(
                "llama2-uncensored:7b", 
                messages, 
                options={
                    "num_ctx": 4096,  # Larger context window
                    "temperature": 0.7,  # Lower temperature for more consistency
                    "top_p": 0.85,
                    "repeat_penalty": 1.1  # Reduce repetitive AI-like responses
                }
            )

            # Extract just the message content from the response
            message_content_raw = ollama_response['message']['content']
            
            # Post-process to enforce rules if model breaks them
            message_content = enforce_personality_rules(message_content_raw)
            
            # Double-check for character breaks and force correction if needed
            if any(phrase in message_content.lower() for phrase in ["i apologize", "as an ai", "language model", "i cannot", "i'm sorry"]):
                # Force a Nancy-like response if character is broken
                fallback_responses = [
                    "lol whatever", "nah", "lmao", "bro what", "uhm ok", "sure",
                    "maybe idk", "k", "cool", "weird but ok", "fine whatever"
                ]
                message_content = random.choice(fallback_responses)
            
            # Store this interaction in conversation history
            new_interaction = {
                'username': message.author.name,
                'message': user_message,
                'response': message_content
            }
            function.save_history(channel_id, new_interaction)
            
            response = message_content 
        except Exception as e:
            print(e)
            
    elif message.author.name not in banned and user_message.startswith("!"):
        command_parts = user_message[1:].lower().strip().split()

        if command_parts[0] == "roll":
            response = cmd.roll()
        elif command_parts[0] == "ban":
            response = cmd.ban(command_parts[1] if len(command_parts) > 1 else "", message)
        elif command_parts[0] == "unban":
            response = cmd.unban(command_parts[1] if len(command_parts) > 1 else "", message)
        elif command_parts[0] == "quote":
            response = cmd.quote()
        elif command_parts[0] == "joke" or command_parts[0] == "dadjoke":
            response = cmd.joke()
        elif command_parts[0] == "meme":
            response = cmd.meme()
        elif command_parts[0] == "duck":
            response = cmd.duck()
        elif command_parts[0] == "dog":
            response = cmd.dog()
        elif command_parts[0] == "cat":
            response = cmd.cat()
        elif command_parts[0] == "chuck" or command_parts[0] == "chucknorris":
            response = cmd.chuck()
        elif command_parts[0] == "fact" or command_parts[0] == "funfact":
            response = cmd.fact()
        elif command_parts[0] == "bible" or command_parts[0] == 'verse':
            response = cmd.bible()
        elif command_parts[0] == "calc" or command_parts[0] == 'calculate':
            response = cmd.calculate(command_parts[1] if len(command_parts) > 1 else "")
        elif command_parts[0] == "btc" or command_parts[0] == "bitcoin":
            response = cmd.bitcoin(command_parts[1] if len(command_parts) > 1 else "usd")
        elif command_parts[0] == "qr":
            response = cmd.qr(command_parts[1] if len(command_parts) > 1 else "")
        elif command_parts[0] == "random" or command_parts[0] == 'rand':
            low = int(command_parts[1]) if len(command_parts) > 1 and command_parts[1].isdigit() else 0
            high = int(command_parts[2]) if len(command_parts) > 2 and command_parts[2].isdigit() else 100
            response = str(cmd.random_digit(low, high))
        elif command_parts[0] == "coinflip" or command_parts[0] == "flip":
            response = cmd.coinflip()
        elif command_parts[0] == "emote" or command_parts[0] == "emoji":
            response = cmd.emote(emotes)
        
        elif command_parts[0] == "russianroulette" or command_parts[0] == 'rr':
            participants = []
            for user in message.mentions:
                participants.append(user.name)
            if not participants and len(command_parts) > 1:
                participants = command_parts[1:]
            
            await game.russian_roulette(message, participants)
            return

        elif command_parts[0] == "help" or command_parts[0] == "h" or command_parts[0] == "?":
            response = cmd.show_commands()

    if response:
        await message.channel.send(str(response))