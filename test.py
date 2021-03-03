import requests
import os
from random import choice, randrange, shuffle
from pprint import pprint

PATH_CONFIG_SUBREDDITS = "./config/subreddits.txt"
PATH_CACHE_USED = "./cache/used.txt"
PATH_CACHE_UNUSED = "./cache/unused.txt"
PATH_CACHE_BAD = "./cache/bad.txt"
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


def configure_subreddits() -> list:
    # todo subreddit file does not exist, exit

    # get subreddits
    with open(PATH_CONFIG_SUBREDDITS) as f:
        subreddits = [line.rstrip() for line in f]

    return subreddits


def configure_cache() -> dict:
    # todo cache files do not exist, create them

    cache = dict()

    # get cached urls
    with open(PATH_CACHE_USED, 'r') as fd:
        cache[USED] = set(fd.read().strip().splitlines())

    with open(PATH_CACHE_UNUSED, 'r') as fd:
        cache[UNUSED] = set(fd.read().strip().splitlines())

    with open(PATH_CACHE_BAD, 'r') as fd:
        cache[BAD] = set(fd.read().strip().splitlines())

    print_cache(cache)

    return cache


def print_cache(cache):
    print("cache: used={}, unused={}, bad={}".format(
        len(cache[USED]),
        len(cache[UNUSED]),
        len(cache[BAD])
    ))


def write_cache_used(cache) -> None:
    with open(PATH_CACHE_USED, 'w') as fd:
        fd.write("\n".join(url for url in cache[USED]))


def write_cache_unused(cache) -> None:
    with open(PATH_CACHE_UNUSED, 'w') as fd:
        fd.write("\n".join(url for url in cache[UNUSED]))


def write_cache_bad(cache) -> None:
    with open(PATH_CACHE_BAD, 'w') as fd:
        fd.write("\n".join(url for url in cache[BAD]))


def write_cache(cache) -> None:
    write_cache_used(cache)
    write_cache_unused(cache)
    write_cache_bad(cache)


def scrape_subreddit_image_urls(subreddit) -> (int, list):
    list_image_urls = []

    resp = requests.get(URL_REDDIT.format(subreddit))

    if resp.status_code == STATUS_OK:
        resp_json = resp.json()

        for url in [sub[DATA][URL] for sub in resp_json[DATA][CHILDREN]]:
            if url.endswith(DOT_JPG) or url.endswith(DOT_PNG):
                list_image_urls.append(url)

    return resp.status_code, list_image_urls


def update_cache_reddit(cache, subreddits, shuffle_first=True):
    if shuffle_first:
        shuffle(subreddits)

    for subreddit in subreddits:
        status_code, list_urls = scrape_subreddit_image_urls(subreddit)
        print("scraping: subreddit={} (status: {})".format(
            subreddit, status_code))

        for image_url in list_urls:
            cache[UNUSED].add(image_url)

        write_cache_unused(cache)

    print_cache(cache)


def main():
    subreddits = configure_subreddits()
    cache = configure_cache()

    update_cache_reddit(cache, subreddits)


if __name__ == "__main__":
    main()
