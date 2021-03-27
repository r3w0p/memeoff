from textwrap import wrap
from PIL import Image, ImageDraw, ImageOps


class MemeGen:
    I_OFFSET = 2
    I_WORD_WRAP = 26
    I_HEIGHT_PAD = 15
    I_HEIGHT_FORCE = 45

    T_WORD_WRAP = 31
    T_HEIGHT_FORCE = 45
    T_PAD = 15
    T_RADIUS = 60
    T_RADIUS_MULTIPLY = 3

    D_PAD = 3
    DT_HEIGHT_FORCE = 50
    DS_HEIGHT_FORCE = 24

    def __init__(
            self,
            logger,
            font_twitter,
            font_impact,
            font_demot_title,
            font_demot_subtitle) -> None:
        super().__init__()

        self.logger = logger
        self.font_twitter = font_twitter
        self.font_impact = font_impact
        self.font_demot_title = font_demot_title
        self.font_demot_subtitle = font_demot_subtitle

    def apply_format_impact(self, image, list_text, top):
        draw = ImageDraw.Draw(image)

        i_width, i_height = image.size
        text_lines = wrap(
            ' '.join(list_text).upper(),
            width=MemeGen.I_WORD_WRAP)

        for i, text in enumerate(text_lines):
            t_width, t_height = draw.textsize(text, font=self.font_impact)

            x = (i_width - t_width) / 2

            if top:
                y = (i * MemeGen.I_HEIGHT_FORCE)
            else:
                y = (i_height -
                     MemeGen.I_HEIGHT_FORCE -
                     MemeGen.I_HEIGHT_PAD) - \
                    (len(text_lines) - (i + 1)) * \
                    MemeGen.I_HEIGHT_FORCE

            for pos in [
                (x - MemeGen.I_OFFSET, y - MemeGen.I_OFFSET),
                (x + MemeGen.I_OFFSET, y - MemeGen.I_OFFSET),
                (x - MemeGen.I_OFFSET, y + MemeGen.I_OFFSET),
                (x + MemeGen.I_OFFSET, y + MemeGen.I_OFFSET)
            ]:
                draw.text(pos, text, font=self.font_impact, fill="black")

            draw.text((x, y), text, font=self.font_impact, fill="white")

        return image

    def apply_format_twitter(self, image, list_text):
        text_lines = wrap(
            ' '.join(list_text),
            width=MemeGen.T_WORD_WRAP)
        image = MemeGen._add_corners(image, MemeGen.T_RADIUS)

        top = (MemeGen.T_PAD * 2) + \
              (len(text_lines) *
               MemeGen.T_HEIGHT_FORCE)

        border = (MemeGen.T_PAD, top, MemeGen.T_PAD, MemeGen.T_PAD)

        image = ImageOps.expand(image, border=border, fill='white')
        draw = ImageDraw.Draw(image)

        for i, text in enumerate(text_lines):
            x = MemeGen.T_PAD
            y = MemeGen.T_PAD + (i * MemeGen.T_HEIGHT_FORCE)

            draw.text((x, y), text, font=self.font_twitter, fill="black")

        return image

    @staticmethod
    def _add_corners(image, radius):
        # Adapted from: https://stackoverflow.com/a/11291419

        # Temporarily double image size so that corners appear smoother
        # when returned back to its original size
        w_orig, h_orig = image.size
        image = image.resize((w_orig * MemeGen.T_RADIUS_MULTIPLY,
                              h_orig * MemeGen.T_RADIUS_MULTIPLY))
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

    def apply_format_demotivational(
            self, image, list_title=None, list_subtitle=None):
        border_inner = \
            (MemeGen.D_PAD, MemeGen.D_PAD, MemeGen.D_PAD, MemeGen.D_PAD)

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
                    border=(0, 0, 0, 20 if list_title is None else 15),
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

        title_lines = wrap(' '.join(list_title).upper(), width=22)
        title_bottom = len(title_lines) * MemeGen.DT_HEIGHT_FORCE

        image = ImageOps.expand(
            image,
            border=(0, 0, 0, title_bottom),
            fill='black')

        dt_draw = ImageDraw.Draw(image)

        for i, text in enumerate(title_lines):
            t_width, t_height = dt_draw.textsize(
                text, font=self.font_demot_title)

            x = (dt_width - t_width) / 2
            y = dt_height - \
                (MemeGen.DT_HEIGHT_FORCE / 2) + \
                (i * MemeGen.DT_HEIGHT_FORCE)

            dt_draw.text(
                (x, y),
                text,
                font=self.font_demot_title,
                fill="white")

        return image

    def _add_demotivational_subtitle(self, image, list_subtitle):
        ds_width, ds_height = image.size

        subtitle_lines = wrap(' '.join(list_subtitle), width=74)
        subtitle_bottom = len(subtitle_lines) * MemeGen.DS_HEIGHT_FORCE

        image = ImageOps.expand(
            image,
            border=(0, 0, 0, subtitle_bottom),
            fill='black')

        ds_draw = ImageDraw.Draw(image)

        for i, text in enumerate(subtitle_lines):
            t_width, t_height = ds_draw.textsize(
                text, font=self.font_demot_subtitle)

            x = (ds_width - t_width) / 2
            y = ds_height - \
                (MemeGen.DS_HEIGHT_FORCE / 2) + \
                (i * MemeGen.DS_HEIGHT_FORCE)

            ds_draw.text(
                (x, y),
                text,
                font=self.font_demot_subtitle,
                fill="white")

        return image
