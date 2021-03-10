import discord
import argparse
from textwrap import wrap
from io import BytesIO
import PIL.ImageDraw as ImageDraw
import PIL.ImageFont as ImageFont
import PIL.ImageOps as ImageOps
from pprint import pprint
from log import *
from subreddits import *
from cache import *
from tools import *
from time import sleep

# constants
SYM_M = "-M"

SYM_T = "-T"
SYM_IT = "-IT"
SYM_IB = "-IB"
SYM_URL = "-URL"
SYM_CHECK = [SYM_T, SYM_IT, SYM_IB, SYM_URL]

LOG_DISCORD_NAME = "discord"
LOG_DISCORD_PATH = "./logs/discord.log"

FONT_ARIMO_PATH = "./config/fonts/Arimo/Arimo-Regular.ttf"
FONT_ARIMO = ImageFont.truetype(FONT_ARIMO_PATH, 36)

FONT_ANTON_PATH = "./config/fonts/Anton/Anton-Regular.ttf"
FONT_ANTON = ImageFont.truetype(FONT_ANTON_PATH, 40)

IMAGE_WIDTH_MAX = 500

I_COLOUR_SHADOW = "black"
I_COLOUR_FILL = "white"
I_OFFSET = 2
I_WIDTH_WRAP = 20
I_HEIGHT_PAD = 15
I_HEIGHT_FORCE = 45

T_COLOUR_FILL = "black"
T_WIDTH_WRAP = 28
T_HEIGHT_FORCE = 45
T_PAD = 15
T_RADIUS = 60
T_RADIUS_MULTIPLY = 3

# arguments
parser = argparse.ArgumentParser()
parser.add_argument('-token', type=str)
args = parser.parse_args()

# discord
client = discord.Client()


def parse_message_content(content, sym_start, sym_check):
    cs = content.split(' ')
    csu = content.upper().split()

    sym_all = [sym_start] + sym_check

    positions = [(index_first(csu, sym), sym) for sym in sym_all]

    if not (positions[0][0] == 0 and positions[0][1] == sym_start):
        return None  # message is not for the bot

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


def add_corners(image, radius):
    # Adapted from: https://stackoverflow.com/a/11291419

    # Temporarily double image size so that corners appear smoother when
    # returned back to its original size
    w_orig, h_orig = image.size
    image = image.resize((w_orig * T_RADIUS_MULTIPLY,
                          h_orig * T_RADIUS_MULTIPLY))
    w, h = image.size

    # Add corners
    circle = Image.new('L', (radius * 2, radius * 2), 0)
    draw = ImageDraw.Draw(circle)
    draw.ellipse((0, 0, radius * 2, radius * 2), fill=255)

    alpha = Image.new('L', image.size, "white")
    alpha.paste(circle.crop((0, 0, radius, radius)),
                (0, 0))
    alpha.paste(circle.crop((0, radius, radius, radius * 2)),
                (0, h - radius))
    alpha.paste(circle.crop((radius, 0, radius * 2, radius)),
                (w - radius, 0))
    alpha.paste(circle.crop((radius, radius, radius * 2, radius * 2)),
                (w - radius, h - radius))
    image.putalpha(alpha)

    # Turn transparent corners white
    white = Image.new("RGBA", image.size, "white")
    white.paste(image, (0, 0), image)
    image = white.convert('RGB')

    # Resize to original dimensions
    image = image.resize((w_orig, h_orig))

    return image


def apply_format_twitter(image, list_text):
    text_lines = wrap(' '.join(list_text), width=T_WIDTH_WRAP)
    image = add_corners(image, T_RADIUS)

    top = (T_PAD * 2) + (len(text_lines) * T_HEIGHT_FORCE)
    border = (T_PAD, top, T_PAD, T_PAD)
    image = ImageOps.expand(image, border=border, fill='white')
    draw = ImageDraw.Draw(image)

    for i, text in enumerate(text_lines):
        x = T_PAD
        y = T_PAD + (i * T_HEIGHT_FORCE)
        draw.text((x, y), text, font=FONT_ARIMO, fill=T_COLOUR_FILL)

    return image


def apply_format_impact(image, list_text, top):
    draw = ImageDraw.Draw(image)

    i_width, i_height = image.size
    text_lines = wrap(' '.join(list_text), width=I_WIDTH_WRAP)

    for i, text in enumerate(text_lines):
        t_width, t_height = draw.textsize(text, font=FONT_ANTON)

        x = (i_width - t_width) / 2

        if top:
            y = (i * I_HEIGHT_FORCE)
        else:
            y = (i_height - I_HEIGHT_FORCE - I_HEIGHT_PAD) - \
                (len(text_lines) - (i + 1)) * I_HEIGHT_FORCE

        for pos in [
            (x - I_OFFSET, y - I_OFFSET),
            (x + I_OFFSET, y - I_OFFSET),
            (x - I_OFFSET, y + I_OFFSET),
            (x + I_OFFSET, y + I_OFFSET)
        ]:
            draw.text(pos, text, font=FONT_ANTON, fill=I_COLOUR_SHADOW)

        draw.text((x, y), text, font=FONT_ANTON, fill=I_COLOUR_FILL)

    return image


@client.event
async def on_ready():
    print("Logged in as {0.user}".format(client))


@client.event
async def on_message(message):
    if message.author == client.user:
        return

    commands = parse_message_content(message.content, SYM_M, SYM_CHECK)

    if commands is not None:
        image_path = None

        if SYM_URL in commands and len(commands[SYM_URL]) > 0:
            image_path = download_image(commands[SYM_URL][0], IMAGE_WIDTH_MAX)

        while image_path is None:
            image_path = download_random_image(cache, IMAGE_WIDTH_MAX)

        image = Image.open(image_path)
        image_format = image.format

        if SYM_IT in commands:
            image = apply_format_impact(image, commands[SYM_IT], True)

        if SYM_IB in commands:
            image = apply_format_impact(image, commands[SYM_IB], False)

        if SYM_T in commands:
            image = apply_format_twitter(image, commands[SYM_T])

        with BytesIO() as image_binary:
            image.save(image_binary, image_format)
            image_binary.seek(0)

            await message.channel.send(
                message.author.mention,
                file=discord.File(
                    fp=image_binary,
                    filename='{}.{}'.format(time_ns(), image_format)
                )
            )

            await message.delete()

        update_cache_reddit(cache, subreddits, stop_first_success=False)


print("Init logs")
logger_discord = init_log(LOG_DISCORD_NAME, LOG_DISCORD_PATH)

print("Init subreddits")
subreddits = init_subreddits()

print("Init cache")
cache = init_cache()

print("Updating cache")
while len(cache[UNUSED]) == 0:
    update_cache_reddit(cache, subreddits, stop_first_success=False)  # todo make stop_first_success=False the default
    
    if len(cache[UNUSED]) == 0:
        print("Unused cache is empty. Reattempting cache update in 5 minutes...")
        sleep(60 * 5)  # todo change update_cache_reddit so that wait period is provided as an argument instead

print("Starting bot")
client.run(args.token)
