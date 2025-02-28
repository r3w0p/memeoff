# Copyright (c) 2021-2025 r3w0p
# The following code can be redistributed and/or
# modified under the terms of the GPL-3.0 License.

from pathlib import Path
from typing import List

MEMEOFF_VERSION: str = "1.0.0"
MEMEOFF_URL_WIKI: str = "https://github.com/r3w0p/memeoff/wiki"

NAME_MEMEOFF: str = "memeoff"
NAME_DEMOTIV: str = "demotiv"
NAME_GIFCAP: str = "gifcap"
NAME_IMPACT: str = "impact"
NAME_TWITTER: str = "twitter"
NAME_WHISPER: str = "whisper"
NAME_ANON: str = "anon"
NAME_DARK: str = "dark"

NAME_TITLE: str = "title"
NAME_SUBTITLE: str = "subtitle"

COMMAND_DEMOTIV: str = f"/{NAME_DEMOTIV}"
COMMAND_GIFCAP: str = f"/{NAME_GIFCAP}"
COMMAND_IMPACT: str = f"/{NAME_IMPACT}"
COMMAND_TWITTER: str = f"/{NAME_TWITTER}"
COMMAND_WHISPER: str = f"/{NAME_WHISPER}"
COMMAND_ANON: str = f"/{NAME_ANON}"
COMMAND_DARK: str = f"/{NAME_DARK}"

COMMANDS_FORMATS: List[str] = [
    COMMAND_DEMOTIV,
    COMMAND_GIFCAP,
    COMMAND_IMPACT,
    COMMAND_TWITTER,
    COMMAND_WHISPER
]

COMMANDS_OPTIONS: List[str] = [
    COMMAND_ANON,
    COMMAND_DARK
]

COMMANDS_ALL: List[str] = COMMANDS_FORMATS + COMMANDS_OPTIONS

REGEX_PATTERN_SLASH: str = '|'.join([f"({c})" for c in COMMANDS_ALL])

DELIM_SPOILER: str = "||"
DELIM_NEWLINE: str = "##"
DELIM_CONTEXT: str = "//"

DIR_CONFIG: str = "config"
DIR_FONTS: str = "fonts"
DIR_TITLE: str = "title"
DIR_SUBTITLE: str = "subtitle"

IMAGE_WIDTH_MIN: int = 200
IMAGE_WIDTH_FORCE: int = 500

FILE_TYPE_JPG: str = "JPG"
FILE_TYPE_JPEG: str = "JPEG"
FILE_TYPE_PNG: str = "PNG"
FILE_TYPE_WEBP: str = "WEBP"

SUPPORTED_FILE_TYPES: List[str] = [
    FILE_TYPE_JPG,
    FILE_TYPE_JPEG,
    FILE_TYPE_PNG,
    FILE_TYPE_WEBP
]

SLASH_MEMEOFF_HELP: str = "help"
SLASH_MEMEOFF_VERSION: str = "version"

SLASH_MEMEOFF_OPTIONS: List[str] = [
    SLASH_MEMEOFF_HELP,
    SLASH_MEMEOFF_VERSION
]

EMOJI_STYLE_APPLE: str = "apple"
EMOJI_STYLE_GOOGLE: str = "google"
EMOJI_STYLE_FACEBOOK: str = "facebook"
EMOJI_STYLE_TWITTER: str = "twitter"

EMOJI_STYLES_ALL: List[str] = [
    EMOJI_STYLE_APPLE,
    EMOJI_STYLE_GOOGLE,
    EMOJI_STYLE_FACEBOOK,
    EMOJI_STYLE_TWITTER
]

SLEEP_ERROR_MINOR: int = 10

PATH_MEMEOFF: Path = Path(__file__).parent.parent.absolute()
PATH_FONTS: Path = PATH_MEMEOFF / DIR_CONFIG / DIR_FONTS

PATH_FONTS_DEMOTIV_TITLE: Path = PATH_FONTS / NAME_DEMOTIV / DIR_TITLE
PATH_FONTS_DEMOTIV_SUBTITLE: Path = PATH_FONTS / NAME_DEMOTIV / DIR_SUBTITLE
PATH_FONTS_GIFCAP: Path = PATH_FONTS / NAME_GIFCAP
PATH_FONTS_IMPACT: Path = PATH_FONTS / NAME_IMPACT
PATH_FONTS_TWITTER: Path = PATH_FONTS / NAME_TWITTER
PATH_FONTS_WHISPER: Path = PATH_FONTS / NAME_WHISPER
