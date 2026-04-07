import asyncio
import discord
from discord.ext import commands, tasks
import a2s
from pyparsing import conditionAsParseAction

from modules import config

SERVER_IP = config.server_ip       # move to config later
SERVER_PORT = config.server_port
CHANNEL_NAME = "server-status"


class ServerStatus(commands.Cog):
    def __init__(self, client: commands.Bot):
        self.client = client
        self.server_status_message: discord.Message | None = None
        self.server_status_loop.start()

    def cog_unload(self):
        self.server_status_loop.cancel()

    def get_data(self, server_ip: str, server_port: int):
        server_address = (server_ip, server_port)
        info = a2s.info(server_address)
        players = a2s.players(server_address)
        return info, players

    @tasks.loop(minutes=10)
    async def server_status_loop(self):
        # wait until bot is fully ready
        if not self.client.is_ready():
            return

        if self.server_status_message is None:
            channel = discord.utils.get(self.client.get_all_channels(), name=CHANNEL_NAME)
            if channel is None:
                print("Error: 'server-status' channel not found!")
                return
            self.server_status_message = await channel.send("Getting server status...")

        try:
            # a2s is blocking; run in thread so bot loop doesn't freeze
            info, players = await asyncio.to_thread(self.get_data, SERVER_IP, SERVER_PORT)

            embed = discord.Embed(
                title="Server Status",
                description="Online!",
                color=discord.Color.green(),
                timestamp=discord.utils.utcnow(),
            )

            if players:
                player_list = "\n".join(f"• {p.name}" for p in players)
                embed.add_field(name=f"Players Online ({len(players)})", value=player_list, inline=False)
            else:
                embed.add_field(name="Players Online", value="*No players online*", inline=False)

            embed.add_field(name="Mission", value=info.game or "Unknown", inline=False)
            embed.set_footer(text="Last updated")

            await self.server_status_message.edit(content=None, embed=embed)

        except Exception as e:
            error_embed = discord.Embed(
                title="Server Status",
                description="Could not connect to server",
                color=discord.Color.red(),
                timestamp=discord.utils.utcnow(),
            )
            error_embed.set_footer(text=f"Error: {e}")
            await self.server_status_message.edit(content=None, embed=error_embed)

    @server_status_loop.before_loop
    async def before_server_status_loop(self):
        await self.client.wait_until_ready()


async def setup(client: commands.Bot):
    await client.add_cog(ServerStatus(client))