import discord
import argparse
from io import BytesIO
from time import sleep
from subreddits import *
from meme import *
from cache import *


# constants
SYM_M = "-M"
SYM_T = "-T"
SYM_IT = "-IT"
SYM_IB = "-IB"
SYM_URL = "-URL"
SYM_CHECK = [SYM_T, SYM_IT, SYM_IB, SYM_URL]

URL = "url"

IMAGE_WIDTH_MIN = 200
IMAGE_WIDTH_FORCE = 500
UPDATE_WAIT_SECONDS = 60 * 1

# logger
LOG_BOT_NAME = "bot"
LOG_BOT_PATH = "./logs/bot.log"
logger_bot = init_log(LOG_BOT_NAME, LOG_BOT_PATH)

LOG_DISCORD_NAME = "discord"
LOG_DISCORD_PATH = "./logs/discord.log"
logger_discord = init_log(LOG_DISCORD_NAME, LOG_DISCORD_PATH)

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


@client.event
async def on_ready():
    print_info(logger_bot, "Logged in as {}".format(client.user))


@client.event
async def on_message(message):
    if message.author == client.user:
        return

    commands = parse_message_content(message.content, SYM_M, SYM_CHECK)

    if commands is not None:
        if len(message.attachments) > 0:

            print_info(logger_bot, "{}: attachment {}"
                       .format(message.author, message.attachments[0].url))

            # if an attachment was passed, download it
            try:
                image, image_fname = download_image(
                    image_url=message.attachments[0].url,
                    min_width=IMAGE_WIDTH_MIN,
                    force_width=IMAGE_WIDTH_FORCE)

            except InvalidImageURLException:
                await message.channel.send(
                    "{} The attachment you provided was invalid. "
                    "It must be a JPEG or PNG image."
                    .format(message.author.mention)
                )
                return

            except ImageDownloadException:
                await message.channel.send(
                    "{} Unable to download the attached image."
                    .format(message.author.mention)
                )
                return

            except ImageLoadException:
                await message.channel.send(
                    "{} Unable to open the attached image."
                    .format(message.author.mention)
                )
                return

            except ImageTooSmallException:
                await message.channel.send(
                    "{} The attached image you provided was too small. "
                    "Images must have a width of at least {}px."
                    .format(message.author.mention, IMAGE_WIDTH_MIN)
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

        elif SYM_URL in commands and len(commands[SYM_URL]) > 0:
            await message.delete()

            print_info(logger_bot, "{}: custom url {}"
                       .format(message.author, commands[SYM_URL][0]))

            # if custom image url was passed, download it
            try:
                image, image_fname = download_image(
                    image_url=commands[SYM_URL][0],
                    min_width=IMAGE_WIDTH_MIN,
                    force_width=IMAGE_WIDTH_FORCE)

            except InvalidImageURLException:
                await message.channel.send(
                    "{} The image URL you provided was invalid. "
                    "URLs must be a direct link to a JPEG or PNG image."
                    .format(message.author.mention)
                )
                return

            except ImageDownloadException:
                await message.channel.send(
                    "{} Unable to download the image from the provided URL."
                    .format(message.author.mention)
                )
                return

            except ImageLoadException:
                await message.channel.send(
                    "{} Unable to open the image downloaded from the provided "
                    "URL."
                    .format(message.author.mention)
                )
                return

            except ImageTooSmallException:
                await message.channel.send(
                    "{} The image you provided was too small. "
                    "Images must have a width of at least {}px."
                    .format(message.author.mention, IMAGE_WIDTH_MIN)
                )
                return

            except Exception:
                await message.channel.send(
                    "{} An unknown problem occurred. "
                    "Please try again."
                    .format(message.author.mention)
                )
                return

        else:
            await message.delete()

            print_info(logger_bot, "{}: random image".format(message.author))

            # no custom image, download random image instead
            image, image_fname = download_random_image(
                cache=cache,
                min_width=IMAGE_WIDTH_MIN,
                force_width=IMAGE_WIDTH_FORCE,
                attempts=3,
                default_used=True)

            if image is None:
                await message.channel.send(
                    "{} A problem occurred when downloading an image. "
                    "Please try again."
                    .format(message.author.mention)
                )
                return

        # impact format
        if SYM_IT in commands:
            image = apply_format_impact(image, commands[SYM_IT], True)

        if SYM_IB in commands:
            image = apply_format_impact(image, commands[SYM_IB], False)

        # twitter format
        if SYM_T in commands:
            image = apply_format_twitter(image, commands[SYM_T])

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


print_info(logger_bot, "Init subreddits")
subreddits = init_subreddits()

print_info(logger_bot, "Init cache")
cache = init_cache()

print_info(logger_bot, "Updating cache")
update_cache_reddit(cache, subreddits)

# ensure unused cache is not empty before starting
while len(cache[UNUSED]) == 0:
    print_info(logger_bot,
               "Unused cache is empty. "
               "Reattempting cache update in {} second(s)..."
               .format(UPDATE_WAIT_SECONDS))
    sleep(UPDATE_WAIT_SECONDS)
    update_cache_reddit(cache, subreddits, wait_sec=UPDATE_WAIT_SECONDS)

print_info(logger_bot, "Starting bot")
client.run(args.token)
