import discord
import argparse
import logging
from pprint import pprint

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
handler = logging.FileHandler(
    filename='discord.log', encoding='utf-8', mode='w')
handler.setFormatter(logging.Formatter(
    '%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
logger.addHandler(handler)

# discord
client = discord.Client()


@client.event
async def on_ready():
    print('We have logged in as {0.user}'.format(client))


async def process_twitter(message):
    await message.channel.send("twitter")


async def process_impact(message):
    await message.channel.send("impact")


@client.event
async def on_message(message):
    pprint(message)

    if message.author == client.user:
        return

    c = message.content

    if c.startswith(SYMBOL_TWITTER):
        await process_twitter(message)

    elif c.startswith(SYMBOL_IMPACT_TOP) or c.startswith(SYMBOL_IMPACT_BOTTOM):
        await process_impact(message)


client.run(args.token)
