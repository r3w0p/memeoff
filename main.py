# Copyright (c) 2021-2025 r3w0p
# The following code can be redistributed and/or
# modified under the terms of the GPL-3.0 License.

import argparse
from src.client import get_client
from src.constants import EMOJI_STYLES_ALL, EMOJI_STYLE_APPLE

parser = argparse.ArgumentParser()
parser.add_argument("-e", "--emoji", type=str, default=EMOJI_STYLE_APPLE, help=f"Emoji style to use ({', '.join(EMOJI_STYLES_ALL)}).")
parser.add_argument("-g", "--guild", type=str, help="Discord guild ID for slash commands.")
parser.add_argument("-t", "--token", type=str, required=True, help="Discord token.")
parser.add_argument("--disable_anon", action="store_true", help="Disables anonymity on all messages.")
parser.add_argument("--force_anon", action="store_true", help="Forces anonymity on all messages.")
args = parser.parse_args()


if __name__ == "__main__":
    get_client(args).run(args.token)
