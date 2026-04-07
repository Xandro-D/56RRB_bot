import random
import discord
from discord.app_commands import commands
from modules import utils
from modules import json_reader


class factcheck(commands.Cog):
        def __init__(self, client:discord.Client):
            self.client = client

        @app_commands.command(
            name="factcheck",
            description="The silly factcheck, totally fair and all knowing.",
        )
        async def factcheck(self, interaction: discord.Interaction):
            if await utils.admin_check(interaction):
                await interaction.response.send_message(random.choice(json_reader.SILLY_FACT_CHECK_POSITIVE))
            else:
                await interaction.response.send_message(random.choice(json_reader.SILLY_FACT_CHECK_NEGATIVE))


async def setup(client:commands.client):
    await client.add_cog(factcheck(client))