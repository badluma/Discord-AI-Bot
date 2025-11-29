from typing import Final
from dotenv import load_dotenv
from discord.ext import commands

import functions as function
import music

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


def show_commands():
    response = "**Fun & Games**\n!roll - Roll a dice (1-6)\n!flip or !coinflip - Flip a coin (heads/tails)\n!random <low> <high> - Generate random number between two values\n!randomnumber or !randint <low> <high> - Generate random number (alias)\n!tord <t|d|r> - Truth or Dare (t=truth, d=dare, r=random)\n!truth - Get a truth question\n!dare - Get a dare\n!wyr - Get a \"Would You Rather\" question\n!rizz [target] - Get a pickup line (optionally mention someone)\n!roast - Get a random insult\n!compliment - Get a random compliment\n!activity - Get a random activity suggestion\n!draw <participants...> - Randomly choose from participants\n\n**Content & Media**\n!quote - Get a random inspirational quote\n!fact or !funfact - Get a random useless fun fact\n!joke or !dadjoke - Get an unfunny dad joke\n!chuck or !chucknorris - Get a Chuck Norris joke\n!bible or !verse - Get a random Bible verse\n!meme - Get a random meme\n!emote or !emoji - Get a random custom emote\n!duck - Get a random duck picture\n!cat - Get a random cat picture\n!dog - Get a random dog picture\n\n**Music**\n!play <song> - Play a song or add it to the queue\n!pause - Pause the current song\n!resume - Resume the paused song\n!skip - Skip to the next song\n!skipback - Go back to the previous song\n!stop - Stop music and disconnect from voice channel\n!now - Show currently playing song\n!queue - Show the music queue\n\n**Utilities**\n!bitcoin or !btc <eur|usd> - Get current Bitcoin price\n!calc or !calculate <expression> - Simple calculator (+, -, *, /)\n!qr <link> - Generate QR code for a link\n!translate <source_lang> <target_lang> <text> - Translate text between languages\n\n**Moderation** (admin only)\n!ban <user> - Ban user from using the bot\n!unban <user> - Unban user to allow bot usage"
    
    return response

def roll():
    response = f"result is {random.randint(1, 6)}"
    return response
def ban(user, message):
    if message.author.name in config["bot_admin"]:
        if user not in config["banned"]:
            if user not in config["admin"] and user not in config["bot_admin"]:
                function.add_to_list("banned", user)
                response = f"i banned {user} from interacting with the bot"
            else:
                response = f"bro u cant ban {user}, theyre an admin"
        else:
            response = f"{user} is already banned lmao"
    else:
        response = "bro u cant ban anyone, nice try lol"
    return response
def unban(user, message):
    if message.author.name in config["bot_admin"]:
        current_config = function.load_config(config_path)
        if user in current_config["banned"]:
            if user not in ["admin"] and user not in ["bot_admin"]:
                current_config["banned"].remove(user)
                function.save_config(current_config, config_path)
                response = f"i unbanned {user}"
            else:
                response = f"bro u cant unban {user}, theyre an admin"
        else:
            response = "the guy u want to unban isnt even in the ban list lmao"
    else:
        response = "bro u cant unban anyone lmao"
    return response
def quote():
    quote_response = requests.get("https://zenquotes.io/api/random")
    try:
        data = quote_response.json()
        quote = data[0]["q"]
        author = data[0]["a"]
        response = f"""{quote}\n~{author}"""
    except (requests.exceptions.JSONDecodeError, KeyError, IndexError):
        response = "failed to get a quote sry :("
    return response
def joke():
    return function.access_api("https://icanhazdadjoke.com/", "joke", "failed to get a joke sry :(", {"Accept": "application/json"})
def meme():
    return function.access_api('https://meme-api.com/gimme', 'url', "failed to get a meme sry :(")
def duck():
    return function.access_api("https://random-d.uk/api/random", 'url', "failed to get a duck image sry :(")
def dog():
    return function.access_api("https://random.dog/woof.json", 'url', "failed to get a pic image sorry")
def cat():
    raw = requests.get("https://api.thecatapi.com/v1/images/search")
    if raw.status_code == 200:
        try:
            data = raw.json()
            response = data[0]['url']
        except (requests.exceptions.JSONDecodeError, KeyError, IndexError):
            response = "failed to get a cat image for u sry :("
    else:
        response = "failed to get a cat image for u sry :("
    return response
def chuck():
    return function.access_api("https://api.chucknorris.io/jokes/random", 'value', "sorry seems like chuck norris is offline XD")
def fact():
    return function.access_api("https://uselessfacts.jsph.pl/api/v2/facts/random", "text", "sry couldnt get random fact rn, try again later maybe")
def bible():
    bible_response = requests.get("https://bible-api.com/data/web/random")
    if bible_response.status_code == 200:
        try:
            data = bible_response.json()
            if 'random_verse' in data:
                verse = data['random_verse']
                response = f"{verse['text']}{verse['book']} {verse['chapter']}, {verse['verse']}"
            else:
                response = "Failed to fetch bible verse - invalid response format"
        except (requests.exceptions.JSONDecodeError, KeyError):
            response = "sry couldnt get a bible verse"
    else:
        response = f"Failed to fetch bible verse, status code: {bible_response.status_code}"
    return response
def calculate(calculation):
    try:
        result = eval(calculation)
        response = f"Result: {result}"
    except Exception as e:
        response = f"bro u cant even spell a simple calculation right lmao (error {str(e)})"
    return response
def bitcoin(currency_parameter):
    currency = currency_parameter.lower() if len(str(currency_parameter)) > 1 else "usd"
    bitcoin_price = requests.get(f"https://api.coingecko.com/api/v3/simple/price?ids=bitcoin&vs_currencies={currency}")
    if bitcoin_price.status_code == 200:
        data = bitcoin_price.json()
        if "bitcoin" in data and currency in data["bitcoin"]:
            response = f"bitcoin is at {data['bitcoin'][currency]} {currency} rn"
        else:
            response = "cant find that currency, try either eur or usd"
    else:
        response = "sry couldnt fetch the price try again later maybe"
    return response
def qr(link):
    response = f"https://api.qrserver.com/v1/create-qr-code/?size=150x150&data={link}"
    return response
def random_digit(lowest=0, highest=100):
    response = random.randint(int(lowest), int(highest))
    return response
def coinflip():
    raw = random.randint(0, 5000)
    if raw != 0:
        raw = random.randint(1, 2)
        if raw == 1:
            response = "heads"
            return response
        elif raw == 2:
            response = "tails"
            return response
    else:
        response = "wtf how is this possible? it landed edge lmao"
        return response
def emote(emotes):
    response = random.choice(emotes)
    return response
def draw(participants):
    if not participants:
        return "you need to provide at least one participant to draw from"
    participant_list = participants.split()
    if len(participant_list) == 1:
        return f"only one participant provided: {participant_list[0]}"
    chosen = random.choice(participant_list)
    response = f"{chosen} was chosen"
    return response
def rizz():
    response = function.access_api("https://rizzapi.vercel.app/random", "text", "rizz api not available rn srry")
    return response.lower()
def roast():
    response = function.access_api("https://evilinsult.com/generate_insult.php?lang=en&type=json", "insult", "sry u gotta roast that guy urself, api down rn")
    return response
def translate(source_lang, target_lang, text):
    # Validate source and target languages
    from process import language_list
    if source_lang not in language_list:
        return f"invalid source language code. use !help to see supported languages"
    if target_lang not in language_list:
        return f"invalid target language code. use !help to see supported languages"
    
    url = f"https://api.mymemory.translated.net/get?q={text}&langpair={source_lang}|{target_lang}"
    raw = requests.get(url)
    if raw.status_code == 200:
        try:
            data = raw.json()
            if 'responseData' in data and 'translatedText' in data['responseData']:
                response = data['responseData']['translatedText']
                return response
            else:
                return "sry couldnt translate that rn try again later"
        except (requests.exceptions.JSONDecodeError, KeyError):
            return "sry couldnt translate that rn try again later"
    else:
        return f"Sry the translate api is unavailable rn (error {str(raw.status_code)})"
def compliment():
    try:
        response = function.access_api("https://my-fun-api.onrender.com/compliment", "data", "sry seems like thats not available rn")
        if isinstance(response, dict) and "compliment" in response:
            response = response["compliment"]
        return response
    except Exception as e:
        return "sry the compliment service is not available rn"
def activity():
    response = function.access_api("https://bored-api.appbrewery.com/random", "activity", "sry u gotta find smth to do without the api :P")
    return response
# def disney(character_parameter):
#     character = character_parameter.lower()
#     character_info = requests.get("https://api.disneyapi.dev")
#     if character_info.status_code == 200:
#         data = character_info.json()
#         if character in data["bitcoin"]:
#             fi
            
#             response = f"bitcoin is at {data['bitcoin'][currency]} {currency} rn"
#         else:
#             response = "sry couldnt find that character"
#     else:
#         response = "sry couldnt fetch the price try again later maybe"
#     return response

# Music

async def play_music(message):
    """Start playing music"""
    if music.music_player is None:
        return "music player not initialized"
    response = await music.music_player.start(message)
    return response

def skip_song():
    """Skip current song"""
    if music.music_player is None:
        return "music player not initialized"
    return music.music_player.skip()

def skip_back_song():
    """Go back to previous song"""
    if music.music_player is None:
        return "music player not initialized"
    return music.music_player.skip_back()

def pause_music():
    """Pause music"""
    if music.music_player is None:
        return "music player not initialized"
    return music.music_player.pause()

def resume_music():
    """Resume music"""
    if music.music_player is None:
        return "music player not initialized"
    return music.music_player.resume()

async def stop_music():
    """Stop music and disconnect"""
    if music.music_player is None:
        return "music player not initialized"
    response = await music.music_player.stop()
    return response

def now_playing():
    """Show current song"""
    if music.music_player is None:
        return "music player not initialized"
    return music.music_player.now_playing()

def music_queue():
    """Show upcoming songs"""
    if music.music_player is None:
        return "music player not initialized"
    return music.music_player.queue_info()

def list_voice_channels(message):
    """List all voice channels in the server"""
    if message.guild:
        voice_channels = [channel for channel in message.guild.channels if channel.type == discord.ChannelType.voice]
        if voice_channels:
            channel_list = "\n".join([f"• {channel.name}" for channel in voice_channels])
            return f"Voice channels in this server:\n{channel_list}"
        else:
            return "No voice channels found in this server"
    else:
        return "This command can only be used in a server"