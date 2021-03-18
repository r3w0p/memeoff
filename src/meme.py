from textwrap import wrap
from PIL import Image, ImageDraw, ImageOps


class MemeGenerator:
    I_COLOUR_SHADOW = "black"
    I_COLOUR_FILL = "white"
    I_OFFSET = 2
    I_WIDTH_WRAP = 26
    I_HEIGHT_PAD = 15
    I_HEIGHT_FORCE = 45

    T_COLOUR_FILL = "black"
    T_WIDTH_WRAP = 28
    T_HEIGHT_FORCE = 45
    T_PAD = 15
    T_RADIUS = 60
    T_RADIUS_MULTIPLY = 3

    def __init__(
            self,
            logger_meme,
            font_twitter,
            font_impact) -> None:
        super().__init__()

        self.logger_meme = logger_meme
        self.font_twitter = font_twitter
        self.font_impact = font_impact

    def apply_format_impact(self, image, list_text, top):
        draw = ImageDraw.Draw(image)

        i_width, i_height = image.size
        text_lines = wrap(
            ' '.join(list_text),
            width=MemeGenerator.I_WIDTH_WRAP)

        for i, text in enumerate(text_lines):
            t_width, t_height = draw.textsize(text, font=self.font_impact)

            x = (i_width - t_width) / 2

            if top:
                y = (i * MemeGenerator.I_HEIGHT_FORCE)
            else:
                y = (i_height -
                     MemeGenerator.I_HEIGHT_FORCE -
                     MemeGenerator.I_HEIGHT_PAD) - \
                    (len(text_lines) - (i + 1)) *\
                    MemeGenerator.I_HEIGHT_FORCE

            for pos in [
                (x - MemeGenerator.I_OFFSET, y - MemeGenerator.I_OFFSET),
                (x + MemeGenerator.I_OFFSET, y - MemeGenerator.I_OFFSET),
                (x - MemeGenerator.I_OFFSET, y + MemeGenerator.I_OFFSET),
                (x + MemeGenerator.I_OFFSET, y + MemeGenerator.I_OFFSET)
            ]:
                draw.text(pos,
                          text,
                          font=self.font_impact,
                          fill=MemeGenerator.I_COLOUR_SHADOW)

            draw.text((x, y),
                      text,
                      font=self.font_impact,
                      fill=MemeGenerator.I_COLOUR_FILL)

        return image

    def apply_format_twitter(self, image, list_text):
        text_lines = wrap(
            ' '.join(list_text),
            width=MemeGenerator.T_WIDTH_WRAP)
        image = MemeGenerator._add_corners(image, MemeGenerator.T_RADIUS)

        top = (MemeGenerator.T_PAD * 2) + \
              (len(text_lines) *
               MemeGenerator.T_HEIGHT_FORCE)

        border = (MemeGenerator.T_PAD,
                  top,
                  MemeGenerator.T_PAD,
                  MemeGenerator.T_PAD)

        image = ImageOps.expand(image, border=border, fill='white')
        draw = ImageDraw.Draw(image)

        for i, text in enumerate(text_lines):
            x = MemeGenerator.T_PAD
            y = MemeGenerator.T_PAD + (i * MemeGenerator.T_HEIGHT_FORCE)

            draw.text((x, y),
                      text,
                      font=self.font_twitter,
                      fill=MemeGenerator.T_COLOUR_FILL)

        return image

    @staticmethod
    def _add_corners(image, radius):
        # Adapted from: https://stackoverflow.com/a/11291419

        # Temporarily double image size so that corners appear smoother when
        # returned back to its original size
        w_orig, h_orig = image.size
        image = image.resize((w_orig * MemeGenerator.T_RADIUS_MULTIPLY,
                              h_orig * MemeGenerator.T_RADIUS_MULTIPLY))
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
