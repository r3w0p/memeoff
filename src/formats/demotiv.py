# Copyright (c) 2021-2025 r3w0p
# The following code can be redistributed and/or
# modified under the terms of the GPL-3.0 License.
from PIL import ImageFile, ImageOps
from pilmoji import Pilmoji

from src.constants import DELIM_CONTEXT
from src.formats import MemeFormat

_BORDER_PAD_INNER = 3
_BORDER_PAD_OUTER_TOP = 55
_BORDER_PAD_OUTER_SIDES_INIT = 75
_BORDER_PAD_OUTER_SIDES_FINAL = 25

_TITLE_PAD_ABOVE = 38
_TITLE_WORD_WRAP = 18
_TITLE_FONT_SIZE_INIT = 60
_TITLE_FONT_SCALE = 0.9
_TITLE_EMOJI_SCALE = 0.85
_TITLE_EMOJI_POS_OFFSET = (0, 8)

_SUBTITLE_PAD_ABOVE_SOLO = 20
_SUBTITLE_PAD_BELOW = 30
_SUBTITLE_WORD_WRAP = 54
_SUBTITLE_FONT_SIZE_INIT = 26
_SUBTITLE_FONT_SCALE = 1.0
_SUBTITLE_EMOJI_SCALE = 1.0
_SUBTITLE_EMOJI_POS_OFFSET = (0, 5)


class MemeFormatDemotiv(MemeFormat):

    def __init__(self, path_font_title: str, path_font_subtitle: str) -> None:
        super().__init__()

        self._path_font_title = path_font_title
        self._path_font_subtitle = path_font_subtitle

    def apply(
            self,
            image: ImageFile,
            text: str,
            emoji_source,
            dark: bool = False
    ) -> ImageFile:
        text_context = text.split(DELIM_CONTEXT, 1)
        text_title: str = text_context[0].strip()
        text_subtitle: str = (
            text_context[1].strip() if len(text_context) > 1 else ""
        )

        title_lines = self._wrap_new_lines(
            text_title.upper(), _TITLE_WORD_WRAP)
        subtitle_lines = self._wrap_new_lines(
            text_subtitle, _SUBTITLE_WORD_WRAP)

        border_inner = (
            _BORDER_PAD_INNER,
            _BORDER_PAD_INNER,
            _BORDER_PAD_INNER,
            _BORDER_PAD_INNER
        )

        border_outer = (
            _BORDER_PAD_OUTER_SIDES_INIT,
            _BORDER_PAD_OUTER_TOP,
            _BORDER_PAD_OUTER_SIDES_INIT,
            0
        )

        image = ImageOps.expand(image, border=border_inner, fill="black")
        image = ImageOps.expand(image, border=border_inner, fill="white")
        image = ImageOps.expand(image, border=border_outer, fill="black")

        is_title = text_title is not None and len(text_title) > 0
        is_subtitle = text_subtitle is not None and len(text_subtitle) > 0

        if (not is_title) and (not is_subtitle):
            image = ImageOps.expand(
                image,
                border=(0, 0, 0, _BORDER_PAD_OUTER_TOP),
                fill="black")
        else:
            if is_title:
                image = self._apply_title(image, title_lines, emoji_source,
                                          is_subtitle)

            if is_subtitle:
                image = self._apply_subtitle(image, subtitle_lines,
                                             emoji_source, is_title)

        # Final padding to ensure text gap
        image = ImageOps.expand(
            image,
            border=(
                _BORDER_PAD_OUTER_SIDES_FINAL, 0,
                _BORDER_PAD_OUTER_SIDES_FINAL, 0
            ),
            fill="black"
        )

        return image

    def _apply_title(self, image, title_lines, emoji_source, is_subtitle):
        image = ImageOps.expand(
            image,
            border=(0, 0, 0, _TITLE_PAD_ABOVE),
            fill="black")

        dt_width, dt_height = image.size

        font = self._generate_font(
            text_lines=title_lines,
            image=image,
            font_path=self._path_font_title,
            init_font_size=_TITLE_FONT_SIZE_INIT,
            font_scale=_TITLE_FONT_SCALE,
            emoji_scale_factor=_TITLE_EMOJI_SCALE)

        max_text_height = self._get_max_text_height(
            text_lines=title_lines, font=font)

        len_title_lines = len(title_lines)
        title_bottom = int(len_title_lines * max_text_height * 0.9) + 5

        image = ImageOps.expand(
            image, border=(0, 0, 0, title_bottom), fill="black")

        for i, text in enumerate(title_lines):
            with Pilmoji(image, source=emoji_source) as pilmoji:
                t_width, t_height = pilmoji.getsize(
                    text=text,
                    font=font,
                    emoji_scale_factor=_TITLE_EMOJI_SCALE)

            x = int((dt_width - t_width) / 2)
            y = int(
                dt_height +
                i * (max_text_height * 0.95) -
                max_text_height * 0.5
            )

            with Pilmoji(image, source=emoji_source) as pilmoji:
                pilmoji.text(
                    (x, y),
                    text,
                    fill=(255, 255, 255),
                    font=font,
                    emoji_scale_factor=_TITLE_EMOJI_SCALE,
                    emoji_position_offset=_TITLE_EMOJI_POS_OFFSET)

        return image

    def _apply_subtitle(self, image, subtitle_lines, emoji_source, is_title):
        if not is_title:
            image = ImageOps.expand(
                image,
                border=(0, 0, 0, _SUBTITLE_PAD_ABOVE_SOLO),
                fill="black")

        ds_width, ds_height = image.size

        font = self._generate_font(
            text_lines=subtitle_lines,
            image=image,
            font_path=self._path_font_subtitle,
            init_font_size=_SUBTITLE_FONT_SIZE_INIT,
            font_scale=_SUBTITLE_FONT_SCALE,
            emoji_scale_factor=_SUBTITLE_EMOJI_SCALE)

        max_text_height = self._get_max_text_height(
            text_lines=subtitle_lines, font=font) + 5

        subtitle_bottom = len(subtitle_lines) * max_text_height + 5

        image = ImageOps.expand(
            image, border=(0, 0, 0, subtitle_bottom), fill="black")

        for i, text in enumerate(subtitle_lines):
            with Pilmoji(image, source=emoji_source) as pimoji:
                t_width, t_height = pimoji.getsize(
                    text=text,
                    font=font,
                    emoji_scale_factor=_SUBTITLE_EMOJI_SCALE)

            x = int((ds_width - t_width) / 2)

            if is_title:
                y = int(
                    ds_height +
                    i * max_text_height -
                    max_text_height * 0.3
                )
            else:
                y = int(
                    ds_height +
                    i * max_text_height -
                    max_text_height * 0.2
                )

            with Pilmoji(image, source=emoji_source) as pilmoji:
                pilmoji.text(
                    (x, y),
                    text,
                    fill=(255, 255, 255),
                    font=font,
                    emoji_scale_factor=_SUBTITLE_EMOJI_SCALE,
                    emoji_position_offset=_SUBTITLE_EMOJI_POS_OFFSET)

        return image
