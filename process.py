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



game_running = False
config_path = 'config.json'
config = function.load_config(config_path)
slurs_path = 'slurs.json'
slurs = function.load_config(slurs_path)
banned = config["banned"]
PROMPT = config.get("prompt", "")
emotes = ["<:1_:1440783147565318265>", 
          "<:2_:1440783161301667910>", 
          "<:3_:1440783172911763669>", 
          "<:amogus:1440824569802788954>", 
          "<:angel:1441062581799489556>", 
          "<:anonymous:1440766225016819772>", 
          "<:arcticFox:1441063285259501670>", 
          "<:blackWitch:1441062189157847040>", 
          "<:blush:1440777955533131776>", 
          "<:coolGuy:1441062264491868210>", 
          "<:crash:1440784746140532849>", 
          "<:croco:1440766300933591210>", 
          "<:cute:1440770218388619395>", 
          "<:deadpool:1440766016891392081>", 
          "<:duck:1440766454591914035>", 
          "<:emo:1441060748175610016>", 
          "<:evil:1440782801812066425>", 
          "<:fbi:1441062362088996965>", 
          "<:happy:1440775333119922378>", 
          "<:huh:1440807952909996153>", 
          "<:itempistolyellow:1440781831392727110>", 
          "<:itemstairsgrey:1440783817689530519>", 
          "<:laugh:1440871493285314633>", 
          "<:laugh2:1440872332494245989>", 
          "<:maggie:1440766480042954782>", 
          "<:nancybrain:1440771404738859189>", 
          "<:nanncy:1440784428703154176>", 
          "<:ninja:1441062523318308924>", 
          "<:nocheating:1440785581641699328>", 
          "<:omE:1440766507188486174>", 
          "<:orang:1440777076939685990>", 
          "<:orangshotgun:1440776793836621917>", 
          "<:patpat:1440826307805052998>", 
          "<:pepecross:1440766656698646740>", 
          "<:pepemonster:1440766828069650442>", 
          "<:queen:1441063203378299031>", 
          "<:robinHood:1441060911501803680>", 
          "<:robloxface:1440809897351712788>", 
          "<:sleepy:1440808831411290213>", 
          "<:stare:1440826772999508090>", 
          "<:suprised:1440826796160450674>", 
          "<:tnt:1440779932870508785>", 
          "<:tuff:1440826292470550693>", 
          "<:ughping:1440766923863228537>", 
          "<:uhm:1440769726786699436>", 
          "<:werewolf:1440820914601066577>"]

languages = ("Arabic: `ar`\n"
    "Azerbaijani: `az`\n"
    "Chinese: `zh`\n"
    "Czech: `cs`\n"
    "Danish: `da`\n"
    "Dutch: `nl`\n"
    "English: `en`\n"
    "Esperanto: `eo`\n"
    "Finnish: `fi`\n"
    "French: `fr`\n"
    "German: `de`\n"
    "Greek: `el`\n"
    "Hebrew: `he`\n"
    "Hindi: `hi`\n"
    "Hungarian: `hu`\n"
    "Indonesian: `id`\n"
    "Irish: `ga`\n"
    "Italian: `it`\n"
    "Japanese: `ja`\n"
    "Kabyle: `kab`\n"
    "Korean: `ko`\n"
    "Occitan: `oc`\n"
    "Persian: `fa`\n"
    "Polish: `pl`\n"
    "Portuguese: `pt`\n"
    "Russian: `ru`\n"
    "Slovak: `sk`\n"
    "Spanish: `es`\n"
    "Swedish: `sv`\n"
    "Turkish: `tr`\n"
    "Ukrainian: `uk`\n"
    "Vietnamese: `vi`\n")

language_list = ["ar", "zh", "cs", "da", "nl", "en", "eo", "fi", 
                 "fr", "de", "el", "he", "hi", "hu", "id", "ga", 
                 "it", "ja", "kab", "ko", "oc", "fa", "pl", "pt", 
                 "ru", "sk", "es", "sv", "tr", "uk", "vi"]

# PROMPT = Final[str] = os.getenv("PROMPT") or ""

def enforce_personality_rules(text: str) -> str:
    # --- Post-process bot responses to enforce personality rules ---
    # Remove any capitalization at start of sentences
    text = text.lower()
    
    # Remove AI-like phrases that break character
    ai_phrases = [
        "i apologize", "unfortunately",
        "as an ai", "i don't have", "please note",
        "i understand", "how can i assist"
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
    global game_running
    response = ""
    
    # Check if it's a DM or if the bot was mentioned in a server
    is_dm = isinstance(message.channel, discord.DMChannel)
    is_mentioned = config["ai_trigger"] in user_message
    
    if (is_dm or is_mentioned) and message.author.name not in banned and not user_message.startswith("!"):
        if is_mentioned:
            user_message = user_message.replace(config["ai_trigger"].lower(), "")
        
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
            ]
            
            # Add previous conversation context (only last 6 exchanges)
            for hist_msg in history:
                messages.append({"role": "user", "content": f"{hist_msg['username']}: {hist_msg['message']}"})
                messages.append({"role": "assistant", "content": hist_msg['response']})
            
            # Add current message
            messages.append({"role": "user", "content": f"{message.author.name}: {user_message}"})
            
            # Use a better model for character consistency
            ollama_response = ollama.chat(
                config["model"], 
                messages, 
                options={
                    "num_ctx": 4096,  # Larger context window
                    "temperature": 0.7, # Lower temperature for more consistency
                    "top_p": 0.85,
                    "repeat_penalty": 1.1 # Reduce repetitive AI-like responses
                }
            )

            # Extract just the message content from the response
            message_content = ollama_response['message']['content']

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
        cmd_parts = user_message[1:].lower().strip().split()

        if cmd_parts[0] == "roll":
            response = cmd.roll()
        elif cmd_parts[0] == "ban":
            response = cmd.ban(cmd_parts[1] if len(cmd_parts) > 1 else "", message)
        elif cmd_parts[0] == "unban":
            response = cmd.unban(cmd_parts[1] if len(cmd_parts) > 1 else "", message)
        elif cmd_parts[0] == "quote":
            response = cmd.quote()
        elif cmd_parts[0] == "joke" or cmd_parts[0] == "dadjoke":
            response = cmd.joke()
        elif cmd_parts[0] == "meme":
            response = cmd.meme()
        elif cmd_parts[0] == "duck":
            response = cmd.duck()
        elif cmd_parts[0] == "dog":
            response = cmd.dog()
        elif cmd_parts[0] == "cat":
            response = cmd.cat()
        elif cmd_parts[0] == "chuck" or cmd_parts[0] == "chucknorris":
            response = cmd.chuck()
        elif cmd_parts[0] == "fact" or cmd_parts[0] == "funfact":
            response = cmd.fact()
        elif cmd_parts[0] == "bible" or cmd_parts[0] == 'verse':
            response = cmd.bible()
        elif cmd_parts[0] == "calc" or cmd_parts[0] == 'calculate':
            response = cmd.calculate(cmd_parts[1] if len(cmd_parts) > 1 else "")
        elif cmd_parts[0] == "btc" or cmd_parts[0] == "bitcoin":
            response = cmd.bitcoin(cmd_parts[1] if len(cmd_parts) > 1 else "usd")
        elif cmd_parts[0] == "qr":
            response = cmd.qr(cmd_parts[1] if len(cmd_parts) > 1 else "")
        elif cmd_parts[0] == "activity":
            response = cmd.activity()
        elif cmd_parts[0] == "roast" or cmd_parts[0] == "insult":
            if len(cmd_parts) > 1:
                response = f"{cmd_parts[1]} {cmd.roast()}"
            else:
                response = cmd.roast()
        elif cmd_parts[0] == "compliment" or cmd_parts[0] == "nice":
            if len(cmd_parts) > 1: # Checks if an argument is given
                response = f"{cmd_parts[1]} {cmd.compliment()}"
            else:
                response = cmd.compliment() # If no argument is given, the command excecutes without printing a name
        elif cmd_parts[0] == "rizz" or cmd_parts[0] == "pickup":
            if len(cmd_parts) > 1:
                response = f"{' '.join(cmd_parts[1:])}, {cmd.rizz()}"
            else:
                response = cmd.rizz()
        elif cmd_parts[0] == "randomnumber" or cmd_parts[0] == "randint":
            low = int(cmd_parts[1]) if len(cmd_parts) > 1 and cmd_parts[1].isdigit() else 0
            high = int(cmd_parts[2]) if len(cmd_parts) > 2 and cmd_parts[2].isdigit() else 100
            response = str(cmd.random_digit(low, high))
        elif cmd_parts[0] == "coinflip" or cmd_parts[0] == "flip":
            response = cmd.coinflip()
        elif cmd_parts[0] == "emote" or cmd_parts[0] == "emoji":
            response = cmd.emote(emotes)
        elif cmd_parts[0] == "draw":
            if len(cmd_parts) > 1:
                participants = ' '.join(cmd_parts[1:])
                response = cmd.draw(participants)
            else:
                response = "you need to provide participants to draw from"
        elif cmd_parts[0] == "translate" or cmd_parts[0] == "trans":
            if len(cmd_parts) == 1:
                response = f"**Supported Languages:**\n{languages}\n**Usage:** !translate source_lang target_lang text"
            elif len(cmd_parts) >= 3:
                source_lang = cmd_parts[1]
                target_lang = cmd_parts[2]
                # Extract text after the command and language codes
                text_start = len(cmd_parts[0]) + len(source_lang) + len(target_lang) + 3  # +3 for spaces and !
                text = user_message[text_start:].strip()
                if text:
                    response = cmd.translate(source_lang, target_lang, text)
                else:
                    response = "u need to provide text to translate. format: !translate source_lang target_lang text"
            else:
                response = "Wrong format. Use: !translate source_lang target_lang text"
        elif cmd_parts[0] == "truth":
            response = game.tord("truth")
        elif cmd_parts[0] == "dare":
            response = game.tord("dare")
        elif cmd_parts[0] == "wyr":
            response = game.wyr()

        elif cmd_parts[0] == "help" or cmd_parts[0] == "h" or cmd_parts[0] == "?":
            await message.channel.send(str(cmd.show_commands()))
            return

        # Music
        elif cmd_parts[0] == "listvc":
            response = cmd.list_voice_channels(message)

        elif cmd_parts[0] == "play":
            response = await cmd.play_music(message)
        elif cmd_parts[0] == "pause":
            response = cmd.pause_music()
        elif cmd_parts[0] == "resume":
            response = cmd.resume_music()
        elif cmd_parts[0] == "skip":
            response = cmd.skip_song()
        elif cmd_parts[0] == "skipback":
            response = cmd.skip_back_song()
        elif cmd_parts[0] == "stop":
            response = await cmd.stop_music()
        elif cmd_parts[0] == "now":
            response = cmd.now_playing()
        elif cmd_parts[0] == "queue":
            response = cmd.music_queue()
    
    function.save_config(config, config_path)

    if response:
        # Check if response is a URL (starts with http:// or https://)
        is_url = response.startswith('http://') or response.startswith('https://')
        
        if config["is_casual"] == True and not is_url:
            response = enforce_personality_rules(response)
        elif config["is_casual"] == False:
            pass
        else:
            print(f"\nInvalid value for is_casual in config.json: '{config["is_casual"]}'. Please use either true or false\n")

        await message.channel.send(str(response))