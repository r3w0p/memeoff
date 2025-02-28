# Copyright (c) 2021-2025 r3w0p
# The following code can be redistributed and/or
# modified under the terms of the GPL-3.0 License.
import argparse
from shutil import rmtree

from src.functions import *

PATH_TEST: Path = Path(__file__).parent.absolute()

parser = argparse.ArgumentParser()
parser.add_argument("-i", "--image", help="Input image.", type=str)
parser.add_argument("-b", "--batch", help="Command batch.", type=str)
parser.add_argument("-o", "--output", help="Output directory.", type=str)
parser.add_argument("-e", "--emoji", type=str, default=EMOJI_STYLE_APPLE,
                    help=f"Emoji style to use ({', '.join(EMOJI_STYLES_ALL)}).")
args = parser.parse_args()

path_image: Path = PATH_TEST / args.image
print(path_image)

path_batch: Path = PATH_TEST / args.batch
print(path_batch)

batch = open(path_batch).read().splitlines()
formats = get_formats()
emoji_source = emoji_style_to_pilmoji_source_class(args.emoji)

fname = path_image.stem
bname = path_batch.stem

path_output: Path = PATH_TEST / args.output / fname / bname
print(path_output)

if path_output.exists():
    rmtree(str(path_output))
path_output.mkdir(parents=True, exist_ok=True)

# Remove spoiler marks at start and end, if they exist
for i, content in enumerate(batch):
    image = reshape_image(Image.open(path_image))
    image_ftype = image_ftype_from_path(path_image)

    image = process_content(
        image=image,
        content=content,
        formats=formats,
        emoji_source=emoji_source
    )

    image.save(path_output / f"{i + 1}.{image_ftype}")
