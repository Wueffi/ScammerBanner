import discord
from discord.ext import commands
import asyncio
import logging

import utils.guild_setup
from config import BOT_TOKEN
from utils.VerificationView import VerificationView
from utils.message_listener import MessageListener, InviteLogView

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  [%(levelname)s]  %(name)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
log = logging.getLogger("bot")


intents = discord.Intents.default()
intents.members = True
intents.message_content = True


class ScammerBanner(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix=commands.when_mentioned,intents=intents)
        self.listener = MessageListener(self)

    async def on_ready(self):
        log.info("Logged in as %s (ID: %s)", self.user, self.user.id)
        log.info("Connected to %d guild(s)", len(self.guilds))
        self.add_view(InviteLogView(listener=self.listener, invite=""))
        self.add_view(VerificationView())
        for guild in self.guilds:
            role = await utils.guild_setup.setupRole(guild)
            await utils.guild_setup.setupChannel(guild, role)
            await utils.guild_setup.setupPerms(guild, role)
        await self.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name="Looking for rule breakers!"))

    async def on_guild_join(self, guild):
        role = await utils.guild_setup.setupRole(guild)
        await utils.guild_setup.setupChannel(guild, role)
        await utils.guild_setup.setupPerms(guild, role)

    async def on_message(self, message: discord.Message):
        await self.listener.handle(message)
        await self.process_commands(message)

async def main():
    async with ScammerBanner() as bot:
        await bot.start(BOT_TOKEN)



if __name__ == "__main__":
    asyncio.run(main())