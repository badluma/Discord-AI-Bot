import random
import discord

from dotenv import load_dotenv
from discord.ext import commands

def remove_chars(input_string, chars_to_remove):
    removal_table = str.maketrans('', '', chars_to_remove)
    result_string = input_string.translate(removal_table)
    return result_string

async def russian_roulette(message_parameter, participants):
    if not participants or len(participants) < 2:
        return "need at least 2 people to play"
    
    alive = list(participants)
    bullets = 6
    await message_parameter.channel.send("Russian roulette starting with " + str(alive).replace("'", "").replace("[", "").replace("]", "") + "!")
    
    while len(alive) > 1:
        for player in alive:
            if len(alive) == 1:
                break
            
            if random.randint(1, bullets) == 1:
                await message_parameter.channel.send(player + " got shot")
                alive.remove(player)
                bullets = 6
                if len(alive) > 1:
                    await message_parameter.channel.send(player + str(alive).replace("'", "").replace("[", "").replace("]", ""))
                break
            else:
                await message_parameter.channel.send(str("click " + player + " survived"))
                bullets -= 1
    
    if alive:
        await message_parameter.channel.send(f"**{alive[0]}** won the game! **Congratulations!**\n\nhttps://media2.giphy.com/media/v1.Y2lkPTc5MGI3NjExOG10NnY0MXYwNDlxaWFrbXZudXpkb2swY2tscmhmZ3NoOWlpcmlkcCZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/LcpsCfdinbzNfHOtWB/giphy.gif")
    
    return ""