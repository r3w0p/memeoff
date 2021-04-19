from abc import ABC
from textwrap import wrap
from PIL import Image, ImageDraw, ImageOps
from PIL import ImageFont


class MemeFormat(ABC):

    def __init__(self, logger) -> None:
        super().__init__()

        self.logger = logger


class ImpactFormat(MemeFormat):
    POSITION_TOP = "TOP"
    POSITION_BOTTOM = "BOTTOM"
    OFFSET = 2
    WORD_WRAP = 26
    HEIGHT_PAD = 15
    HEIGHT_FORCE = 45

    def __init__(self, logger, font_path, font_size) -> None:
        super().__init__(logger)

        self.font_path = font_path
        self.font_size = font_size
        self.font = ImageFont.truetype(font_path, font_size)

    def apply_format(self, image, list_text, position):
        position = position.strip().upper()
        draw = ImageDraw.Draw(image)

        i_width, i_height = image.size
        text_lines = wrap(
            ' '.join(list_text).upper(),
            width=ImpactFormat.WORD_WRAP)

        for i, text in enumerate(text_lines):
            t_width, t_height = draw.textsize(text, font=self.font)

            x = (i_width - t_width) / 2

            if position == ImpactFormat.POSITION_TOP:
                y = (i * ImpactFormat.HEIGHT_FORCE)

            elif position == ImpactFormat.POSITION_BOTTOM:
                y = (i_height -
                     ImpactFormat.HEIGHT_FORCE -
                     ImpactFormat.HEIGHT_PAD) - \
                    (len(text_lines) - (i + 1)) * \
                    ImpactFormat.HEIGHT_FORCE
            else:
                return image  # invalid position

            for pos in [
                (x - ImpactFormat.OFFSET, y - ImpactFormat.OFFSET),
                (x + ImpactFormat.OFFSET, y - ImpactFormat.OFFSET),
                (x - ImpactFormat.OFFSET, y + ImpactFormat.OFFSET),
                (x + ImpactFormat.OFFSET, y + ImpactFormat.OFFSET)
            ]:
                draw.text(pos, text, font=self.font, fill="black")

            draw.text((x, y), text, font=self.font, fill="white")

        return image


class TwitterFormat(MemeFormat):
    WORD_WRAP = 30
    HEIGHT_FORCE = 45
    PAD = 15
    RADIUS = 60
    RADIUS_MULTIPLY = 3

    def __init__(self, logger, font_path, font_size) -> None:
        super().__init__(logger)

        self.font_path = font_path
        self.font_size = font_size
        self.font = ImageFont.truetype(font_path, font_size)

    def apply_format(self, image, list_text):
        text_lines = wrap(
            ' '.join(list_text),
            width=TwitterFormat.WORD_WRAP)
        image = TwitterFormat._add_corners(image, TwitterFormat.RADIUS)

        top = (TwitterFormat.PAD * 2) + \
              (len(text_lines) *
               TwitterFormat.HEIGHT_FORCE)

        border = (TwitterFormat.PAD, top, TwitterFormat.PAD, TwitterFormat.PAD)

        image = ImageOps.expand(image, border=border, fill='white')
        draw = ImageDraw.Draw(image)

        for i, text in enumerate(text_lines):
            x = TwitterFormat.PAD
            y = TwitterFormat.PAD + (i * TwitterFormat.HEIGHT_FORCE)

            draw.text((x, y), text, font=self.font, fill="black")

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
    PAD = 3
    DT_HEIGHT_FORCE = 50
    DT_WORD_WRAP = 22
    DS_HEIGHT_FORCE = 26
    DS_WORD_WRAP = 63

    def __init__(self,
                 logger,
                 font_title_path,
                 font_title_size,
                 font_subtitle_path,
                 font_subtitle_size) -> None:
        super().__init__(logger)

        self.font_title_path = font_title_path
        self.font_title_size = font_title_size
        self.font_title = ImageFont.truetype(
            font_title_path, font_title_size)

        self.font_subtitle_path = font_subtitle_path
        self.font_subtitle_size = font_subtitle_size
        self.font_subtitle = ImageFont.truetype(
            font_subtitle_path, font_subtitle_size)

    def apply_format(
            self, image, list_title=None, list_subtitle=None):
        border_inner = (
            DemotivationalFormat.PAD,
            DemotivationalFormat.PAD,
            DemotivationalFormat.PAD,
            DemotivationalFormat.PAD
        )

        border_outer = (80, 50, 80, 0)

        image = ImageOps.expand(image, border=border_inner, fill='black')
        image = ImageOps.expand(image, border=border_inner, fill='white')
        image = ImageOps.expand(image, border=border_outer, fill='black')

        if list_title is None and list_subtitle is None:
            image = ImageOps.expand(
                image,
                border=(0, 0, 0, 50),
                fill='black')

        else:
            if list_title is not None:
                image = ImageOps.expand(
                    image, border=(0, 0, 0, 8), fill='black')

                image = self._add_demotivational_title(image, list_title)

            if list_subtitle is not None:
                image = ImageOps.expand(
                    image,
                    border=(0, 0, 0, 20 if list_title is None else 17),
                    fill='black')

                image = self._add_demotivational_subtitle(image, list_subtitle)

            else:
                image = ImageOps.expand(
                    image,
                    border=(0, 0, 0, 15),
                    fill='black')

        return image

    def _add_demotivational_title(self, image, list_title):
        dt_width, dt_height = image.size

        title_lines = wrap(' '.join(list_title).upper(),
                           width=DemotivationalFormat.DT_WORD_WRAP)
        title_bottom = len(title_lines) * DemotivationalFormat.DT_HEIGHT_FORCE

        image = ImageOps.expand(
            image,
            border=(0, 0, 0, title_bottom),
            fill='black')

        dt_draw = ImageDraw.Draw(image)

        for i, text in enumerate(title_lines):
            t_width, t_height = dt_draw.textsize(
                text, font=self.font_title)

            x = (dt_width - t_width) / 2
            y = dt_height - \
                (DemotivationalFormat.DT_HEIGHT_FORCE / 2) + \
                (i * DemotivationalFormat.DT_HEIGHT_FORCE)

            dt_draw.text(
                (x, y),
                text,
                font=self.font_title,
                fill="white")

        return image

    def _add_demotivational_subtitle(self, image, list_subtitle):
        ds_width, ds_height = image.size

        subtitle_lines = wrap(' '.join(list_subtitle),
                              width=DemotivationalFormat.DS_WORD_WRAP)
        subtitle_bottom = \
            len(subtitle_lines) * \
            DemotivationalFormat.DS_HEIGHT_FORCE

        image = ImageOps.expand(
            image,
            border=(0, 0, 0, subtitle_bottom),
            fill='black')

        ds_draw = ImageDraw.Draw(image)

        for i, text in enumerate(subtitle_lines):
            t_width, t_height = ds_draw.textsize(
                text, font=self.font_subtitle)

            x = (ds_width - t_width) / 2
            y = ds_height - \
                (DemotivationalFormat.DS_HEIGHT_FORCE / 2) + \
                (i * DemotivationalFormat.DS_HEIGHT_FORCE)

            ds_draw.text(
                (x, y),
                text,
                font=self.font_subtitle,
                fill="white")

        return image
