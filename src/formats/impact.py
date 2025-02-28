# Copyright (c) 2021-2025 r3w0p
# The following code can be redistributed and/or
# modified under the terms of the GPL-3.0 License.

from PIL import ImageFile
from pilmoji import Pilmoji

from src.constants import DELIM_CONTEXT
from src.formats import MemeFormat

_WORD_WRAP = 25
_INIT_FONT_SIZE = 50
_MAX_FONT = 0.94
_STROKE_WIDTH = 3
_PAD_BOTTOM = 13
_EMOJI_SCALE = 0.9
_EMOJI_POS_OFFSET = (0, 15)


class MemeFormatImpact(MemeFormat):

    def __init__(self, path_font: str) -> None:
        super().__init__()

        self._path_font = path_font

    def apply(
            self,
            image: ImageFile,
            text: str,
            emoji_source,
            dark: bool = False
    ) -> ImageFile:
        # Split by context
        text_context = text.split(DELIM_CONTEXT, 1)
        text_top: str = text_context[0].strip()
        text_bottom: str = (
            text_context[1].strip() if len(text_context) > 1 else ""
        )

        i_width, i_height = image.size

        # Top position
        top_lines = self._wrap_new_lines(text_top.upper(), _WORD_WRAP)
        bottom_lines = self._wrap_new_lines(text_bottom.upper(), _WORD_WRAP)

        top_font = self._generate_font(
            text_lines=top_lines,
            image=image,
            font_path=self._path_font,
            init_font_size=_INIT_FONT_SIZE,
            font_scale=_MAX_FONT,
            emoji_scale_factor=_EMOJI_SCALE)

        bottom_font = self._generate_font(
            text_lines=bottom_lines,
            image=image,
            font_path=self._path_font,
            init_font_size=_INIT_FONT_SIZE,
            font_scale=_MAX_FONT,
            emoji_scale_factor=_EMOJI_SCALE)

        top_max_height = self._get_max_text_height(
            text_lines=top_lines, font=top_font)

        bottom_max_height = self._get_max_text_height(
            text_lines=bottom_lines, font=bottom_font)

        for lines, font, pos_top in [
            (top_lines, top_font, True),
            (bottom_lines, bottom_font, False)
        ]:
            for i, text in enumerate(lines):
                with Pilmoji(image, source=emoji_source) as pilmoji:
                    t_width, t_height = pilmoji.getsize(
                        text=text,
                        font=font,
                        emoji_scale_factor=_EMOJI_SCALE)

                x = int((i_width - t_width) / 2)

                if pos_top:
                    y = int(i * top_max_height - 4)
                else:
                    y = int(
                        i_height -
                        _PAD_BOTTOM -
                        ((len(lines) - i) * bottom_max_height)
                    )

                with Pilmoji(image, source=emoji_source) as pilmoji:
                    pilmoji.text(
                        (x, y),
                        text,
                        fill=(255, 255, 255),
                        font=font,
                        stroke_width=_STROKE_WIDTH,
                        stroke_fill=(0, 0, 0),
                        emoji_scale_factor=_EMOJI_SCALE,
                        emoji_position_offset=_EMOJI_POS_OFFSET)

        return image
