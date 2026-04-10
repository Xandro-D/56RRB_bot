import discord
from discord import app_commands
from discord.ext import commands


class WhoIsIn(commands.Cog):
    def __init__(self, client: commands.Bot):
        self.client = client

    @app_commands.command(name="whoisin", description="Dm's a list of people who are in either of the asked for roles.")
    async def whoisin(
            self,
            interaction: discord.Interaction,
            role1: discord.Role,
            role2: discord.Role = None,
            role3: discord.Role = None,
    ):
        user_count = 0
        await interaction.response.defer(ephemeral=True)
        roles = [role1, role2, role3]
        for role in roles:
            if not role:
                break
            else:
                member_list = [f"The following people are in {role.mention}"]
                members = role.members
                for member in members:
                    user_count = user_count + 1
                    member_list.append(f"{member.mention}")
                member_list.append(f"For a total of {user_count} people.")
                await interaction.followup.send("\n".join(member_list), ephemeral=True)
                user_count = 0

    @app_commands.command(name="whoisinboth", description="Dms a list of people who are in both role1 and role2.")
    async def whoisinboth(
            self,
            interaction: discord.Interaction,
            role1: discord.Role,
            role2: discord.Role,
    ):
        await interaction.response.defer(ephemeral=True)
        user_count: int = 0
        member_list1 = role1.members
        member_list2 = role2.members
        member_list_final = [f'The following people are in both {role1.mention} and {role2.mention}.']
        for member in member_list1:
            if member in member_list2:
                user_count += 1
                member_list_final.append(f"{member.mention}")
                # await user.send(f"**{member.display_name}** has: {role1.name} and {role2.name}")
        member_list_final.append(f"For a total of {user_count} people.")
        await interaction.followup.send("\n".join(member_list_final), ephemeral=True)



async def setup(client: commands.Bot):
    await client.add_cog(WhoIsIn(client))