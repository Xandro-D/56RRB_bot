import discord
from discord import app_commands
from discord.ext import commands
from modules import utils



class BctTraining(commands.Cog):
    def __init__(self, client: commands.Bot):
        self.client = client

    @app_commands.command(name="bct_training",
                         description="Send a private message to everyone who still needs a bct.")
    async def bct_training(
            self,
            interaction: discord.Interaction,
    ):
        await interaction.response.defer()
        if not await utils.admin_check(interaction):
            return
        guild = interaction.guild
        members = guild.members
        success_list = []
        fail_list = []
        for member in members:
            if not await utils.check_needed_roles(member, ["Waiting for BCT"]):
                try:
                    await member.send(
                        f'Hello, you have joined the 56th RRB. To be able to join OPs follow the installation guide and request a BCT https://discord.com/channels/1090564451201196122/1346494156410716281.')
                    success_list.append(member.display_name)
                except:
                    fail_list.append(member.display_name)
        if success_list:
            await interaction.followup.send(
                "These users have been sent a DM:\n```"
                + "\n".join(success_list)
                + "```"
            )

        if fail_list:
            await interaction.followup.send(
                "These users have **not** been sent a DM:\n```"
                + "\n".join(fail_list)
                + "```"
            )


async def setup(client: commands.Bot):
    await client.add_cog(BctTraining(client))