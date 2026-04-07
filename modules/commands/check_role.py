import discord
from discord import app_commands
from discord.ext import commands
from modules import utils
from modules import json_reader as js


class CheckRole(commands.Cog):
    def __init__(self, client: commands.Bot):
        self.client = client

    @app_commands.command(name="check_roles", description="A temporary command to check who still needs trainings.")
    async def check_roles(
            interaction: discord.Interaction,
            role: discord.Role
    ):
        message = f""
        await interaction.response.defer(ephemeral=True)
        for member in role.members:
            role_names = [role.name for role in member.roles if role.name != "@everyone"]
            user_ranks_ground = [role for role in js.GROUND_ROLE_HIERARCHY if role in role_names]
            if user_ranks_ground:
                if js.GROUND_ROLE_HIERARCHY.index(user_ranks_ground[0]) >= 3:
                    needed_roles = await utils.check_needed_roles(member)
                    if needed_roles:
                        text = f"{member.display_name} still needs {', '.join(needed_roles)}\n"
                        message += text
                        await interaction.followup.send(f"{member.mention} still needs {', '.join(needed_roles)}'",
                                                        ephemeral=True)
        await interaction.followup.send(f"```{message}```", ephemeral=True)




async def setup(client: commands.Bot):
    await client.add_cog(CheckRole(client))