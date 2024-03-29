from abc import ABC
from textwrap import wrap
from PIL import Image, ImageDraw, ImageOps
from PIL import ImageFont
from src.pilmojicore import *


class MemeFormat(ABC):

    def __init__(self, logger) -> None:
        super().__init__()

        self.logger = logger

    @staticmethod
    def _generate_font(text_lines, image, font_path, init_font_size,
                       font_scale=1.0, emoji_scale_factor: float = None):
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


class ImpactFormat(MemeFormat):
    POSITION_TOP = "TOP"
    POSITION_BOTTOM = "BOTTOM"

    WORD_WRAP = 25
    INIT_FONT_SIZE = 50
    MAX_FONT = 0.94
    OFFSET = 2
    PAD_BOTTOM = 10
    EMOJI_SCALE = 0.9

    def __init__(self, logger, font_path) -> None:
        super().__init__(logger)

        self.font_path = font_path

    def apply_format(self, image, list_text, position):
        position = position.strip().upper()

        i_width, i_height = image.size
        text_lines = wrap(
            ' '.join(list_text).upper(),
            width=ImpactFormat.WORD_WRAP)

        font = self._generate_font(
            text_lines=text_lines,
            image=image,
            font_path=self.font_path,
            init_font_size=self.INIT_FONT_SIZE,
            font_scale=self.MAX_FONT,
            emoji_scale_factor=self.EMOJI_SCALE)

        max_text_height = self._get_max_text_height(
            text_lines=text_lines, font=font)

        for i, text in enumerate(text_lines):
            with Pilmoji(image) as pimoji:
                t_width, t_height = pimoji.getsize(
                    text=text,
                    font=font,
                    emoji_scale_factor=self.EMOJI_SCALE)

            x = int((i_width - t_width) / 2)

            if position == ImpactFormat.POSITION_TOP:
                y = int(i * max_text_height)

            elif position == ImpactFormat.POSITION_BOTTOM:
                y = i_height - \
                    self.PAD_BOTTOM - \
                    int((len(text_lines) - i) * max_text_height)
            else:
                return image  # todo handle invalid position

            for pos in [
                (x - ImpactFormat.OFFSET, y - ImpactFormat.OFFSET),
                (x + ImpactFormat.OFFSET, y - ImpactFormat.OFFSET),
                (x - ImpactFormat.OFFSET, y + ImpactFormat.OFFSET),
                (x + ImpactFormat.OFFSET, y + ImpactFormat.OFFSET)
            ]:
                with Pilmoji(image) as pilmoji:
                    pilmoji.text(pos, text, fill=(0, 0, 0), font=font,
                                 emoji_scale_factor=self.EMOJI_SCALE,
                                 emoji_position_offset=(0, 7),
                                 emoji_fill=(0, 0, 0))

            with Pilmoji(image) as pilmoji:
                pilmoji.text((x, y), text, fill=(255, 255, 255), font=font,
                             emoji_scale_factor=self.EMOJI_SCALE,
                             emoji_position_offset=(0, 7))

        return image


class TwitterFormat(MemeFormat):
    WORD_WRAP = 30
    INIT_FONT_SIZE = 42
    MAX_FONT = 0.94
    PAD_WHITE = 15
    RADIUS = 60
    RADIUS_MULTIPLY = 3

    def __init__(self, logger, font_path) -> None:
        super().__init__(logger)

        self.font_path = font_path

    def apply_format(self, image, list_text):
        text_lines = wrap(
            ' '.join(list_text),
            width=TwitterFormat.WORD_WRAP)

        font = self._generate_font(
            text_lines=text_lines,
            image=image,
            font_path=self.font_path,
            init_font_size=self.INIT_FONT_SIZE,
            font_scale=self.MAX_FONT)

        max_text_height = self._get_max_text_height(
            text_lines=text_lines,
            font=font)

        image = TwitterFormat._add_corners(image, TwitterFormat.RADIUS)

        pad_top = int(TwitterFormat.PAD_WHITE * 2.4)
        pad_white_top = pad_top + (len(text_lines) * max_text_height)
        border = (TwitterFormat.PAD_WHITE,
                  pad_white_top,
                  TwitterFormat.PAD_WHITE,
                  TwitterFormat.PAD_WHITE)

        image = ImageOps.expand(image, border=border, fill="white")

        for i, text in enumerate(text_lines):
            x = TwitterFormat.PAD_WHITE
            y = int(pad_top * 0.42) + (i * max_text_height)

            with Pilmoji(image) as pilmoji:
                pilmoji.text((x, y), text, fill=(0, 0, 0), font=font,
                             emoji_position_offset=(0, 3))

        return image

    @staticmethod
    def _add_corners(image, radius):
        # Adapted from: https://stackoverflow.com/a/11291419

        # Temporarily double image size so that corners appear smoother
        # when returned back to its original size
        w_orig, h_orig = image.size
        image = image.resize((w_orig * TwitterFormat.RADIUS_MULTIPLY,
                              h_orig * TwitterFormat.RADIUS_MULTIPLY))
        w, h = image.size

        # Add corners
        circle = Image.new('L', (radius * 2, radius * 2), 0)
        draw = ImageDraw.Draw(circle)
        draw.ellipse((0, 0, radius * 2, radius * 2), fill=255)

        alpha = Image.new('L', image.size, "white")
        alpha.paste(circle.crop((0, 0, radius, radius)),
                    (0, 0))
        alpha.paste(circle.crop((0, radius, radius, radius * 2)),
                    (0, h - radius))
        alpha.paste(circle.crop((radius, 0, radius * 2, radius)),
                    (w - radius, 0))
        alpha.paste(circle.crop((radius, radius, radius * 2, radius * 2)),
                    (w - radius, h - radius))
        image.putalpha(alpha)

        # Turn transparent corners white
        white = Image.new("RGBA", image.size, "white")
        white.paste(image, (0, 0), image)
        image = white.convert('RGB')

        # Resize to original dimensions
        image = image.resize((w_orig, h_orig))

        return image


class DemotivationalFormat(MemeFormat):
    PAD_BORDER_INNER = 3
    PAD_BORDER_OUTER_TOP = 55
    PAD_ABOVE = 35

    DT_INIT_FONT_SIZE = 60
    DT_WORD_WRAP = 18
    DT_MAX_FONT = 0.9
    DT_MAX_TEXT_SCALE = 1.1
    DT_EMOJI_SCALE = 0.85
    DT_MULTILINE_SCALE = 0.2

    DS_INIT_FONT_SIZE = 28
    DS_WORD_WRAP = 55
    DS_MAX_FONT = 0.94
    DS_EMOJI_SCALE = 1.0

    def __init__(self,
                 logger,
                 font_title_path,
                 font_subtitle_path) -> None:
        super().__init__(logger)

        self.font_title_path = font_title_path
        self.font_subtitle_path = font_subtitle_path

    def apply_format(self, image,
                     list_title=None, list_subtitle=None):
        border_inner = (
            DemotivationalFormat.PAD_BORDER_INNER,
            DemotivationalFormat.PAD_BORDER_INNER,
            DemotivationalFormat.PAD_BORDER_INNER,
            DemotivationalFormat.PAD_BORDER_INNER
        )

        border_outer = (80, self.PAD_BORDER_OUTER_TOP, 80, 0)

        image = ImageOps.expand(image, border=border_inner, fill='black')
        image = ImageOps.expand(image, border=border_inner, fill='white')
        image = ImageOps.expand(image, border=border_outer, fill='black')

        is_title = list_title is not None and len(list_title) > 0
        is_subtitle = list_subtitle is not None and len(list_subtitle) > 0

        if (not is_title) and (not is_subtitle):
            image = ImageOps.expand(
                image, border=(0, 0, 0, self.PAD_BORDER_OUTER_TOP),
                fill='black')
        else:
            image = ImageOps.expand(
                image, border=(0, 0, 0, self.PAD_ABOVE), fill='black')

            if is_title:
                image = self._add_demotivational_title(
                    image, list_title, is_subtitle)

            if is_subtitle:
                image = self._add_demotivational_subtitle(
                    image, list_subtitle, is_title)

        return image

    def _add_demotivational_title(self, image, list_title, is_subtitle):
        dt_width, dt_height = image.size

        title_lines = wrap(' '.join(list_title).upper(),
                           width=DemotivationalFormat.DT_WORD_WRAP)

        font = self._generate_font(
            text_lines=title_lines,
            image=image,
            font_path=self.font_title_path,
            init_font_size=self.DT_INIT_FONT_SIZE,
            font_scale=self.DT_MAX_FONT,
            emoji_scale_factor=self.DT_EMOJI_SCALE)

        max_text_height = self._get_max_text_height(
            text_lines=title_lines, font=font)

        max_text_height = max_text_height * self.DT_MAX_TEXT_SCALE

        len_title_lines = len(title_lines)
        title_bottom = int(len_title_lines *
                           max_text_height -
                           ((len_title_lines - 1) *
                            max_text_height *
                            self.DT_MULTILINE_SCALE))

        image = ImageOps.expand(
            image, border=(0, 0, 0, title_bottom), fill='black')

        for i, text in enumerate(title_lines):
            with Pilmoji(image) as pimoji:
                t_width, t_height = pimoji.getsize(
                    text=text,
                    font=font,
                    emoji_scale_factor=self.DT_EMOJI_SCALE)

            x = int((dt_width - t_width) / 2)
            y = int(dt_height +
                    (i * max_text_height) -
                    (max_text_height * 0.37))

            if i > 0:
                y -= int(i * max_text_height * self.DT_MULTILINE_SCALE)

            with Pilmoji(image) as pilmoji:
                pilmoji.text((x, y), text, fill=(255, 255, 255), font=font,
                             emoji_scale_factor=self.DT_EMOJI_SCALE,
                             emoji_position_offset=(0, int(max_text_height *
                                                           0.32)))
        return image

    def _add_demotivational_subtitle(self, image, list_subtitle, is_title):
        ds_width, ds_height = image.size

        subtitle_lines = wrap(' '.join(list_subtitle),
                              width=DemotivationalFormat.DS_WORD_WRAP)

        font = self._generate_font(
            text_lines=subtitle_lines,
            image=image,
            font_path=self.font_subtitle_path,
            init_font_size=self.DS_INIT_FONT_SIZE,
            font_scale=self.DS_MAX_FONT,
            emoji_scale_factor=self.DS_EMOJI_SCALE)

        max_text_height = self._get_max_text_height(
            text_lines=subtitle_lines, font=font)

        subtitle_bottom = len(subtitle_lines) * max_text_height

        image = ImageOps.expand(
            image, border=(0, 0, 0, subtitle_bottom), fill='black')

        for i, text in enumerate(subtitle_lines):
            with Pilmoji(image) as pimoji:
                t_width, t_height = pimoji.getsize(
                    text=text,
                    font=font,
                    emoji_scale_factor=self.DS_EMOJI_SCALE)

            x = int((ds_width - t_width) / 2)

            y = int(ds_height -
                    (self.PAD_ABOVE * 0.6) +
                    (i * max_text_height))

            with Pilmoji(image) as pilmoji:
                pilmoji.text((x, y), text, fill=(255, 255, 255), font=font,
                             emoji_scale_factor=self.DS_EMOJI_SCALE,
                             emoji_position_offset=(0, int(max_text_height *
                                                           0.2)))
        return image


class GIFCaptionFormat(MemeFormat):
    WORD_WRAP = 25
    INIT_FONT_SIZE = 50
    TEXT_SPACE = 5
    MAX_FONT = 0.94
    HEIGHT_PAD = 20
    EMOJI_SCALE = 0.95

    def __init__(self, logger, font_path) -> None:
        super().__init__(logger)

        self.font_path = font_path

    def apply_format(self, image, list_text):
        text_lines = wrap(
            ' '.join(list_text),
            width=GIFCaptionFormat.WORD_WRAP)

        font = self._generate_font(
            text_lines=text_lines,
            image=image,
            font_path=self.font_path,
            init_font_size=self.INIT_FONT_SIZE,
            font_scale=self.MAX_FONT)

        max_text_height = self._get_max_text_height(
            text_lines=text_lines, font=font)

        top = (GIFCaptionFormat.HEIGHT_PAD * 2) + \
              (max_text_height * len(text_lines)) + \
              (GIFCaptionFormat.TEXT_SPACE * len(text_lines))

        border = (0, top, 0, 0)
        image = ImageOps.expand(image, border=border, fill='white')

        i_width, i_height = image.size

        for i, text in enumerate(text_lines):
            with Pilmoji(image) as pimoji:
                t_width, t_height = pimoji.getsize(
                    text=text,
                    font=font,
                    emoji_scale_factor=self.EMOJI_SCALE)

            x = int((i_width - t_width) / 2)
            y = int((GIFCaptionFormat.HEIGHT_PAD * 0.95) +
                    (i * (max_text_height + GIFCaptionFormat.TEXT_SPACE)))

            with Pilmoji(image) as pilmoji:
                pilmoji.text((x, y), text, fill=(0, 0, 0), font=font,
                             emoji_scale_factor=self.EMOJI_SCALE,
                             emoji_position_offset=(0, 6))

        return image


