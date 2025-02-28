# Copyright (c) 2021-2025 r3w0p
# The following code can be redistributed and/or
# modified under the terms of the GPL-3.0 License.
from PIL import ImageFile, ImageOps
from pilmoji import Pilmoji

from src.formats import MemeFormat

_WORD_WRAP = 25
_INIT_FONT_SIZE = 80
_TEXT_SPACE = 6
_MAX_FONT = 0.94
_HEIGHT_PAD = 20
_EMOJI_SCALE = 0.8
_EMOJI_POS_OFFSET = (0, 17)


class MemeFormatGifcap(MemeFormat):

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
        text_lines = self._wrap_new_lines(text, _WORD_WRAP)

        font = self._generate_font(
            text_lines=text_lines,
            image=image,
            font_path=self._path_font,
            init_font_size=_INIT_FONT_SIZE,
            font_scale=_MAX_FONT)

        max_text_height = self._get_max_text_height(
            text_lines=text_lines, font=font)

        top = int(
            _HEIGHT_PAD * 2 +
            max_text_height * len(text_lines) +
            _TEXT_SPACE * len(text_lines)
        )

        border = (0, top, 0, 0)
        image = ImageOps.expand(image, border=border, fill='white')

        i_width, i_height = image.size

        for i, text in enumerate(text_lines):
            with Pilmoji(image, source=emoji_source) as pilmoji:
                t_width, t_height = pilmoji.getsize(
                    text=text,
                    font=font,
                    emoji_scale_factor=_EMOJI_SCALE)

            x = int((i_width - t_width) / 2)
            y = int(
                _HEIGHT_PAD * 0.7 +
                i * (max_text_height + _TEXT_SPACE)
            )

            with Pilmoji(image, source=emoji_source) as pilmoji:
                pilmoji.text(
                    (x, y),
                    text,
                    fill=(0, 0, 0),
                    font=font,
                    emoji_scale_factor=_EMOJI_SCALE,
                    emoji_position_offset=_EMOJI_POS_OFFSET)

        return image
