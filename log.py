import logging
from tools import *


def init_log(name_log, path_log):
    logger = logging.getLogger(name_log)
    logger.setLevel(logging.DEBUG)
    file_touch(path_log)

    handler = logging.FileHandler(
        filename=path_log, encoding='utf-8', mode='w')

    handler.setFormatter(logging.Formatter(
        '%(asctime)s:%(levelname)s:%(name)s: %(message)s'))

    logger.addHandler(handler)
    return logger
