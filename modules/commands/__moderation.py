import discord
from discord import app_commands
from discord.ext import commands
from modules import utils
from modules import database

db = database.ModerationDatabase()


class Moderation(commands.Cog):
    def __init__(self, client: commands.Bot):
        self.client = client

    @app_commands.command(
        name="strike",
        description="Strike a person, strikes last 6 months.",
    )
    async def strike(self,interaction: discord.Interaction, target: discord.Member, reason: str):
        if await utils.admin_check(interaction):
            db.add_strike(target.id, 15778463)
            if db.get_strikes(target.id) < 3:
                await interaction.response.send_message(
                    f"{target.display_name} has been struck and now has {db.get_strikes(target.id)} strikes."
                    f"\nreason:```{reason}```"
                )
            else:
                await interaction.response.send_message(
                    f"{target.display_name} has three or more strikes and should be banned, get em boys."
                    f"\nreason:```{reason}```"
                )
    @app_commands.command(name="remove_strike", description="Removes 1 strike from a person")
    async def remove_strike(self,interaction: discord.Interaction, target: discord.Member):
        if await utils.admin_check(interaction):
             if db.get_strikes(target.id) > 0:
                db.remove_strike(target.id)
                await interaction.response.send_message(
                      f"{target.display_name} now has {db.get_strikes(target.id)} strikes."
                )
             else:
                await interaction.response.send_message(
                    f"{target.display_name} has no strikes to remove."

                )

    @app_commands.command(name="reset", description="Resets a persons strikes and warns")
    async def reset(self,interaction: discord.Interaction, target: discord.Member):
        if await utils.admin_check(interaction):
            db.reset_strikes(target.id)
            db.reset_warnings(target.id)
            await interaction.response.send_message(f"{target.display_name} has been reset.")

    app_commands.command(name="warn", description="Gives 1 warning to a person, warnings last until a strike.")
    async def warn(self,interaction: discord.Interaction, target: discord.Member, reason: str):
        if await utils.admin_check(interaction):
            if db.get_warnings(target.id) <= 4:
                db.add_warning(target.id)
                await interaction.response.send_message(f"{target.display_name} has been warned."
                                                        f"\nreason:```{reason}```")
            else:
                db.reset_warnings(target.id)
                db.add_strike(target.id, duration_seconds=15778463)
                message = (f"{target.display_name} has 4 or more warnings and has been struck. "
                           f"Now he has {db.get_strikes(target.id)} strikes and {db.get_warnings(target.id)} warns."
                           f"\nreason:```{reason}```")
                await interaction.response.send_message(message)

    @app_commands.command(name="remove_warn", description="Removes 1 warning from a person.")
    async def remove_warn(self,interaction: discord.Interaction, target: discord.Member):
        if await utils.admin_check(interaction):
            if db.get_warnings(target.id) > 0:
                db.remove_warning(target.id)
                await interaction.response.send_message(
                    f"{target.display_name} now has {db.get_warnings(target.id)} warnings."
                )
            else:
                await interaction.response.send_message(
                    f"{target.display_name} has no warnings to remove."
                )

    @app_commands.command(name="info", description="displays")
    async def info(self,interaction: discord.Interaction, target: discord.Member):
        strikes = db.get_strikes(target.id)
        warnings = db.get_warnings(target.id)
        await interaction.response.send_message(f"{target.display_name} has {strikes} strikes and {warnings} warnings.")


async def setup(client: commands.Bot):
    await client.add_cog(Moderation(client))