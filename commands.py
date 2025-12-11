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
    response = """
## All Commands
Here are all commands that are currently available.

**Fun & Games**
`!roll` - Roll a dice (1-6)
`!flip or !coinflip` - Flip a coin (heads/tails)
`!randomnumber` or `!randint <low> <high>` - Generate random number (alias)
`!truth` - Get a truth question
`!dare` - Get a dare
`!wyr` - Get a "Would You Rather" question
`!rizz <target>` - Get a pickup line (optionally mention someone)
`!roast` - Get a random insult
`!compliment` - Get a random compliment
`!activity` - Get a random activity suggestion
`!draw <participant1 participant2 ...>` - Randomly choose from participants

**Content & Media**
`!quote` - Get a random inspirational quote
`!fact or !funfact` - Get a random useless fun fact
`!joke or !dadjoke` - Get an unfunny dad joke
`!chuck or !chucknorris` - Get a Chuck Norris joke
`!bible or !verse` - Get a random Bible verse
`!meme` - Get a random meme
`!emote or !emoji` - Get a random custom emote
`!duck` - Get a random duck picture
`!cat` - Get a random cat picture
`!dog` - Get a random dog picture

**Music**
`!play <song>` - Play a song or add it to the queue
`!pause` - Pause the current song
`!resume` - Resume the paused song
`!skip` - Skip to the next song
`!skipback` - Go back to the previous song
`!stop` - Stop music and disconnect from voice channel
`!now` - Show currently playing song
`!queue` - Show the music queue

**Utilities**
`!bitcoin or !btc <eur|usd>` - Get current Bitcoin price
`!calc or !calculate <expression>` - Simple calculator (+, -, *, /)
`!qr <link>` - Generate QR code for a link
`!translate <source_lang> <target_lang> <text>` - Translate text between languages

**Moderation** (admin only)
`!ban <user>` - Ban user from using the bot
`!unban <user>` - Unban user to allow bot usage
    """
    return response

def roll():
    response = f"result is {random.randint(1, 6)}"
    return response
def ban(user, message):
    if message.author.name in config["admin"]:
        if user not in config["banned"]:
            if user not in config["admin"]:
                function.add_to_list("banned", user)
                response = function.get_response(f"i banned {user} from interacting with the bot", f"Banned {user} from interacting with the bot.")
            else:
                response = function.get_response(f"bro u cant ban {user}, theyre an admin", f"{user} cannot be banned because they are an admin.")
        else:
            response = function.get_response(f"{user} is already banned lmao", f"{user} is already banned.")
    else:
        response = function.get_response("bro u cant ban anyone, nice try lol", "You cannot ban anybody because you aren't an admin.")
    return response
def unban(user, message):
    if message.author.name in config["admin"]:
        current_config = function.load_config(config_path)
        if user in current_config["banned"]:
            if user not in ["admin"]:
                current_config["banned"].remove(user)
                function.save_config(current_config, config_path)
                response = function.get_response(f"i unbanned {user}", f"{user} has been unbanned.")
            else:
                response = function.get_response(f"bro u cant unban {user}, theyre an admin", f"{user} cannot be unbanned because they are an admin")
        else:
            response = function.get_response("the guy u want to unban isnt even in the ban list lmao", f"{user} is not banned.")
    else:
        response = function.get_response("bro u cant unban anyone lmao", "You cannot unban anyone because you are not an admin.")
    return response
def quote():
    quote_response = requests.get("https://zenquotes.io/api/random")
    try:
        data = quote_response.json()
        quote = data[0]["q"]
        author = data[0]["a"]
        response = f"""{quote}\n~{author}"""
    except (requests.exceptions.JSONDecodeError, KeyError, IndexError):
        response = function.get_response("failed to get a quote sry :(", "Quote API unavailable.")
    return response
def joke():
    return function.access_api("https://icanhazdadjoke.com/", "joke", function.get_response("failed to get a joke sry :(", "Joke API unavailable."), {"Accept": "application/json"})
def meme():
    return function.access_api('https://meme-api.com/gimme', 'url', function.get_response("failed to get a meme sry :(", "Meme API unavailable."))
def duck():
    return function.access_api("https://random-d.uk/api/random", 'url', function.get_response("failed to get a duck image sry :(", "RandomDuck API unavailable."))
def dog():
    return function.access_api("https://random.dog/woof.json", 'url', function.get_response("failed to get a dog image sorry", "RandomDog API unavailable."))
def cat():
    raw = requests.get("https://api.thecatapi.com/v1/images/search")
    if raw.status_code == 200:
        try:
            data = raw.json()
            response = data[0]['url']
        except (requests.exceptions.JSONDecodeError, KeyError, IndexError):
            response = function.get_response("failed to get a cat image for u sry :(", "TheCatAPI unavailable.")
    else:
        response = function.get_response("failed to get a cat image for u sry :(", "TheCatAPI unavailable.")
    return response
def chuck():
    return function.access_api("https://api.chucknorris.io/jokes/random", 'value', function.get_response("sorry seems like chuck norris is offline XD", "Chuck Norris API unavailable."))
def fact():
    return function.access_api("https://uselessfacts.jsph.pl/api/v2/facts/random", "text", function.get_response("sry couldnt get random fact rn, try again later maybe", "UselessFacts API unavailable."))
def bible():
    bible_response = requests.get("https://bible-api.com/data/web/random")
    if bible_response.status_code == 200:
        try:
            data = bible_response.json()
            if 'random_verse' in data:
                verse = data['random_verse']
                response = f"{verse['text']}{verse['book']} {verse['chapter']}, {verse['verse']}"
            else:
                response = function.get_response("failed to fetch bible verse bc of invalid response format", "Failed to fetch bible verse - invalid response format")
        except (requests.exceptions.JSONDecodeError, KeyError):
            response = function.get_response("sry couldnt get a bible verse", "Couldn't fetch bible verse.")
    else:
        response = function.get_response(f"failed fetching bible verse, heres the status code: {bible_response.status_code}", f"Failed to fetch bible verse, status code: {bible_response.status_code}")
    return response
def calculate(calculation):
    try:
        result = eval(calculation)
        response = function.get_response(f"result is {result}", f"Result: {result}")
    except Exception as e:
        response = function.get_response(f"bro u cant even spell a simple calculation right lmao (error {str(e)})", f"Syntax error: {str(e)}")
    return response
def bitcoin(currency_parameter):
    currency = currency_parameter.lower() if len(str(currency_parameter)) > 1 else "usd"
    bitcoin_price = requests.get(f"https://api.coingecko.com/api/v3/simple/price?ids=bitcoin&vs_currencies={currency}")
    if bitcoin_price.status_code == 200:
        data = bitcoin_price.json()
        if "bitcoin" in data and currency in data["bitcoin"]:
            response = f"bitcoin is at {data['bitcoin'][currency]} {currency} rn"
        else:
            response = function.get_response("cant find that currency, try either eur or usd", "Please use either usd or eur as currency")
    else:
        response = function.get_response("sry couldnt fetch the price try again later maybe", "Failed fetching price.")
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
            response = "Heads"
            return response
        elif raw == 2:
            response = "Tails"
            return response
    else:
        response = function.get_response("wtf how is this possible? it landed edge lmao", "Edge")
        return response
def emote(emotes):
    response = random.choice(emotes)
    return response
def draw(participants):
    if not participants:
        return function.get_response("you need to provide at least two participant to draw from", "At least two participant is required.")
    participant_list = participants.split()
    if len(participant_list) == 1:
        return f"only one participant provided: {participant_list[0]}"
    chosen = random.choice(participant_list)
    response = function.get_response(f"{chosen} was chosen", f"{chosen} was chosen.")
    return response
def rizz():
    response = function.access_api("https://rizzapi.vercel.app/random", "text", function.get_response("rizz api not available rn srry", "Rizz API unavailable."))
    return response
def roast():
    response = function.access_api("https://evilinsult.com/generate_insult.php?lang=en&type=json", "insult",function.get_response("sry u gotta roast that guy urself, api down rn", "EvilInsult API unavailable."))
    return response
def translate(source_lang, target_lang, text):
    # Validate source and target languages
    from process import language_list
    if source_lang not in language_list:
        return f"Invalid source language code. Use !help to see supported languages."
    if target_lang not in language_list:
        return f"Invalid target language code. Use !help to see supported languages."
    
    url = f"https://api.mymemory.translated.net/get?q={text}&langpair={source_lang}|{target_lang}"
    raw = requests.get(url)
    if raw.status_code == 200:
        try:
            data = raw.json()
            if 'responseData' in data and 'translatedText' in data['responseData']:
                response = data['responseData']['translatedText']
                return response
            else:
                return function.get_response("sry couldnt translate that rn try again later", "Translation failed")
        except (requests.exceptions.JSONDecodeError, KeyError):
            return function.get_response("sry couldnt translate that rn try again later", "Translation failed")
    else:
        return function.get_response(f"Sry the translate api is unavailable rn (error {str(raw.status_code)})", f"Translate API unavailable (error {str(raw.status_code)})")
def compliment():
    try:
        response = function.access_api("https://my-fun-api.onrender.com/compliment", "data", function.get_response("sry seems like thats not available rn", "MyFunAPI unavailable."))
        if isinstance(response, dict) and "compliment" in response:
            response = response["compliment"]
        return response
    except Exception as e:
        return function.get_response("sry the compliment service is not available rn", "MyFunAPI unavailable")
def activity():
    response = function.access_api("https://bored-api.appbrewery.com/random", "activity", function.get_response("sry u gotta find smth to do without the api :P", "Bored API unavailable."))
    return response

# Music
async def play_music(message):
    # Start playing music
    if music.music_player is None:
        return "Music player not initialized."
    response = await music.music_player.start(message)
    return response

def skip_song():
    # Skip current song
    if music.music_player is None:
        return "Music player not initialized."
    return music.music_player.skip()

def skip_back_song():
    # Go back to previous song
    if music.music_player is None:
        return "Music player not initialized."
    return music.music_player.skip_back()

def pause_music():
    # Pause music
    if music.music_player is None:
        return "Music player not initialized."
    return music.music_player.pause()

def resume_music():
    # Resume music
    if music.music_player is None:
        return "Music player not initialized."
    return music.music_player.resume()

async def stop_music():
    # Stop music and disconnect
    if music.music_player is None:
        return "Music player not initialized."
    response = await music.music_player.stop()
    return response

def now_playing():
    # Show current song
    if music.music_player is None:
        return "Music player not initialized."
    return music.music_player.now_playing()

def music_queue():
    # Show upcoming songs
    if music.music_player is None:
        return "Music player not initialized."
    return music.music_player.queue_info()

def list_voice_channels(message):
    # List all voice channels in the server
    if message.guild:
        voice_channels = [channel for channel in message.guild.channels if channel.type == discord.ChannelType.voice]
        if voice_channels:
            channel_list = "\n".join([f"• {channel.name}" for channel in voice_channels])
            return f"Voice channels in this server:\n{channel_list}"
        else:
            return "No voice channels found in this server"
    else:
        return "This command can only be used in a server"

print(show_commands())