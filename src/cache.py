import requests
import csv
from time import time_ns
from math import floor
from random import shuffle, choice, sample
from slugify import slugify
from PIL import Image
from src.log import *
from pprint import pprint


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


class RedditCache:
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

    def __init__(
            self,
            logger,
            path_unused,
            path_used,
            path_bad,
            cache_size_limit) -> None:
        super().__init__()

        self.logger = logger
        self.path_unused = path_unused
        self.path_used = path_used
        self.path_bad = path_bad
        self.cache_size_limit = cache_size_limit

        self._read_cache()

        self.cache_last_update = 0

    def update_cache(
            self,
            subreddits,
            wait_sec=-1,
            shuffle_first=True,
            stop_first_failure=False,
            cull=True,
            write=True,
            log=True):

        # not enough time has passed since the last cache update
        if (time_ns() - self.cache_last_update) / 1e+9 < wait_sec:
            print_info(
                self.logger,
                "Wait period for cache update has not elapsed. "
                "Ignoring update request.")
            return

        self.cache_last_update = time_ns()

        # shuffle the subreddit list beforehand
        if shuffle_first:
            shuffle(subreddits)

        for subreddit in subreddits:
            status_code, list_urls = \
                self._scrape_subreddit_image_urls(subreddit)

            print_info(
                self.logger,
                "Subreddit {}: {} (status={})"
                .format(subreddit,
                        "SUCCESS" if status_code == RedditCache.STATUS_OK
                        else "FAILURE",
                        status_code))

            if status_code == RedditCache.STATUS_OK:
                timestamp = time_ns()

                for image_url in list_urls:
                    # ignore if bad url
                    if image_url in self.bad:
                        continue

                    # ignore if already used
                    if image_url in self.used:
                        continue

                    # store timestamp of download with url
                    self.unused[image_url] = timestamp

            elif stop_first_failure:
                break

        if cull:
            for cache in [self.unused, self.used, self.bad]:
                cache_keys = cache.keys()
                cache_keys_len = len(cache_keys)

                if cache_keys_len > self.cache_size_limit:
                    keys_cull = sample(
                        cache_keys,
                        cache_keys_len - self.cache_size_limit)

                    for key in keys_cull:
                        cache.pop(key, None)

        if write:
            self._write_cache()

        if log:
            self.print_info_cache()

    def download_random_image(
            self,
            min_width=0,
            force_width=0,
            attempts=1):

        if len(self.unused) > 0:
            # select from unused cache, if any
            cache_download = self.unused
        elif len(self.used) > 0:
            # select from used cache, if unused is empty
            cache_download = self.used
        else:
            # caches are empty
            raise RandomCacheDownloadException()

        image = None
        image_fname = None
        attempt = 0
        attempts = max(1, attempts)

        while (image is None and image_fname is None) and attempt < attempts:
            attempt += 1
            random_image_url = choice(list(cache_download.keys()))

            try:
                image, image_fname = self.download_image(
                    random_image_url, min_width, force_width)

            except Exception as e:
                print_info(
                    self.logger,
                    "Random image download failed (attempt {}/{}): {}, {}"
                    .format(attempt, attempts, random_image_url, e))

                # unsuccessful image url is moved to bad cache
                cache_download.pop(random_image_url, None)
                self.bad[random_image_url] = time_ns()

            # successful image url is moved to used cache if from unused cache
            if cache_download == self.unused:
                self.unused.pop(random_image_url, None)
                self.used[random_image_url] = time_ns()

        if image is None or image_fname is None:
            raise RandomCacheDownloadException()

        return image, image_fname

    def download_image(self, image_url, min_width=0, force_width=0):
        if not self.validate_image_url(image_url):
            raise InvalidImageURLException()

        try:
            image_response = requests.get(image_url, stream=True).raw

        except Exception as e:
            print_info(
                self.logger,
                "Exception when downloading image {}: {}"
                .format(image_url, e))

            raise ImageDownloadException()

        try:
            image = Image.open(image_response)

        except Exception as e:
            print_info(
                self.logger,
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

        return image, self.slugify_image_url(image_url)

    @staticmethod
    def _scrape_subreddit_image_urls(subreddit) -> (int, list):
        list_image_urls = []

        resp = requests.get(RedditCache.URL_REDDIT.format(subreddit))

        if resp.status_code == RedditCache.STATUS_OK:
            resp_json = resp.json()

            for url in [sub[RedditCache.DATA][RedditCache.URL]
                        for sub in
                        resp_json[RedditCache.DATA][RedditCache.CHILDREN]]:
                if RedditCache.validate_image_url(url):
                    list_image_urls.append(url)

        return resp.status_code, list_image_urls

    @staticmethod
    def validate_image_url(url) -> bool:
        # todo complete implementation
        url_dot = url.rfind('.')

        if url_dot == -1:
            return False

        url_end = url[url_dot:].strip().upper()
        return len(url_end) > 1 and url_end[1:] in RedditCache.VALID_FORMATS

    @staticmethod
    def slugify_image_url(url_str) -> str:
        url_cleaned = url_str.strip().upper()
        last_dot = url_cleaned.rfind('.')

        file_name = slugify(url_cleaned[:last_dot])
        file_format = url_cleaned[last_dot + 1:]

        # PIL uses 'JPEG' and not 'JPG', change accordingly
        if file_format == RedditCache.JPG:
            file_format = RedditCache.JPEG

        return "{0}.{1}".format(
            file_name,
            file_format
        )

    def _read_cache(self) -> None:
        self.unused = RedditCache._read_cache_file(self.path_unused)
        self.used = RedditCache._read_cache_file(self.path_used)
        self.bad = RedditCache._read_cache_file(self.path_bad)

    def _write_cache(self) -> None:
        RedditCache._write_cache_file(self.unused, self.path_unused)
        RedditCache._write_cache_file(self.used, self.path_used)
        RedditCache._write_cache_file(self.bad, self.path_bad)

    @staticmethod
    def _read_cache_file(path_file, delimiter=',') -> dict:
        file_touch(path_file)

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

    @staticmethod
    def _write_cache_file(cache, path_cache, delimiter=',') -> None:
        file_touch(path_cache)

        with open(path_cache, mode='w', newline='') as csv_file:
            writer = csv.writer(csv_file, delimiter=delimiter)

            for url, timestamp in cache.items():
                writer.writerow([url, timestamp])

    def print_info_cache(self):
        print_info(
            self.logger,
            "Cache: unused={}, used={}, bad={}".format(
                len(self.unused),
                len(self.used),
                len(self.bad))
        )
