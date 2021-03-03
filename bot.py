import discord
import argparse
import logging
from pathlib import Path
from cache import *

# constants
SYMBOL_TWITTER = 'm~'
SYMBOL_IMPACT_TOP = "m-"
SYMBOL_IMPACT_BOTTOM = "m_"

# arguments
parser = argparse.ArgumentParser()
parser.add_argument('-token', type=str)
args = parser.parse_args()

# logging
logger = logging.getLogger('discord')
logger.setLevel(logging.DEBUG)
Path("./logs").mkdir(parents=True, exist_ok=True)
handler = logging.FileHandler(
    filename='./logs/discord.log', encoding='utf-8', mode='w')
handler.setFormatter(logging.Formatter(
    '%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
logger.addHandler(handler)

# discord
client = discord.Client()


@client.event
async def on_ready():
    print('Logged in as {0.user}'.format(client))


# async def process_twitter(message):
#     await message.channel.send("...")


@client.event
async def on_message(message):
    if message.author == client.user:
        return

    c = message.content

    if c.startswith("~m"):
        path_image = download_random_image(cache)
        with open(path_image, 'rb') as f:
            await message.channel.send(file=discord.File(f))


print("Init subreddits")
subreddits = init_subreddits()

print("Init cache")
cache = init_cache()

print("Updating cache")
# update_cache_reddit(cache, subreddits)

print("Starting bot")
client.run(args.token)
