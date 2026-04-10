import discord
from discord import app_commands
from discord.ext import commands
from modules import utils
from modules import googleapi as google



class Sheet(commands.Cog):
    def __init__(self, client: commands.Bot):
        self.client = client

    @app_commands.command(name="sheet",description="Update the google spreadsheet information.")
    async def sheet(
            self,
            interaction:discord.Interaction,
    ):
        await interaction.response.defer(ephemeral=True)
        if await utils.admin_check(interaction):
            author = interaction.user
            bravo_role = discord.utils.get(author.guild.roles, name="bravo squadmember")
            charlie_role = discord.utils.get(author.guild.roles, name="charlie squadmember")
            bravo_members = bravo_role.members
            charlie_members = charlie_role.members
            roles_to_display = ["Combat Life Saver", "Anti Tank", "Combat Engineer","International Scientific Group"]
            sheet_data = [["Bravo", "Combat Life Saver", "Anti Tank", "Combat Engineer","International Scientific Group"]]  # Header row

            for member in bravo_members:
                member_row = [member.display_name]
                member_roles_names = [role.name for role in member.roles if role.name != "@everyone"]

                for role in roles_to_display:
                    if role in member_roles_names:
                        member_row.append("✅")
                    else:
                        member_row.append("❌")

                sheet_data.append(member_row)
            sheet_data.append(["Charlie", "Combat Life Saver", "Anti Tank","Combat Engineer","International Scientific Group"])
            for member in charlie_members:
                member_row = [member.display_name]
                member_roles_names = [role.name for role in member.roles if role.name != "@everyone"]

                for role in roles_to_display:
                    if role in member_roles_names:
                        member_row.append("✅")
                    else:
                        member_row.append("❌")

                sheet_data.append(member_row)
            lines_update = google.sheets(sheet_data)
            await interaction.followup.send(f"{lines_update} lines where updated.", ephemeral=True)


async def setup(client: commands.Bot):
    await client.add_cog(Sheet(client))