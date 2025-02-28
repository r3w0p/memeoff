# Copyright (c) 2021-2025 r3w0p
# The following code can be redistributed and/or
# modified under the terms of the GPL-3.0 License.
from glob import glob
from math import floor
from os.path import splitext
from re import split as re_split
from typing import Dict
from urllib.parse import urlparse

import requests
from PIL import Image
from pilmoji.source import EmojiCDNSource, AppleEmojiSource, GoogleEmojiSource, \
    FacebookEmojiSource, TwitterEmojiSource

from src.constants import *
from src.exceptions import MinorMemeoffError, MajorMemeoffError
from src.formats import *
from src.formats.demotiv import MemeFormatDemotiv
from src.formats.gifcap import MemeFormatGifcap
from src.formats.impact import MemeFormatImpact
from src.formats.twitter import MemeFormatTwitter
from src.formats.whisper import MemeFormatWhisper

_EXC_FONT_NOT_FOUND: str = "Font not found: %s"
_EXC_FONT_MULTIPLE: str = "Multiple fonts found: %s"


def process_content(
        image,
        content: str,
        formats,
        emoji_source
):
    # Remove variant selectors
    # FE0E: emoji to be presented as text
    content = content.replace(u"\uFE0E", "")
    # FE0F: emoji to be presented as an image (color, animation)
    content = content.replace(u"\uFE0F", "")
    # 2642: male variant
    content = content.replace(u"\u2642", "")
    # 2640: female variant
    content = content.replace(u"\u2640", "")
    # 200D: zero-width joiner, joins emoji into a single glyph
    content = content.replace(u"\u200D", "")

    # Remove spoiler marks at start and end, if they exist
    if (
            content.startswith(DELIM_SPOILER) and
            content.endswith(DELIM_SPOILER)
    ):
        content = content[len(DELIM_SPOILER):][:-len(DELIM_SPOILER)]

    # Options
    dark: bool = COMMAND_DARK in content

    content_split: List[str] = [
        x.strip() for x in re_split(REGEX_PATTERN_SLASH, content)
        if x is not None and len(x.strip()) > 0
    ]
    len_content_split: int = len(content_split)

    i: int = 0
    # if first split is not a slash string, skip it
    if not is_memeoff_command(content_split[i]):
        i += 1

    # Parse and apply format requests
    while i < len_content_split:
        slash: str = content_split[i]
        text: str = (
            content_split[i + 1] if (
                    i + 1 < len_content_split and
                    not is_memeoff_command(content_split[i + 1])
            ) else ""
        )

        i += 1 if len(text) == 0 else 2

        if slash == COMMAND_DEMOTIV:
            image = formats[NAME_DEMOTIV].apply(image, text, emoji_source)

        elif slash == COMMAND_GIFCAP:
            image = formats[NAME_GIFCAP].apply(image, text, emoji_source)

        elif slash == COMMAND_IMPACT:
            image = formats[NAME_IMPACT].apply(image, text, emoji_source)

        elif slash == COMMAND_TWITTER:
            image = formats[NAME_TWITTER].apply(
                image=image,
                text=text,
                emoji_source=emoji_source,
                dark=dark
            )

        elif slash == COMMAND_WHISPER:
            image = formats[NAME_WHISPER].apply(image, text, emoji_source)

    return image


def emoji_style_to_pilmoji_source_class(
        style: str
) -> EmojiCDNSource.__class__:
    if style == EMOJI_STYLE_APPLE:
        return AppleEmojiSource

    if style == EMOJI_STYLE_GOOGLE:
        return GoogleEmojiSource

    if style == EMOJI_STYLE_FACEBOOK:
        return FacebookEmojiSource

    if style == EMOJI_STYLE_TWITTER:
        return TwitterEmojiSource

    raise MajorMemeoffError(f"Invalid emoji style: {style}")


def message_has_image_reference(message) -> bool:
    # Attachment
    if len(message.attachments) > 0:
        return True

    # Reply Attachment
    if (
            message.reference is not None and
            message.reference.resolved is not None and
            len(message.reference.resolved.attachments) > 0
    ):
        return True

    return False


async def download_image_from_message(message):
    # Attachment
    if len(message.attachments) > 0:
        return download_image(message.attachments[0].url)

    # Reply Attachment
    else:
        return download_image(
            message.reference.resolved.attachments[0].url
        )


def reshape_image(image):
    # Check whether image is too small
    # if IMAGE_WIDTH_MIN > 0 and image.size[0] < IMAGE_WIDTH_MIN:
    #    raise MinorMemeoffError(
    #        f"Cannot use image from {image_url}: "
    #        f"width is less than {IMAGE_WIDTH_MIN}px.")

    # Check whether image meets the enforced width, and resize if not
    if image.size[0] > IMAGE_WIDTH_FORCE:
        reduction = (image.size[0] - IMAGE_WIDTH_FORCE) / image.size[0]
        height_reduced = floor(image.size[1] * (1 - reduction))

        image = image.resize((IMAGE_WIDTH_FORCE, height_reduced))

    elif image.size[0] < IMAGE_WIDTH_FORCE:
        increase = IMAGE_WIDTH_FORCE / image.size[0]
        height_increased = floor(image.size[1] * increase)

        image = image.resize((IMAGE_WIDTH_FORCE, height_increased))

    return image


def image_ftype_from_url(image_url) -> str:
    image_ftype = splitext(urlparse(image_url).path)[1][1:].upper()

    # PIL cannot handle "JPG"
    if image_ftype == FILE_TYPE_JPG:
        image_ftype = FILE_TYPE_JPEG

    return image_ftype


def image_ftype_from_path(image_path: Path) -> str:
    image_ftype = image_path.suffix[1:].upper()

    # PIL cannot handle "JPG"
    if image_ftype == FILE_TYPE_JPG:
        image_ftype = FILE_TYPE_JPEG

    return image_ftype


def download_image(image_url):
    try:
        image_response = requests.get(image_url, stream=True).raw

    except Exception as e:
        raise MinorMemeoffError(
            f"Failed to download image at {image_url}: {e}")

    try:
        image = Image.open(image_response)

    except Exception as e:
        raise MinorMemeoffError(
            f"Failed to open image from {image_url}: {e}")

    image = reshape_image(image)
    image_ftype = image_ftype_from_url(image_url)

    return image, image_ftype


def contains_memeoff_format(s: str) -> bool:
    return any(slash in s for slash in COMMANDS_FORMATS)


def is_memeoff_command(s: str) -> bool:
    return any(s == slash for slash in COMMANDS_ALL)


def get_formats() -> Dict[str, MemeFormat]:
    return {
        NAME_DEMOTIV: _get_format_demotiv(),
        NAME_GIFCAP: _get_format_gifcap(),
        NAME_IMPACT: _get_format_impact(),
        NAME_TWITTER: _get_format_twitter(),
        NAME_WHISPER: _get_format_whisper()
    }


def _get_format_demotiv() -> MemeFormat:
    demotiv_title_glob = glob(str(PATH_FONTS_DEMOTIV_TITLE / "*.ttf"))
    demotiv_subtitle_glob = glob(str(PATH_FONTS_DEMOTIV_SUBTITLE / "*.ttf"))

    if len(demotiv_title_glob) == 0:
        raise RuntimeError(
            _EXC_FONT_NOT_FOUND.format(f"{NAME_DEMOTIV} {NAME_TITLE}"))

    if len(demotiv_title_glob) > 1:
        raise RuntimeError(
            _EXC_FONT_MULTIPLE.format(f"{NAME_DEMOTIV} {NAME_TITLE}"))

    if len(demotiv_subtitle_glob) == 0:
        raise RuntimeError(
            _EXC_FONT_NOT_FOUND.format(f"{NAME_DEMOTIV} {NAME_SUBTITLE}"))

    if len(demotiv_subtitle_glob) > 1:
        raise RuntimeError(
            _EXC_FONT_MULTIPLE.format(f"{NAME_DEMOTIV} {NAME_SUBTITLE}"))

    return MemeFormatDemotiv(
        path_font_title=demotiv_title_glob[0],
        path_font_subtitle=demotiv_subtitle_glob[0]
    )


def _get_format_gifcap() -> MemeFormat:
    gifcap_glob = glob(str(PATH_FONTS_GIFCAP / "*.ttf"))

    if len(gifcap_glob) == 0:
        raise RuntimeError(_EXC_FONT_NOT_FOUND.format(NAME_GIFCAP))

    if len(gifcap_glob) > 1:
        raise RuntimeError(_EXC_FONT_MULTIPLE.format(NAME_GIFCAP))

    return MemeFormatGifcap(
        path_font=gifcap_glob[0]
    )


def _get_format_impact() -> MemeFormat:
    impact_glob = glob(str(PATH_FONTS_IMPACT / "*.ttf"))

    if len(impact_glob) == 0:
        raise RuntimeError(_EXC_FONT_NOT_FOUND.format(NAME_IMPACT))

    if len(impact_glob) > 1:
        raise RuntimeError(_EXC_FONT_MULTIPLE.format(NAME_IMPACT))

    return MemeFormatImpact(
        path_font=impact_glob[0]
    )


def _get_format_twitter() -> MemeFormat:
    twitter_glob = glob(str(PATH_FONTS_TWITTER / "*.ttf"))

    if len(twitter_glob) == 0:
        raise RuntimeError(_EXC_FONT_NOT_FOUND.format(NAME_TWITTER))

    if len(twitter_glob) > 1:
        raise RuntimeError(_EXC_FONT_MULTIPLE.format(NAME_TWITTER))

    return MemeFormatTwitter(
        path_font=twitter_glob[0]
    )


def _get_format_whisper() -> MemeFormat:
    whisper_glob = glob(str(PATH_FONTS_WHISPER / "*.ttf"))

    if len(whisper_glob) == 0:
        raise RuntimeError(_EXC_FONT_NOT_FOUND.format(NAME_WHISPER))

    if len(whisper_glob) > 1:
        raise RuntimeError(_EXC_FONT_MULTIPLE.format(NAME_WHISPER))

    return MemeFormatWhisper(
        path_font=whisper_glob[0]
    )
