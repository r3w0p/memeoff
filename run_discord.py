import discord
import argparse
from io import BytesIO
from time import sleep
from PIL import ImageFont
from src.subreddits import *
from src.meme import *
from src.cache import *

# arguments
parser = argparse.ArgumentParser()
parser.add_argument('-token', type=str)
args = parser.parse_args()

# directories
DIR_FILE = Path(__file__).parent.absolute()
DIR_CACHE = "cache"
DIR_CONFIG = "config"
DIR_FONTS = "fonts"
DIR_LOGS = "logs"
DIR_SRC = "src"

# paths
PATH_CACHE_UNUSED = DIR_FILE / DIR_CACHE / "unused.csv"
PATH_CACHE_USED = DIR_FILE / DIR_CACHE / "used.csv"
PATH_CACHE_BAD = DIR_FILE / DIR_CACHE / "bad.csv"

PATH_CONFIG_SUBREDDIT = DIR_FILE / "subreddits.txt"

PATH_FONTS_IMPACT = DIR_FILE / DIR_CONFIG / DIR_FONTS / \
                     "Anton" / "Anton-Regular.ttf"
PATH_FONTS_TWITTER = DIR_FILE / DIR_CONFIG / DIR_FONTS / \
                     "Arimo" / "Arimo-Regular.ttf"

PATH_LOGS_RUN_DISCORD = DIR_FILE / DIR_LOGS / "run_discord.log"
PATH_LOGS_DISCORD = DIR_FILE / DIR_LOGS / "discord.log"
PATH_LOGS_CACHE = DIR_FILE / DIR_LOGS / "cache.log"
PATH_LOGS_MEME = DIR_FILE / DIR_LOGS / "meme.log"
PATH_LOGS_SUBREDDITS = DIR_FILE / DIR_LOGS / "subreddits.log"

# commands
SYM_M = "-M"
SYM_T = "-T"
SYM_IT = "-IT"
SYM_IB = "-IB"
SYM_URL = "-URL"
SYM_CHECK = [SYM_T, SYM_IT, SYM_IB, SYM_URL]

# cache
UPDATE_WAIT_SECONDS_INIT = 10
UPDATE_WAIT_SECONDS = 60 * 10

# meme
IMAGE_WIDTH_MIN = 200
IMAGE_WIDTH_FORCE = 500

FONT_IMPACT = ImageFont.truetype(PATH_FONTS_IMPACT, 40)
FONT_TWITTER = ImageFont.truetype(PATH_FONTS_TWITTER, 36)

# logger
logger_run_discord = init_log("run_discord", PATH_LOGS_RUN_DISCORD)
logger_discord = init_log("discord", PATH_LOGS_DISCORD)
logger_cache = init_log("cache", PATH_LOGS_CACHE)
logger_meme = init_log("meme", PATH_LOGS_MEME)
logger_subreddits = init_log("subreddits", PATH_LOGS_SUBREDDITS)

# discord
client = discord.Client()


def parse_message_content(content, sym_start, sym_check):
    cs = content.split(' ')
    csu = content.upper().split()
    sym_all = [sym_start] + sym_check
    positions = [(index_or_default(csu, sym), sym) for sym in sym_all]

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


def extract_image(message, commands):
    # Attachment
    if len(message.attachments) > 0:
        print_info(logger_run_discord, "{}: attachment {}"
                   .format(message.author, message.attachments[0].url))

        return download_image(
            image_url=message.attachments[0].url,
            min_width=IMAGE_WIDTH_MIN,
            force_width=IMAGE_WIDTH_FORCE)

    # Custom URL
    elif SYM_URL in commands and len(commands[SYM_URL]) > 0:
        print_info(logger_run_discord, "{}: custom url {}"
                   .format(message.author, commands[SYM_URL][0]))

        return download_image(
            image_url=commands[SYM_URL][0],
            min_width=IMAGE_WIDTH_MIN,
            force_width=IMAGE_WIDTH_FORCE)

    # Random Image
    else:
        print_info(logger_run_discord, "{}: random image".format(message.author))

        return download_random_image(
            cache=cache,
            min_width=IMAGE_WIDTH_MIN,
            force_width=IMAGE_WIDTH_FORCE,
            attempts=3)


@client.event
async def on_ready():
    print_info(logger_run_discord, "Logged in as {}".format(client.user))


@client.event
async def on_message(message):
    if message.author == client.user:
        return

    commands = parse_message_content(message.content, SYM_M, SYM_CHECK)

    if commands is not None:
        try:
            image, image_fname = extract_image(message, commands)

        except InvalidImageURLException:
            await message.channel.send(
                "{} The image provided is invalid. "
                "It must be a JPEG or PNG image."
                .format(message.author.mention)
            )
            return

        except ImageDownloadException:
            await message.channel.send(
                "{} Unable to download the image provided."
                .format(message.author.mention)
            )
            return

        except ImageLoadException:
            await message.channel.send(
                "{} Unable to open the image provided."
                .format(message.author.mention)
            )
            return

        except ImageTooSmallException:
            await message.channel.send(
                "{} The image provided is too small. "
                "Images must have a width of at least {}px."
                .format(message.author.mention, IMAGE_WIDTH_MIN)
            )
            return

        except RandomCacheDownloadException:
            await message.channel.send(
                "{} Failed to download random image. "
                "Please try again."
                .format(message.author.mention)
            )
            return

        except Exception:
            await message.channel.send(
                "{} An unknown problem occurred. "
                "Please try again."
                .format(message.author.mention)
            )
            return

        finally:
            await message.delete()

        # impact format
        if SYM_IT in commands:
            image = apply_format_impact(image, commands[SYM_IT], True)

        if SYM_IB in commands:
            image = apply_format_impact(image, commands[SYM_IB], False)

        # twitter format
        if SYM_T in commands:
            image = apply_format_twitter(image, commands[SYM_T])

        # todo demotivational format

        # send to discord
        with BytesIO() as image_binary:
            image_format = image_fname[image_fname.rfind('.') + 1:]
            image.save(image_binary, image_format)
            image_binary.seek(0)

            await message.channel.send(
                message.author.mention,
                file=discord.File(
                    fp=image_binary,
                    filename='{}_{}'.format(time_ns(), image_fname)
                )
            )

        update_cache_reddit(cache, subreddits, wait_sec=UPDATE_WAIT_SECONDS)


# todo remove

print(PATH_LOGS_RUN_DISCORD)
print(PATH_LOGS_DISCORD)

exit(0)
# todo remove

print_info(logger_run_discord, "Init subreddits")
subreddits = init_subreddits(
    logger=logger_subreddits,
    path_subreddits=PATH_CONFIG_SUBREDDIT)

print_info(logger_run_discord, "Init cache")
cache = init_cache()

print_info(logger_run_discord, "Updating cache")
update_cache_reddit(cache, subreddits)

# ensure unused cache is not empty before starting
while len(cache[UNUSED]) == 0:
    print_info(logger_run_discord,
               "Cache update failed. "
               "Reattempting in {} second(s)..."
               .format(UPDATE_WAIT_SECONDS_INIT))
    sleep(UPDATE_WAIT_SECONDS_INIT)
    update_cache_reddit(cache, subreddits)

print_info(logger_run_discord, "Starting bot")
client.run(args.token)
