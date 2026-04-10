
import discord
from discord import app_commands
from discord.ext import commands
from modules import utils
import datetime
from modules.ui import confirm_view



class bct_check(commands.Cog):
    def __init__(self, client: commands.Bot):
        self.client = client

    @app_commands.command(name="bct_check",description="Checks if people need to be kicked cause they haven't signed up.")
    async def bct_check(
            self,
        interaction = discord.Interaction
    ):
        if not await utils.admin_check(interaction):
            return
        await interaction.response.defer(ephemeral=True)
        await interaction.followup.send("Checking users...",ephemeral=True)
        list_of_members_to_kick = []
        guild = interaction.guild
        guild_members = guild.members
        for member in guild_members:
            if await utils.check_needed_roles(member,["Member"]):
                join_date = member.joined_at
                now = datetime.datetime.now(datetime.timezone.utc)
                two_months_ago = now - datetime.timedelta(days=60)
                if join_date < two_months_ago:
                    list_of_members_to_kick.append(member)
        if not list_of_members_to_kick:
            await interaction.followup.send(f"No people to review",ephemeral=True)
            return
        for member_to_kick in list_of_members_to_kick:
            timestamp = int(member_to_kick.joined_at.timestamp())

            view = confirm_view.ConfirmView(
                "Kick",
                "Skip"
            )
            await interaction.followup.send(
                content=(
                    f"**Review member**\n"
                    f"{member_to_kick.mention}\n"
                    f"Joined <t:{timestamp}:R> \n\n"
                    f"Kick this member?"
                ),
                view=view,
                ephemeral=True
            )

            await view.wait()

            if view.value is True:
                await member_to_kick.kick(reason="You have been on the 56ths Discord for longer than a month without getting started, rejoin if you are still interested.")
                await interaction.followup.send(f'{member_to_kick.mention} has been kicked',ephemeral=True)
            if view.value is False:
                await interaction.followup.send(f"Not kicking {member_to_kick.mention}",ephemeral=True)
            await interaction.followup.send(f"Done checking !", ephemeral=True)


async def setup(client: commands.Bot):
    await client.add_cog(bct_check(client))






