import datetime
import io
import logging

import aiohttp
import discord
import re
import time
from collections import defaultdict

from config import TEMPBAN_ROLE_NAME, LOGS_CHANNEL_ID
from utils.InviteLogView import InviteLogView
from utils.invite_store import load_invites, save_invites

log = logging.getLogger("bot.message_listener")
INVITE_REGEX = re.compile(r"(discord\.gg/[a-zA-Z0-9]+|discord\.com/invite/[a-zA-Z0-9]+)")

class MessageListener:
    def __init__(self, bot):
        self.bot = bot
        self.user_flags = defaultdict(list)
        self.user_image_flags = defaultdict(list)
        self.known_invites = load_invites()

    async def handle(self, message: discord.Message):
        if message.author.bot:
            return

        if not message.guild:
            return

        member = message.author

        if isinstance(member, discord.Member) and member.guild_permissions.ban_members:
            return

        now = time.time()
        uid = message.author.id

        if message.mention_everyone:
            await self.punish(message, "Everyone ping", "")
            return

        image_count = sum(1 for a in message.attachments if a.content_type and a.content_type.startswith("image/"))

        if image_count >= 4:
            self.user_image_flags[uid].append(now)
            self.user_image_flags[uid] = [t for t in self.user_image_flags[uid] if now - t <= 10]

            if len(self.user_image_flags[uid]) >= 2:
                await self.punish(message, "Image spam", "")
                return

        matches = INVITE_REGEX.findall(message.content)
        if not matches:
            return

        invite = matches[0].replace("https://", "").replace("http://", "")

        self.user_flags[uid].append(now)
        self.user_flags[uid] = [t for t in self.user_flags[uid] if now - t <= 60]

        if invite in self.known_invites:
            await self.punish(message, "Known invite", invite)
            return

        if len(self.user_flags[uid]) >= 2:
            self.known_invites.add(invite)
            save_invites(self.known_invites)

            await self.punish(message, "Invite spam", invite)
            return

    async def punish(self, message: discord.Message, reason: str, invite: str):
        guild = message.guild
        member = message.author

        files = await self._download_attachments(message) if message.attachments else []

        cutoff = discord.utils.utcnow() - datetime.timedelta(seconds=60)

        for channel in guild.text_channels:
            try:
                await channel.purge(limit=100, check=lambda m: m.author.id == member.id, after=cutoff)
            except discord.Forbidden:
                pass
            except discord.HTTPException:
                pass

        temp_role = discord.utils.get(guild.roles, name=TEMPBAN_ROLE_NAME)

        if temp_role:
            try:
                await member.add_roles(temp_role, reason=reason)
            except Exception:
                pass

        if invite != "":
            await self.send_invite_log(message, invite, reason)
        else:
            await self.send_punish_log(message, files, reason)

        for f in files:
            f.fp.close()

    async def _download_attachments(self, message: discord.Message) -> list[discord.File]:
        files = []
        async with aiohttp.ClientSession() as session:
            for attachment in message.attachments:
                try:
                    async with session.get(attachment.url) as resp:
                        if resp.status == 200:
                            data = await resp.read()
                            files.append(discord.File(io.BytesIO(data), filename=attachment.filename))
                except Exception:
                    pass
        return files

    async def send_invite_log(self, message: discord.Message, invite: str, action: str):
        logs_channel = await self.bot.fetch_channel(LOGS_CHANNEL_ID)

        if not logs_channel:
            return

        embed = discord.Embed(title="Invite Detection", description=f"**Action:** {action}", color=discord.Color.red())

        embed.add_field(name="User", value=f"{message.author} ({message.author.id})", inline=False)
        embed.add_field(name="Channel", value=message.channel.mention, inline=False)

        view = InviteLogView(self, invite)

        await logs_channel.send(invite)
        await logs_channel.send(embed=embed, view=view)

    async def send_punish_log(self, message: discord.Message, files: list[discord.File], action: str):
        try:
            logs_channel = await self.bot.fetch_channel(LOGS_CHANNEL_ID)
        except discord.HTTPException:
            log.warning("No access to logs channel: " + str(LOGS_CHANNEL_ID))
            return

        if not logs_channel:
            return

        embed = discord.Embed(title="Scam Detection", description=f"**Action:** {action}", color=discord.Color.red())

        embed.add_field(name="User", value=f"{message.author} ({message.author.id})", inline=False)
        embed.add_field(name="Channel", value=message.channel.mention, inline=False)
        embed.add_field(name="Message Content", value=message.content, inline=False)

        await logs_channel.send(embed=embed, files=files)