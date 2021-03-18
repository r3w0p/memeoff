from src.tools import *


def init_subreddits(logger, path_subreddits) -> list:
    p = Path(path_subreddits)

    if not p.is_file():
        print_info(logger,
                   "Subreddit file does not exist at {}"
                   .format(path_subreddits))
        exit(1)

    if p.stat().st_size == 0:
        print_info(logger,
                   "Subreddit file is empty at {}"
                   .format(path_subreddits))
        exit(1)

    try:
        with open(path_subreddits) as f:
            subreddits = [line.rstrip() for line in f]

    except Exception as e:
        print_info(logger,
                   "Failed to retrieve subreddits from {}: {}"
                   .format(path_subreddits, e))
        exit(1)

    return subreddits
