from abc import ABC
from textwrap import wrap
from PIL import Image, ImageDraw, ImageOps
from PIL import ImageFont
from pilmoji import Pilmoji
from math import floor


class MemeFormat(ABC):

    def __init__(self, logger) -> None:
        super().__init__()

        self.logger = logger

    @staticmethod
    def _generate_font(text_lines, image, font_path, init_font_size,
                       max_font=1.0):
        font = ImageFont.truetype(font_path, init_font_size)
        for text in text_lines:
            while font.getsize(text)[0] > (image.size[0] * max_font):
                init_font_size -= 1
                font = ImageFont.truetype(font_path, init_font_size)

        max_text_height = 0
        for text in text_lines:
            text_size = font.getsize(text)
            if text_size[1] > max_text_height:
                max_text_height = text_size[1]

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
    INIT_FONT_SIZE = 60
    MAX_FONT = 0.94
    OFFSET = 2
    BOTTOM_PAD = 10

    def __init__(self, logger, font_path) -> None:
        super().__init__(logger)

        self.font_path = font_path

    def apply_format(self, image, list_text, position):
        position = position.strip().upper()
        draw = ImageDraw.Draw(image)

        i_width, i_height = image.size
        text_lines = wrap(
            ' '.join(list_text).upper(),
            width=ImpactFormat.WORD_WRAP)

        font = self._generate_font(
            text_lines=text_lines,
            image=image,
            font_path=self.font_path,
            init_font_size=self.INIT_FONT_SIZE,
            max_font=self.MAX_FONT)

        max_text_height = self._get_max_text_height(
            text_lines=text_lines, font=font)

        for i, text in enumerate(text_lines):
            t_width, t_height = draw.textsize(text, font=font)
            x = (i_width - t_width) / 2

            if position == ImpactFormat.POSITION_TOP:
                y = (i * max_text_height)

            elif position == ImpactFormat.POSITION_BOTTOM:
                y = i_height - \
                    self.BOTTOM_PAD - \
                    ((len(text_lines) - i) * max_text_height)
            else:
                return image  # invalid position

            for pos in [
                (x - ImpactFormat.OFFSET, y - ImpactFormat.OFFSET),
                (x + ImpactFormat.OFFSET, y - ImpactFormat.OFFSET),
                (x - ImpactFormat.OFFSET, y + ImpactFormat.OFFSET),
                (x + ImpactFormat.OFFSET, y + ImpactFormat.OFFSET)
            ]:
                draw.text(pos, text, font=font, fill="black")

            draw.text((x, y), text, font=font, fill="white")

        return image


class TwitterFormat(MemeFormat):
    WORD_WRAP = 30
    INIT_FONT_SIZE = 45
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
            max_font=self.MAX_FONT)

        max_text_height = self._get_max_text_height(
            text_lines=text_lines, font=font)

        image = TwitterFormat._add_corners(image, TwitterFormat.RADIUS)

        top = floor(TwitterFormat.PAD_WHITE * 2.5) + \
              (len(text_lines) * max_text_height)

        border = (TwitterFormat.PAD_WHITE,
                  top,
                  TwitterFormat.PAD_WHITE,
                  TwitterFormat.PAD_WHITE)

        image = ImageOps.expand(image, border=border, fill='white')
        draw = ImageDraw.Draw(image)

        for i, text in enumerate(text_lines):
            x = TwitterFormat.PAD_WHITE
            y = TwitterFormat.PAD_WHITE + (i * max_text_height)

            draw.text((x, y), text, font=font, fill="black")

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

    DT_INIT_FONT_SIZE = 60
    DT_WORD_WRAP = 18
    DT_MAX_FONT = 0.9

    DS_INIT_FONT_SIZE = 28
    DS_WORD_WRAP = 55
    DS_MAX_FONT = 0.94

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

        border_outer = (80, 55, 80, 0)

        image = ImageOps.expand(image, border=border_inner, fill='black')
        image = ImageOps.expand(image, border=border_inner, fill='white')
        image = ImageOps.expand(image, border=border_outer, fill='black')

        if list_title is None and list_subtitle is None:
            image = ImageOps.expand(
                image, border=(0, 0, 0, 50), fill='black')

        else:
            if list_title is not None:
                image = ImageOps.expand(
                    image, border=(0, 0, 0, 34), fill='black')

                image = self._add_demotivational_title(image, list_title)

            if list_subtitle is not None:
                if list_title is None:
                    image = ImageOps.expand(
                        image, border=(0, 0, 0, 28), fill='black')

                image = self._add_demotivational_subtitle(image, list_subtitle)

        return image

    def _add_demotivational_title(self, image, list_title):
        dt_width, dt_height = image.size

        title_lines = wrap(' '.join(list_title).upper(),
                           width=DemotivationalFormat.DT_WORD_WRAP)

        font = self._generate_font(
            text_lines=title_lines,
            image=image,
            font_path=self.font_title_path,
            init_font_size=self.DT_INIT_FONT_SIZE,
            max_font=self.DT_MAX_FONT)

        max_text_height = self._get_max_text_height(
            text_lines=title_lines, font=font)

        title_bottom = len(title_lines) * max_text_height

        image = ImageOps.expand(
            image, border=(0, 0, 0, title_bottom), fill='black')

        dt_draw = ImageDraw.Draw(image)

        for i, text in enumerate(title_lines):
            t_width, t_height = dt_draw.textsize(text, font=font)

            x = (dt_width - t_width) / 2
            y = dt_height - \
                (max_text_height / 2) + (i * max_text_height)

            dt_draw.text((x, y), text, font=font, fill="white")

        return image

    def _add_demotivational_subtitle(self, image, list_subtitle):
        ds_width, ds_height = image.size

        subtitle_lines = wrap(' '.join(list_subtitle),
                              width=DemotivationalFormat.DS_WORD_WRAP)

        font = self._generate_font(
            text_lines=subtitle_lines,
            image=image,
            font_path=self.font_subtitle_path,
            init_font_size=self.DS_INIT_FONT_SIZE,
            max_font=self.DS_MAX_FONT)

        max_text_height = self._get_max_text_height(
            text_lines=subtitle_lines, font=font)

        subtitle_bottom = len(subtitle_lines) * max_text_height

        image = ImageOps.expand(
            image, border=(0, 0, 0, subtitle_bottom), fill='black')

        ds_draw = ImageDraw.Draw(image)

        for i, text in enumerate(subtitle_lines):
            t_width, t_height = ds_draw.textsize(
                text, font=font)

            x = (ds_width - t_width) / 2
            y = ds_height - \
                (max_text_height / 2) + (i * max_text_height)

            ds_draw.text((x, y), text, font=font, fill="white")

        return image


class GIFCaptionFormat(MemeFormat):
    WORD_WRAP = 25
    INIT_FONT_SIZE = 50
    TEXT_SPACE = 5
    MAX_FONT = 0.94
    HEIGHT_PAD = 20

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
            max_font=self.MAX_FONT)

        max_text_height = self._get_max_text_height(
            text_lines=text_lines, font=font)

        top = (GIFCaptionFormat.HEIGHT_PAD * 2) + \
              (max_text_height * len(text_lines)) + \
              (GIFCaptionFormat.TEXT_SPACE * len(text_lines))

        border = (0, top, 0, 0)
        image = ImageOps.expand(image, border=border, fill='white')

        draw = ImageDraw.Draw(image)
        i_width, i_height = image.size

        for i, text in enumerate(text_lines):
            t_width, t_height = draw.textsize(text, font=font)

            x = (i_width - t_width) / 2
            y = GIFCaptionFormat.HEIGHT_PAD + \
                (i * (max_text_height + GIFCaptionFormat.TEXT_SPACE))

            draw.text((x, y), text, font=font, fill="black")

        return image


