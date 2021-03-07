import discord
import argparse
from math import floor
from pprint import pprint
from textwrap import wrap
from PIL import ImageDraw, ImageFont
from log import *
from subreddits import *
from cache import *

# constants
SYM_M = "-M"
SYM_T = "-T"
SYM_IT = "-IT"
SYM_IB = "-IB"
SYM_CHECK = [SYM_T, SYM_IT, SYM_IB]

LOG_DISCORD_NAME = "discord"
LOG_DISCORD_PATH = "./logs/discord.log"

FONT_SIZE_I = 40
FONT_ANTON_PATH = "./config/fonts/Anton/Anton-Regular.ttf"
FONT_ANTON = ImageFont.truetype(FONT_ANTON_PATH, FONT_SIZE_I)

IMAGE_WIDTH_MAX = 500

I_COLOUR_SHADOW = "black"
I_COLOUR_FILL = "white"
I_BORDER = 2
I_HEIGHT_PAD = 15
T_HEIGHT_FORCE = 45

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

    content = message.content


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


def on_message_stub(content):
    commands = parse_message_content(content, SYM_M, SYM_CHECK)

    if commands is not None:
        image_path = download_random_image(cache, IMAGE_WIDTH_MAX)
        image = Image.open(image_path)
        draw = ImageDraw.Draw(image)

        i_width, i_height = image.size
        text_lines = wrap(' '.join(commands[SYM_IB]), width=20)

        for i, text in enumerate(text_lines):
            t_width, t_height = draw.textsize(text, font=FONT_ANTON)

            x = (i_width - t_width) / 2
            y = (i_height - T_HEIGHT_FORCE - I_HEIGHT_PAD) - \
                (len(text_lines) - (i + 1)) * T_HEIGHT_FORCE

            for pos in [
                (x - I_BORDER, y - I_BORDER),
                (x + I_BORDER, y - I_BORDER),
                (x - I_BORDER, y + I_BORDER),
                (x + I_BORDER, y + I_BORDER)
            ]:
                draw.text(pos, text, font=FONT_ANTON, fill=I_COLOUR_SHADOW)

            draw.text((x, y), text, font=FONT_ANTON, fill=I_COLOUR_FILL)

        image.save('{}.{}'.format(time_ns(), image.format))


on_message_stub("-m -ib me when the")
