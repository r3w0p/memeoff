import requests
import csv
from time import time_ns
from math import floor
from random import shuffle, choice
from slugify import slugify
from PIL import Image
from tools import *


PATH_CACHE_CSV_USED = "./cache/csv/used.csv"
PATH_CACHE_CSV_UNUSED = "./cache/csv/unused.csv"
PATH_CACHE_CSV_BAD = "./cache/csv/bad.csv"
PATH_CACHE_IMG = "./cache/img"
URL_REDDIT = "https://www.reddit.com/r/{}.json"

USED = "used"
UNUSED = "unused"
BAD = "bad"

DATA = "data"
URL = "url"
CHILDREN = "children"

DOT_JPG = ".jpg"
DOT_PNG = ".png"

RETRY_AFTER = "Retry-After"
STATUS_TOO_MANY_REQUESTS = 429
STATUS_OK = 200

UPDATE_WAIT_SECONDS = 60 * 5
cache_last_update = 0


def init_cache() -> dict:
    file_touch(PATH_CACHE_CSV_USED)
    file_touch(PATH_CACHE_CSV_UNUSED)
    file_touch(PATH_CACHE_CSV_BAD)
    dir_touch(PATH_CACHE_IMG)

    cache = _read_cache()

    return cache


def update_cache_reddit(
        cache,
        subreddits,
        shuffle_first=True,
        stop_first_success=True):

    if (time_ns() - cache_last_update) / 1e+9 < UPDATE_WAIT_SECONDS:
        return

    if shuffle_first:
        shuffle(subreddits)

    timestamp = time_ns()

    for subreddit in subreddits:
        status_code, list_urls = _scrape_subreddit_image_urls(subreddit)
        print("scraping: {} (status: {})".format(
            subreddit, status_code))

        if status_code == STATUS_OK:
            for image_url in list_urls:
                cache[UNUSED][image_url] = timestamp

            _write_cache_file(cache, UNUSED, PATH_CACHE_CSV_UNUSED)

            if stop_first_success:
                break

    _print_cache(cache)


def file_name_from_url(url_str) -> str:
    url_cleaned = url_str.strip().lower()
    return "{0}.{1}".format(
        slugify(url_cleaned[:-3]),
        url_cleaned[-3:]
    )


def download_random_image(cache, force_width, key=UNUSED, save=True):
    random_image_url = choice(list(cache[key].keys()))
    return download_image(random_image_url, force_width)


def download_image(image_url, force_width):
    image_slug = file_name_from_url(image_url)
    path_save = "{}/{}".format(PATH_CACHE_IMG, image_slug)

    if not Path(path_save).is_file():
        try:
            print("Downloading image {}".format(image_url))
            image = Image.open(requests.get(image_url, headers = {'User-agent': str(time_ns())}, stream=True).raw)

            if image.size[0] > force_width:
                reduction = (image.size[0] - force_width) / image.size[0]
                height = floor(image.size[1] * (1 - reduction))

                image = image.resize((force_width, height))

            elif image.size[0] < force_width:
                return None  # image too small

            image.save(path_save)

        except Exception as e:  # todo catch more specific exceptions
            return None

    return path_save


def _scrape_subreddit_image_urls(subreddit) -> (int, list):
    list_image_urls = []

    resp = requests.get(URL_REDDIT.format(subreddit))

    if resp.status_code == STATUS_OK:
        resp_json = resp.json()

        for url in [sub[DATA][URL] for sub in resp_json[DATA][CHILDREN]]:
            if url.endswith(DOT_JPG) or url.endswith(DOT_PNG):
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

    _print_cache(cache)

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


def _print_cache(cache):
    print("cache: used={}, unused={}, bad={}".format(
        len(cache[USED]),
        len(cache[UNUSED]),
        len(cache[BAD])
    ))

