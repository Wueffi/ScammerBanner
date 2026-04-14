from __future__ import annotations

import logging
import discord

from config import (TEMPBAN_ROLE_NAME, TEMPBAN_ROLE_COLOUR, TEMPBAN_CHANNEL_NAME, TEMPBAN_CHANNEL_WELCOME)
from utils.VerificationView import VerificationView

log = logging.getLogger("bot.guild_setup")

async def setupRole(guild: discord.Guild) -> discord.Role:
    existing = discord.utils.get(guild.roles, name=TEMPBAN_ROLE_NAME)
    if existing:
        return existing

    role = await guild.create_role(name=TEMPBAN_ROLE_NAME, colour=discord.Colour(TEMPBAN_ROLE_COLOUR), hoist=False, mentionable=False,reason="Automatically created temp ban role"
    )

    return role

async def setupChannel(guild: discord.Guild, tempban_role: discord.Role) -> discord.TextChannel:
    name_raw = TEMPBAN_CHANNEL_NAME.lstrip("🔒")

    channel = discord.utils.get(guild.text_channels, name=name_raw) or discord.utils.get(guild.text_channels, name=TEMPBAN_CHANNEL_NAME)
    overwrites = _build_overwrites(guild, tempban_role)

    if channel:
        await channel.edit(overwrites=overwrites, reason="Sync tempban channel permissions")
    else:
        channel = await guild.create_text_channel(name=TEMPBAN_CHANNEL_NAME, overwrites=overwrites, topic="Temporary bans channel.", reason="Created tempban channel")

        try:
            view = VerificationView()
            await channel.send(TEMPBAN_CHANNEL_WELCOME, view=view)

        except discord.Forbidden:
            log.warning("Cannot send welcome message in tempban channel")

    return channel

async def setupPerms(guild: discord.Guild, tempban_role: discord.Role) -> None:
    for channel in guild.channels:
        if not isinstance(channel,(discord.TextChannel, discord.VoiceChannel, discord.StageChannel, discord.ForumChannel)):
            continue

        if channel.name in (TEMPBAN_CHANNEL_NAME, TEMPBAN_CHANNEL_NAME.lstrip("🔒")):
            continue

        overwrites = channel.overwrites_for(tempban_role)
        if overwrites.view_channel is False:
            continue

        try:
            await channel.set_permissions(tempban_role, view_channel=False, reason="Hide channel from tempbanned users")
        except discord.Forbidden:
            log.warning("Missing permission to edit %s in %s", channel.name, guild.name)

def _build_overwrites(guild: discord.Guild, tempban_role: discord.Role) -> dict[discord.Role | discord.Member, discord.PermissionOverwrite]:
    return {
        guild.default_role: discord.PermissionOverwrite(view_channel=False),
        tempban_role: discord.PermissionOverwrite(view_channel=True, send_messages=False, read_message_history=True),
        guild.me: discord.PermissionOverwrite(view_channel=True, send_messages=True, read_message_history=True)
    }