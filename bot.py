import discord
import argparse
from pprint import pprint
from log import *
from subreddits import *
from cache import *

# constants
LOG_DISCORD_NAME = "discord"
LOG_DISCORD_PATH = "./logs/discord.log"

SYM_M = "-M"
SYM_T = "-T"
SYM_IT = "-IT"
SYM_IB = "-IB"
SYM_CHECK = [SYM_T, SYM_IT, SYM_IB]

# arguments
parser = argparse.ArgumentParser()
parser.add_argument('-token', type=str)
args = parser.parse_args()

# discord
client = discord.Client()


@client.event
async def on_ready():
    print("Logged in as {0.user}".format(client))


# async def process_twitter(message):
#     await message.channel.send("...")


@client.event
async def on_message(message):
    if message.author == client.user:
        return

    content = message.content.split(' ')
    commands = parse_message_content(content, SYM_M, SYM_CHECK)

    if commands is not None:
        pprint(commands)

    # path_image = download_random_image(cache)
    # with open(path_image, 'rb') as f:
    #    await message.channel.send(file=discord.File(f))


print("Init logs")
logger_discord = init_log(LOG_DISCORD_NAME, LOG_DISCORD_PATH)

print("Init subreddits")
subreddits = init_subreddits()

print("Init cache")
cache = init_cache()

print("Updating cache")
# update_cache_reddit(cache, subreddits)

print("Starting bot")
# client.run(args.token)


def _index_first(lst, val, default=-1):
    return lst.index(val) if val in lst else default


def parse_message_content(content, sym_start, sym_check):
    cs = content.split(' ')
    csu = content.upper().split()

    sym_all = [sym_start] + sym_check

    positions = [(_index_first(csu, sym), sym) for sym in sym_all]

    if not (positions[0][0] == 0 and positions[0][1] == sym_start):
        return None  # incorrect first command

    positions_sorted = sorted(positions)
    positions_len = len(positions)
    cs_len = len(cs)

    commands = {}

    for index in range(positions_len):
        pos = positions_sorted[index][0]
        cmd = positions_sorted[index][1]

        if pos == -1:
            continue

        if index + 1 < positions_len:
            next_pos = positions_sorted[index + 1][0]
        else:
            next_pos = cs_len

        commands[cmd] = [cs[i] for i in range(pos + 1, next_pos)]

    return commands


pprint(parse_message_content(
    "-m some command -t me when the -it bruh -ib bottom text",
    SYM_M, SYM_CHECK))
