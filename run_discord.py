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

PATH_CONFIG_SUBREDDIT = DIR_FILE / DIR_CONFIG / "subreddits.txt"

PATH_FONTS_IMPACT = DIR_FILE / DIR_CONFIG / DIR_FONTS / \
                     "Anton" / "Anton-Regular.ttf"
PATH_FONTS_TWITTER = DIR_FILE / DIR_CONFIG / DIR_FONTS / \
                     "Arimo" / "Arimo-Regular.ttf"
PATH_FONTS_DEMOTIVATIONAL_TITLE = DIR_FILE / DIR_CONFIG / DIR_FONTS / \
                     "Jomolhari" / "Jomolhari-Regular.ttf"
PATH_FONTS_DEMOTIVATIONAL_SUBTITLE = DIR_FILE / DIR_CONFIG / DIR_FONTS / \
                     "OpenSans" / "OpenSans-SemiBold.ttf"

PATH_LOGS_RUN_DISCORD = DIR_FILE / DIR_LOGS / "run_discord.log"
PATH_LOGS_DISCORD = DIR_FILE / DIR_LOGS / "discord.log"
PATH_LOGS_CACHE = DIR_FILE / DIR_LOGS / "cache.log"
PATH_LOGS_MEME = DIR_FILE / DIR_LOGS / "meme.log"
PATH_LOGS_SUBREDDITS = DIR_FILE / DIR_LOGS / "subreddits.log"

# commands
SYM_M = "-M"

# formats
SYM_IT = "-IT"
SYM_IB = "-IB"
SYM_T = "-T"
SYM_DT = "-DT"
SYM_DS = "-DS"

# options
SYM_URL = "-URL"

# arguments
SYM_ARG_ANON = "ANON"
SYM_ARG_PING = "PING"

# misc
SYM_M_LEN = len(SYM_M)
SYM_CHECK = [SYM_IT, SYM_IB, SYM_T, SYM_DT, SYM_DS, SYM_URL]

# cache
UPDATE_WAIT_SECONDS_INIT = 10
UPDATE_WAIT_SECONDS = 60 * 1
MAX_RANDOM_DOWNLOAD_ATTEMPTS = 3
CACHE_SIZE_LIMIT = 1000

# meme
IMAGE_WIDTH_MIN = 200
IMAGE_WIDTH_FORCE = 500

FONT_IMPACT_SIZE = 40
FONT_TWITTER_SIZE = 36
FONT_DEMOTIVATIONAL_TITLE_SIZE = 49
FONT_DEMOTIVATIONAL_SUBTITLE_SIZE = 21

# logger
logger_run_discord = init_log("run_discord", PATH_LOGS_RUN_DISCORD)
logger_discord = init_log("discord", PATH_LOGS_DISCORD)
logger_cache = init_log("cache", PATH_LOGS_CACHE)
logger_meme = init_log("meme", PATH_LOGS_MEME)
logger_subreddits = init_log("subreddits", PATH_LOGS_SUBREDDITS)

# discord
client = discord.Client()


def parse_message(message, sym_start, sym_check):
    content = message.content \
        .replace('\n', ' ') \
        .replace('\t', ' ') \
        .strip()

    if len(content) < SYM_M_LEN or content[:SYM_M_LEN].upper() != SYM_M:
        return None  # not a message for the bot

    content = ' '.join(content.split())

    cs = content.split(' ')
    csu = content.upper().split()
    sym_all = [sym_start] + sym_check
    positions = [(index_or_default(csu, sym), sym) for sym in sym_all]

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

        commands[cmd] = [
            cs[i] if cmd != sym_start else csu[i]
            for i in range(pos + 1, next_pos)
        ]

    return commands


def extract_image(message, commands):
    # Attachment
    if len(message.attachments) > 0:
        print_info(logger_run_discord, "Attachment")

        return cache.download_image(
            image_url=message.attachments[0].url,
            min_width=IMAGE_WIDTH_MIN,
            force_width=IMAGE_WIDTH_FORCE)

    # Reply Attachment
    elif message.reference is not None and \
            message.reference.resolved is not None and \
            len(message.reference.resolved.attachments) > 0:
        print_info(logger_run_discord, "Reply Attachment")

        return cache.download_image(
            image_url=message.reference.resolved.attachments[0].url,
            min_width=IMAGE_WIDTH_MIN,
            force_width=IMAGE_WIDTH_FORCE)

    # Custom URL
    elif SYM_URL in commands and len(commands[SYM_URL]) > 0:
        print_info(logger_run_discord, "Custom URL")

        return cache.download_image(
            image_url=commands[SYM_URL][0],
            min_width=IMAGE_WIDTH_MIN,
            force_width=IMAGE_WIDTH_FORCE)

    # Random Image
    else:
        print_info(logger_run_discord, "Random Image")

        return cache.download_random_image(
            min_width=IMAGE_WIDTH_MIN,
            force_width=IMAGE_WIDTH_FORCE,
            attempts=MAX_RANDOM_DOWNLOAD_ATTEMPTS)


@client.event
async def on_ready():
    print_info(logger_run_discord, "Logged in as {}".format(client.user))


@client.event
async def on_message(message):
    if message.author == client.user:
        return

    commands = parse_message(message, SYM_M, SYM_CHECK)

    if commands is not None:
        image = None
        image_fname = None
        error_message = None
        anonymous = SYM_ARG_ANON in commands[SYM_M]
        text_anonymous = "" if anonymous else (message.author.mention + " ")

        try:
            if SYM_ARG_PING in commands[SYM_M]:
                await message.channel.send(text_anonymous + "Pong.")

            else:
                image, image_fname = extract_image(message, commands)

            await message.delete()

        except InvalidImageURLException:
            error_message = \
                text_anonymous + \
                "The image provided is of an invalid image type." \
                .format(message.author.mention)

        except ImageDownloadException:
            error_message = \
                text_anonymous + \
                "Unable to download the image provided." \
                .format(message.author.mention)

        except ImageLoadException:
            error_message = \
                text_anonymous + \
                "Unable to open the image provided." \
                .format(message.author.mention)

        except ImageTooSmallException:
            error_message = \
                text_anonymous + \
                "The image provided is too small. " \
                "Images must have a width of at least {}px." \
                .format(message.author.mention, IMAGE_WIDTH_MIN)

        except RandomCacheDownloadException:
            error_message = \
                text_anonymous + \
                "Failed to download random image. " \
                "Please try again." \
                .format(message.author.mention)

        except Exception:
            error_message = \
                text_anonymous + \
                "An unknown problem occurred. " \
                "Please try again." \
                .format(message.author.mention)

        finally:
            if error_message is not None:
                await message.channel.send(error_message)
                return

        if image is not None and image_fname is not None:
            # impact format
            if SYM_IT in commands:
                image = format_impact.apply_format(
                    image, commands[SYM_IT], ImpactFormat.POSITION_TOP)

            if SYM_IB in commands:
                image = format_impact.apply_format(
                    image, commands[SYM_IB], ImpactFormat.POSITION_BOTTOM)

            # twitter format
            if SYM_T in commands:
                image = format_twitter.apply_format(image, commands[SYM_T])

            # demotivational format
            if SYM_DT in commands or SYM_DS in commands:
                image = format_demotivational.apply_format(
                    image,
                    commands[SYM_DT] if SYM_DT in commands else None,
                    commands[SYM_DS] if SYM_DS in commands else None)

            # send to discord
            with BytesIO() as image_binary:
                image_format = image_fname[image_fname.rfind('.') + 1:]
                image.save(image_binary, image_format)
                image_binary.seek(0)

                await message.channel.send(
                    text_anonymous,
                    file=discord.File(
                        fp=image_binary,
                        filename='{}_{}'.format(
                            time_ns(), image_fname.lower())
                    )
                )

            cache.update_cache(subreddits, wait_sec=UPDATE_WAIT_SECONDS)


print_info(logger_run_discord, "Init subreddits")

subreddits = init_subreddits(
    logger=logger_subreddits,
    path_subreddits=PATH_CONFIG_SUBREDDIT)


print_info(logger_run_discord, "Init meme formats")

format_impact = ImpactFormat(
    logger=logger_meme,
    font_path=str(PATH_FONTS_IMPACT),
    font_size=FONT_IMPACT_SIZE)

format_twitter = TwitterFormat(
    logger=logger_meme,
    font_path=str(PATH_FONTS_TWITTER),
    font_size=FONT_TWITTER_SIZE)

format_demotivational = DemotivationalFormat(
    logger=logger_meme,
    font_title_path=str(PATH_FONTS_DEMOTIVATIONAL_TITLE),
    font_title_size=FONT_DEMOTIVATIONAL_TITLE_SIZE,
    font_subtitle_path=str(PATH_FONTS_DEMOTIVATIONAL_SUBTITLE),
    font_subtitle_size=FONT_DEMOTIVATIONAL_SUBTITLE_SIZE,
)


print_info(logger_run_discord, "Init cache")

cache = RedditCache(
    logger=logger_cache,
    path_unused=PATH_CACHE_UNUSED,
    path_used=PATH_CACHE_USED,
    path_bad=PATH_CACHE_BAD,
    cache_size_limit=CACHE_SIZE_LIMIT
)

if len(cache.unused) == 0:
    print_info(logger_run_discord, "Updating empty cache")
    cache.update_cache(subreddits)

    while len(cache.unused) == 0:
        print_info(logger_run_discord,
                   "Cache update failed. "
                   "Reattempting in {} second(s)..."
                   .format(UPDATE_WAIT_SECONDS_INIT))
        sleep(UPDATE_WAIT_SECONDS_INIT)
        cache.update_cache(subreddits)

else:
    print_info(logger_run_discord, "Updating cache")
    cache.update_cache(subreddits)


print_info(logger_run_discord, "Starting bot")

client.run(args.token)
