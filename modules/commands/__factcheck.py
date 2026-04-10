import discord
from discord import app_commands
from discord.ext import commands
from modules import utils
from modules import json_reader
import random


class FactCheck(commands.Cog):
    def __init__(self, client: commands.Bot):
        self.client = client

    @app_commands.command(
        name="factcheck",
        description="The silly factcheck, totally fair and all knowing.",
    )
    async def factcheck(self, interaction: discord.Interaction):
        if await utils.admin_check(interaction):
            await interaction.response.send_message(
                random.choice(json_reader.SILLY_FACT_CHECK_POSITIVE)
            )
            interaction.response()
        else:
            await interaction.response.send_message(
                random.choice(json_reader.SILLY_FACT_CHECK_NEGATIVE)
            )


async def setup(client: commands.Bot):
    await client.add_cog(FactCheck(client))