from typing import Final
from dotenv import load_dotenv
from discord.ext import commands

import functions as function
import process as process

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
    response = "**All commands**\n\n!roll to roll a dice\n!flip or !coinflip to flip a coin\n!random <lowest><highest> to generate a random number\n\n!quote to get a random quote\n!fact to get a random useless funfact\n!joke to get an unfunny dadjoke\n!chuck to get a chuck norris joke\n!bible to get a random bible verse\n\n!bitcoin <eur or usd> to get the current bitcoin value\n!calc or !calculate <calculation> to calculate simple stuff with +-/ (e.g. 5-1+1/24)\n!qr <link> to generate a qr code\n\n!meme to get a random meme\n!emote to get a random emote\n!duck to get a random duck pic\n!cat to get a random cat pic\n!dog to get a random dog pic\n\n**Moderation** (admin only)\n!ban to ban members from using the bot\n!unban to unban members to let them use the bot"
    
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

print(show_commands())