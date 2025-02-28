# Copyright (c) 2021-2025 r3w0p
# The following code can be redistributed and/or
# modified under the terms of the GPL-3.0 License.
import asyncio
from io import BytesIO
from time import time_ns
from typing import Optional

import discord
from discord.app_commands import CommandTree

from src.functions import *


def get_client(args) -> discord.Client:
    intents = discord.Intents.all()
    client = discord.Client(intents=intents)
    formats: Dict[str, MemeFormat] = get_formats()
    tree: Optional[CommandTree] = None
    emoji_source = emoji_style_to_pilmoji_source_class(args.emoji)

    # Enable slash commands with Guild ID (optional)
    if args.guild is not None:
        tree = CommandTree(client)
        desc = f"{NAME_MEMEOFF.title()}: {', '.join(SLASH_MEMEOFF_OPTIONS)}"

        @tree.command(
            name=NAME_MEMEOFF,
            description=desc,
            guild=discord.Object(id=args.guild)
        )
        async def memeoff(interaction, message: str):
            if message.lower() == SLASH_MEMEOFF_HELP:
                await interaction.response.send_message(MEMEOFF_URL_WIKI)

            elif message.lower() == SLASH_MEMEOFF_VERSION:
                await interaction.response.send_message(f"v{MEMEOFF_VERSION}")

            else:
                await interaction.response.send_message(
                    f"/{NAME_MEMEOFF} command accepts the following messages: "
                    f"{', '.join(SLASH_MEMEOFF_OPTIONS)}")

    @client.event
    async def on_ready():
        print(f"Logged in as: {client.user}")

        if args.guild is not None:
            await tree.sync(guild=discord.Object(id=args.guild))
            print("Guild ID provided")

    @client.event
    async def on_message_edit(before, after):
        await on_message(after)

    @client.event
    async def on_message(message):
        if message.author == client.user:
            return

        # If message contains any of the recognised slash triggers
        if contains_memeoff_format(message.content):
            try:
                await handle_message(message)
            except Exception as e:
                err_msg = await message.channel.send(e, reference=message)
                await asyncio.sleep(SLEEP_ERROR_MINOR)

                try:
                    await err_msg.delete()
                except discord.errors.NotFound:
                    pass  # user deleted it before program could

                try:
                    await message.delete()
                except discord.errors.NotFound:
                    pass  # user deleted it before program could

    async def handle_message(message):
        if not message_has_image_reference(message):
            raise MinorMemeoffError("Image not provided.")

        image, image_ftype = await download_image_from_message(message)

        if image_ftype not in SUPPORTED_FILE_TYPES:
            raise MinorMemeoffError(
                f"Image file type '{image_ftype}' is not supported.")

        content: str = message.content

        # Options
        anonymous: bool = (
                args.force_anon or
                (not args.disable_anon and COMMAND_ANON in content)
        )

        image = process_content(
            image=image,
            content=content,
            formats=formats,
            emoji_source=emoji_source
        )

        # Send response
        with BytesIO() as image_binary:
            image.save(image_binary, image_ftype)
            image_binary.seek(0)

            await message.channel.send(
                message.author.mention if not anonymous else "",
                file=discord.File(
                    fp=image_binary,
                    filename=f"{time_ns()}.{image_ftype}"
                ),
                reference=(  # maybe send as reply if provided own image
                    message.reference if len(message.attachments) > 0
                    else None
                )
            )

        # Delete trigger message on success
        try:
            await message.delete()
        except discord.errors.NotFound:
            pass  # user deleted it before program could

    return client
