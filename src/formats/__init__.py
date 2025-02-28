# Copyright (c) 2021-2025 r3w0p
# The following code can be redistributed and/or
# modified under the terms of the GPL-3.0 License.

from abc import ABC, abstractmethod
from textwrap import wrap
from typing import List

from PIL import ImageFile, ImageFont
from pilmoji import Pilmoji

from src.constants import DELIM_NEWLINE


class MemeFormat(ABC):

    @abstractmethod
    def apply(
            self,
            image: ImageFile,
            text: str,
            emoji_source,
            dark: bool = False
    ) -> ImageFile:
        """"""

    @staticmethod
    def _generate_font(
            text_lines,
            image,
            font_path,
            init_font_size,
            font_scale=1.0,
            emoji_scale_factor: float = None
    ):
        font = ImageFont.truetype(font_path, init_font_size)
        pilmoji = Pilmoji(image)
        width_scaled = image.size[0] * font_scale
        current_font_size = init_font_size

        for text in text_lines:
            while pilmoji.getsize(
                    text=text,
                    font=font,
                    emoji_scale_factor=emoji_scale_factor)[0] > width_scaled:
                current_font_size -= 1
                font = ImageFont.truetype(font_path, current_font_size)

        pilmoji.close()
        return font

    @staticmethod
    def _get_max_text_height(text_lines, font):
        max_text_height = 0

        for text in text_lines:
            text_size = font.getsize(text)
            if text_size[1] > max_text_height:
                max_text_height = text_size[1]

        return max_text_height

    @staticmethod
    def _wrap_new_lines(
            text: str,
            word_wrap: int,
            break_long_words: bool = True
    ) -> List[str]:
        text_split_nl = text.split(DELIM_NEWLINE)
        text_lines = []

        for t in text_split_nl:
            t = t.strip()

            if len(t) == 0:
                l = [" "]
            else:
                l = wrap(
                    text=t,
                    width=word_wrap,
                    break_long_words=break_long_words
                )

            text_lines += l

        return text_lines
