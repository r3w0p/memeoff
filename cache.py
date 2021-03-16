import requests
import csv
from time import time_ns
from math import floor
from random import shuffle, choice
from slugify import slugify
from PIL import Image
from log import *


PATH_CACHE_CSV_USED = "./cache/used.csv"
PATH_CACHE_CSV_UNUSED = "./cache/unused.csv"
PATH_CACHE_CSV_BAD = "./cache/bad.csv"
URL_REDDIT = "https://www.reddit.com/r/{}.json"

USED = "used"
UNUSED = "unused"
BAD = "bad"

DATA = "data"
URL = "url"
CHILDREN = "children"

JPG = "JPG"
JPEG = "JPEG"
PNG = "PNG"
VALID_FORMATS = (JPG, JPEG, PNG)

RETRY_AFTER = "Retry-After"
STATUS_TOO_MANY_REQUESTS = 429
STATUS_OK = 200

# logger
LOG_CACHE_NAME = "cache"
LOG_CACHE_PATH = "./logs/cache.log"
logger_cache = init_log(LOG_CACHE_NAME, LOG_CACHE_PATH)

cache_last_update = 0


class ImageTooSmallException(Exception):
    """When the image does not meet the minimum dimensions."""


class InvalidImageURLException(Exception):
    """When an image URL is invalid."""


class RandomCacheDownloadException(Exception):
    """When a random image failed to download from the cache."""


class ImageDownloadException(Exception):
    """When an image failed to download."""


class ImageLoadException(Exception):
    """When an image failed to load."""


def init_cache() -> dict:
    file_touch(PATH_CACHE_CSV_USED)
    file_touch(PATH_CACHE_CSV_UNUSED)
    file_touch(PATH_CACHE_CSV_BAD)

    cache = _read_cache()

    return cache


def update_cache_reddit(
        cache,
        subreddits,
        wait_sec=-1,
        shuffle_first=True,
        stop_first_failure=False):
    global cache_last_update

    # not enough time has passed since the last cache update
    if (time_ns() - cache_last_update) / 1e+9 < wait_sec:
        logger_cache.info(
            "Wait period for cache update has not elapsed. "
            "Ignoring update request.")
        return

    cache_last_update = time_ns()

    # shuffle the subreddit list beforehand
    if shuffle_first:
        shuffle(subreddits)

    for subreddit in subreddits:
        status_code, list_urls = _scrape_subreddit_image_urls(subreddit)

        logger_cache.info(
            "Scraped from subreddit {} (status code {})"
            .format(subreddit, status_code))

        if status_code == STATUS_OK:
            timestamp = time_ns()

            for image_url in list_urls:
                # ignore if bad url
                if image_url in cache[BAD]:
                    continue

                # ignore if already used
                if image_url in cache[USED]:
                    continue

                # store timestamp of download with url
                cache[UNUSED][image_url] = timestamp

        elif stop_first_failure:
            break

    _write_cache(cache)
    _log_cache(cache)


def download_random_image(cache, min_width=0, force_width=0, attempts=1):
    if len(cache[UNUSED]) > 0:
        # select from unused cache, if any
        cache_key = UNUSED
    elif len(cache[USED]) > 0:
        # select from used cache, if unused is empty
        cache_key = USED
    else:
        # caches are empty
        raise RandomCacheDownloadException()

    image = None
    image_fname = None
    attempt = 0
    attempts = max(1, attempts)

    while (image is None and image_fname is None) and attempt < attempts:
        attempt += 1
        random_image_url = choice(list(cache[cache_key].keys()))

        try:
            image, image_fname = download_image(
                random_image_url, min_width, force_width)

        except Exception as e:
            logger_cache.info(
                "Exception for random image download {} (attempt {}/{}): {}"
                .format(random_image_url, attempt, attempts, e))

            # unsuccessful image url is moved to bad cache
            cache[cache_key].pop(random_image_url, None)
            cache[BAD][random_image_url] = time_ns()

        # successful image url is moved to used cache if from unused cache
        if cache_key == UNUSED:
            cache[UNUSED].pop(random_image_url, None)
            cache[USED][random_image_url] = time_ns()

    if image is None or image_fname is None:
        raise RandomCacheDownloadException()

    return image, image_fname


def validate_image_url(url) -> bool:
    # todo complete implementation
    url_dot = url.rfind('.')

    if url_dot == -1:
        return False

    url_end = url[url_dot:].strip().upper()
    return len(url_end) > 1 and url_end[1:] in VALID_FORMATS


def slugify_image_url(url_str) -> str:
    url_cleaned = url_str.strip().upper()
    last_dot = url_cleaned.rfind('.')

    file_name = slugify(url_cleaned[:last_dot])
    file_format = url_cleaned[last_dot + 1:]

    # PIL uses 'JPEG' and not 'JPG', change accordingly
    if file_format == JPG:
        file_format = JPEG

    return "{0}.{1}".format(
        file_name,
        file_format
    )


def download_image(image_url, min_width=0, force_width=0):
    if not validate_image_url(image_url):
        raise InvalidImageURLException()

    try:
        logger_cache.info("Downloading image: {}".format(image_url))
        image_response = requests.get(image_url, stream=True).raw

    except Exception as e:  # todo catch more specific exceptions
        logger_cache.info(
            "Exception when downloading image {}: {}"
            .format(image_url, e))

        raise ImageDownloadException()

    try:
        logger_cache.info("Opening downloaded image: {}".format(image_url))
        image = Image.open(image_response)

    except Exception as e:  # todo catch more specific exceptions
        logger_cache.info(
            "Exception when opening downloaded image {}: {}"
            .format(image_url, e))

        raise ImageLoadException()

    # check whether image is too small
    if min_width > 0 and image.size[0] < min_width:
        raise ImageTooSmallException()

    # check whether image meets the enforced width, and resize if not
    if force_width > 0:
        if image.size[0] > force_width:
            reduction = (image.size[0] - force_width) / image.size[0]
            height_reduced = floor(image.size[1] * (1 - reduction))

            image = image.resize((force_width, height_reduced))

        elif image.size[0] < force_width:
            increase = force_width / image.size[0]
            height_increased = floor(image.size[1] * increase)

            image = image.resize((force_width, height_increased))

    return image, slugify_image_url(image_url)


def _scrape_subreddit_image_urls(subreddit) -> (int, list):
    list_image_urls = []

    resp = requests.get(URL_REDDIT.format(subreddit))

    if resp.status_code == STATUS_OK:
        resp_json = resp.json()

        for url in [sub[DATA][URL] for sub in resp_json[DATA][CHILDREN]]:
            if validate_image_url(url):
                list_image_urls.append(url)

    return resp.status_code, list_image_urls


def _read_cache_file(path_file, delimiter=',') -> dict:
    d = {}
    with open(path_file, 'r') as csv_file:
        for row in csv.reader(csv_file, delimiter=delimiter):
            # if url has already appeared
            if row[0] in d:
                # save latest timestamp
                if row[1] > d[row[0]]:
                    d[row[0]] = row[1]
            else:
                d[row[0]] = row[1]
    return d


def _read_cache() -> dict:
    cache = {
        USED: _read_cache_file(PATH_CACHE_CSV_USED),
        UNUSED: _read_cache_file(PATH_CACHE_CSV_UNUSED),
        BAD: _read_cache_file(PATH_CACHE_CSV_BAD)
    }

    _log_cache(cache)

    return cache


def _write_cache_file(cache, cache_key, path_file, delimiter=',') -> None:
    with open(path_file, mode='w') as csv_file:
        writer = csv.writer(csv_file, delimiter=delimiter)

        for url, timestamp in cache[cache_key].items():
            writer.writerow([url, timestamp])


def _write_cache(cache) -> None:
    _write_cache_file(cache, USED, PATH_CACHE_CSV_USED)
    _write_cache_file(cache, UNUSED, PATH_CACHE_CSV_UNUSED)
    _write_cache_file(cache, BAD, PATH_CACHE_CSV_BAD)


def _log_cache(cache):
    logger_cache.info("Current cache: used={}, unused={}, bad={}".format(
        len(cache[USED]),
        len(cache[UNUSED]),
        len(cache[BAD])
    ))
