# Copyright (c) 2021-2025 r3w0p
# The following code can be redistributed and/or
# modified under the terms of the GPL-3.0 License.

from PIL import ImageFile, Image, ImageDraw, ImageOps
from pilmoji import Pilmoji

from src.formats import MemeFormat

_WORD_WRAP = 24
_INIT_FONT_SIZE = 42
_MAX_FONT = 0.94
_PAD_SPACE = 15
_PAD_MULTILINE = 10
_RADIUS = 60
_RADIUS_MULTIPLY = 3
_EMOJI_POS_OFFSET = (0, 3)


class MemeFormatTwitter(MemeFormat):

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
        fill_bg = "#15202b" if dark else "white"
        fill_txt = "white" if dark else "black"

        text_lines = self._wrap_new_lines(text, _WORD_WRAP)

        font = self._generate_font(
            text_lines=text_lines,
            image=image,
            font_path=self._path_font,
            init_font_size=_INIT_FONT_SIZE,
            font_scale=_MAX_FONT)

        max_text_height = self._get_max_text_height(
            text_lines=text_lines, font=font)

        image = self._add_corners(image, _RADIUS, fill_bg)

        pad_space_top = int(
            _PAD_SPACE * 2 +
            len(text_lines) * (max_text_height + _PAD_MULTILINE)
        )
        border = (_PAD_SPACE, pad_space_top, _PAD_SPACE, _PAD_SPACE)

        image = ImageOps.expand(image, border=border, fill=fill_bg)

        for i, text in enumerate(text_lines):
            x = _PAD_SPACE
            y = int(
                _PAD_SPACE +
                i * (max_text_height + _PAD_MULTILINE)
            )

            with Pilmoji(image, source=emoji_source) as pilmoji:
                pilmoji.text(
                    (x, y),
                    text,
                    fill=fill_txt,
                    font=font,
                    emoji_position_offset=_EMOJI_POS_OFFSET)

        return image

    @staticmethod
    def _add_corners(image, radius, fill_bg):
        # Adapted from: https://stackoverflow.com/a/11291419

        # Temporarily double image size so that corners appear smoother
        # when returned back to its original size
        w_orig, h_orig = image.size
        image = image.resize((
            w_orig * _RADIUS_MULTIPLY,
            h_orig * _RADIUS_MULTIPLY
        ))
        w, h = image.size

        # Add corners
        image_circle = Image.new(
            mode='L',
            size=(radius * 2, radius * 2),
            color="black"
        )
        draw = ImageDraw.Draw(image_circle)
        draw.ellipse((0, 0, radius * 2, radius * 2), fill="white")

        alpha = Image.new('L', image.size, color="white")
        alpha.paste(image_circle.crop(
            (0, 0, radius, radius)), (0, 0)
        )
        alpha.paste(image_circle.crop(
            (0, radius, radius, radius * 2)), (0, h - radius)
        )
        alpha.paste(image_circle.crop(
            (radius, 0, radius * 2, radius)), (w - radius, 0)
        )
        alpha.paste(image_circle.crop(
            (radius, radius, radius * 2, radius * 2)),
            (w - radius, h - radius)
        )
        image.putalpha(alpha)

        # Fill transparent corners
        image_fill = Image.new("RGBA", image.size, color=fill_bg)
        image_fill.paste(image, (0, 0), image)
        image = image_fill.convert('RGB')

        # Resize to original dimensions
        image = image.resize((w_orig, h_orig))

        return image
