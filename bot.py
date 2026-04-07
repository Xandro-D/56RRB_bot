import asyncio
from pathlib import Path
import discord
from discord.ext import commands
from discord import app_commands
import modules.config as cfg


intents = discord.Intents.default()
intents.message_content = True
intents.guilds = True
intents.members = True

class MyClient(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix="!", intents=intents)

    async def setup_hook(self):
        await load_modules(self)  # load cogs/extensions first
        guild = discord.Object(id=cfg.GUILD_ID)
        self.tree.copy_global_to(guild=guild)
        await self.tree.sync(guild=guild)


client = MyClient()


async def load_modules(bot: commands.Bot):
    cogs_dir = Path(__file__).resolve().parent / "modules" / "commands"

    if not cogs_dir.exists():
        print("cogs folder not found")
        return

    for file in cogs_dir.glob("*.py"):
        if file.name.startswith("_"):
            continue

        extension = f"modules.commands.{file.stem}"
        try:
            await bot.load_extension(extension)
            print(f"Loaded {extension}")
        except Exception as e:
            print(f"Failed to load {extension}: {e}")

@client.event
async def on_ready():
    print(f"Logged in as {client.user} ({client.user.id})")





async def main():
    await client.start(cfg.bot_token)

@client.tree.error
async def on_app_command_error(interaction: discord.Interaction, error: app_commands.AppCommandError):
    print(f"App command error: {error}")
    if interaction.response.is_done():
        await interaction.followup.send(f"Error: {error}", ephemeral=True)
    else:
        await interaction.response.send_message(f"Error: {error}", ephemeral=True)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Closing...")