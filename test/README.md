# `test.py`

A script that quickly generates a batch of images without having to manually
test them all on Discord.

**It does not currently support Emojis!**

In this directory, use the following directory structure:

- `images`, a directory of images that you want to format
- `batches`, a directory containing files that have formatting commands,
  one per line, equivalent to what you would type in Discord

When running `test.py`, provide the following commands:

- `--image "images/myimage.png"`, the image you want to format
- `--batch "batches/demotiv.txt`, the commands to use against this image

This will output all images to `output/demotiv/myimage`.
