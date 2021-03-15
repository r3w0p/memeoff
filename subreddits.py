from pathlib import Path


PATH_CONFIG_SUBREDDITS = "config/subreddits.txt"


def init_subreddits() -> list:
    p = Path(PATH_CONFIG_SUBREDDITS)

    if not p.is_file():
        print("Subreddit file does not exist at {}".format(
            PATH_CONFIG_SUBREDDITS))
        exit(1)

    if p.stat().st_size == 0:
        print("Subreddit file is empty at {}".format(
            PATH_CONFIG_SUBREDDITS))
        exit(1)

    with open(PATH_CONFIG_SUBREDDITS) as f:
        subreddits = [line.rstrip() for line in f]

    return subreddits
