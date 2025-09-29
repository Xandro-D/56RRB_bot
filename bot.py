import random
import os
import discord
from aiohttp import payload
from discord import app_commands
from pyexpat.errors import messages

from database import ModerationDatabase
import json
from dotenv import load_dotenv


db = ModerationDatabase()

with open("hierarchy.json", "r") as f:
    data = json.load(f)

# assign variables from json file
GROUND_ROLE_HIERARCHY = data["GROUND_ROLE_HIERARCHY"]
GROUND_ROLE_PREFIX = data["GROUND_ROLE_PREFIX"]
NCO_ROLE_HIERARCHY = data["NCO_ROLE_HIERARCHY"]
NCO_ROLE_PREFIX = data["NCO_ROLE_PREFIX"]
AIR_ROLE_HIERARCHY = data["AIR_ROLE_HIERARCHY"]
AIR_ROLE_PREFIX = data["AIR_ROLE_PREFIX"]
ARMOR_ROLE_HIERARCHY = data["ARMOR_ROLE_HIERARCHY"]
ARMOR_ROLE_PREFIX = data["ARMOR_ROLE_PREFIX"]
AUTHORIZED_ROLES = data["AUTHORIZED_ROLES"]
SILLY_FACT_CHECK_POSITIVE = data["SILLY_FACT_CHECK_POSITIVE"]
SILLY_FACT_CHECK_NEGATIVE = data["SILLY_FACT_CHECK_NEGATIVE"]

# Initializing discord bot
load_dotenv()
intents = discord.Intents.default()
intents.message_content = True
intents.guilds = True
intents.members = True  # Needed to access member roles
PREFIX = "!"

GUILD_ID = os.getenv("DISCORD_GUILD_ID")
bot_token = os.getenv("DISCORD_BOT_TOKEN")
discord_msg_id = int(os.getenv("DISCORD_MSG_ID"))


# ---------- Client Subclass ----------
class MyClient(discord.Client):
    def __init__(self):
        super().__init__(intents=intents)
        self.tree = app_commands.CommandTree(self)

    async def setup_hook(self):
        # Sync slash commands to a specific guild for quick iteration
        guild = discord.Object(id=GUILD_ID)
        self.tree.copy_global_to(guild=guild)
        await self.tree.sync(guild=guild)


client = MyClient()


# Admin check, check if user has any roles in the authorized roles list
async def admin_check(interaction):
    author = interaction.user
    # Check if they have a role named "Admin"
    if any(role.name in AUTHORIZED_ROLES for role in author.roles):
        return True
    else:
        await interaction.response.send_message("You are not authorized to use this command")
        return False

# Silly fact check commands, checks if user has an authorized role and response positively if they do.


@client.tree.command(name="factcheck", description="The silly factcheck, totally fair and all knowing.")
async def factcheck(interaction: discord.Interaction):
    author = interaction.user
    # Check if they have a role named "Admin"
    if any(role.name in AUTHORIZED_ROLES for role in author.roles):
        await interaction.response.send_message(random.choice(SILLY_FACT_CHECK_POSITIVE))
    else:
        await interaction.response.send_message(random.choice(SILLY_FACT_CHECK_NEGATIVE))

# Start of the promote command


@client.tree.command(name="promote", description="Promotes users mentioned in the arguments.")
async def promote(
        interaction: discord.Interaction,
        target1: discord.Member,
        target2: discord.Member = None,
        target3: discord.Member = None,
        target4: discord.Member = None,
        target5: discord.Member = None,
        target6: discord.Member = None,
        target7: discord.Member = None,
        target8: discord.Member = None,
        target9: discord.Member = None,
        target10: discord.Member = None
):
    await interaction.response.defer()
    targets_unfiltered = [target1, target2, target3, target4, target5, target6, target7, target8, target9, target10]
    targets = [t for t in targets_unfiltered if t is not None]
    if await admin_check(interaction):
        for target in targets:
            role_names = [role.name for role in target.roles if role.name != "@everyone"]
            user_ranks_ground = [role for role in GROUND_ROLE_HIERARCHY if role in role_names]
            nco_ranks = [role for role in NCO_ROLE_HIERARCHY if role in role_names]
            air_ranks = [role for role in AIR_ROLE_HIERARCHY if role in role_names]
            armor_ranks = [role for role in ARMOR_ROLE_HIERARCHY if role in role_names]
            if user_ranks_ground:
                branch = GROUND_ROLE_HIERARCHY
                prefix_type = GROUND_ROLE_PREFIX
                await promotion(user_ranks_ground, target, branch, prefix_type, interaction)
            if nco_ranks:
                branch = NCO_ROLE_HIERARCHY
                prefix_type = NCO_ROLE_PREFIX
                await promotion(nco_ranks, target, branch, prefix_type, interaction)
            if air_ranks:
                branch = AIR_ROLE_HIERARCHY
                prefix_type = AIR_ROLE_PREFIX
                await promotion(air_ranks, target, branch, prefix_type, interaction)
            if armor_ranks:
                branch = ARMOR_ROLE_HIERARCHY
                prefix_type = ARMOR_ROLE_PREFIX
                await promotion(armor_ranks, target, branch, prefix_type, interaction)
        await interaction.followup.send("I am done :)")


async def promotion(ranks, target, branch, prefix_type, interaction):
    current_index = branch.index(ranks[0])
    next_index = current_index + 1
    if next_index < len(branch):
        # Get the name of the current rank and next rank, then search up the corresponding role
        current_rank_name = branch[current_index]
        next_rank_name = branch[next_index]
        current_role = discord.utils.get(target.guild.roles, name=current_rank_name)
        next_role = discord.utils.get(target.guild.roles, name=next_rank_name)
        author = interaction.user
        # Add the next role (promotion) and remove the cleanup.
        await target.add_roles(next_role)
        await target.remove_roles(current_role)
        # Get the prefix for the current role IE PFC.
        # Split the current username by the Space inbetween the prefix and nickname, thn replace the prefix.
        new_prefix = prefix_type[next_index]
        nickname = target.display_name
        nickname_parts = nickname.split(' ', 1)
        # nickname_parts [0] PFC
        # nickname_parts[1] User
        new_nickname = new_prefix + " " + nickname_parts[1]
        await target.edit(nick=new_nickname)
        await interaction.channel.send(
            "Congrats " + target.mention + " you got promoted from " + str(current_rank_name) +
            " to " + str(next_rank_name) + " by " + author.mention
        )
    else:
        await interaction.channel.send(target.display_name + " is already the highest rank in his/her branch")

# End of promotion command

# Start of moderation commands
# Strike command


@client.tree.command(name="strike", description="Strike a person, strikes last 6 months.")
async def strike(interaction: discord.Interaction, target: discord.Member):
    if await admin_check(interaction):
        db.add_strike(target.id, 15778463)
        if db.get_strikes(target.id) < 3:
            await interaction.response.send_message(
                f"{target.display_name} has been struck and now has {db.get_strikes(target.id)} strikes."
            )
        else:
            await interaction.response.send_message(
                f"{target.display_name} has three or more strikes and should be banned, get em boys."
            )


@client.tree.command(name="remove_strike", description="Removes 1 strike from a person")
async def remove_strike(interaction: discord.Interaction, target: discord.Member):
    if await admin_check(interaction):
        if db.get_strikes(target.id) > 0:
            db.remove_strike(target.id)
            await interaction.response.send_message(
                f"{target.display_name} now has {db.get_strikes(target.id)} strikes."
            )
        else:
            await interaction.response.send_message(
                f"{target.display_name} has no strikes to remove."
            )
# End of strike commands
# Warn commands


@client.tree.command(name="warn", description="Gives 1 warning to a person, warnings last until a strike.")
async def warn(interaction: discord.Interaction, target: discord.Member):
    if await admin_check(interaction):
        if db.get_warnings(target.id) < 2:
            db.add_warning(target.id)
            await interaction.response.send_message(f"{target.display_name} has been warned.")
        else:
            db.reset_warnings(target.id)
            db.add_strike(target.id, 15778463)
            message = (f"{target.display_name} has 2 or more warnings and has been struck. "
                       f"Now he has {db.get_strikes(target.id)} strikes and {db.get_warnings(target.id)} warns.")
            await interaction.response.send_message(message)


@client.tree.command(name="remove_warn", description="Removes 1 warning from a person.")
async def remove_warn(interaction: discord.Interaction, target: discord.Member):
    if await admin_check(interaction):
        if db.get_warnings(target.id) > 0:
            db.remove_warning(target.id)
            await interaction.response.send_message(
                f"{target.display_name} now has {db.get_warnings(target.id)} warnings."
            )
        else:
            await interaction.response.send_message(
                f"{target.display_name} has no warnings to remove."
            )


@client.tree.command(name="info", description="displays")
async def info(interaction: discord.Interaction, target: discord.Member):
    strikes = db.get_strikes(target.id)
    warnings = db.get_warnings(target.id)
    await interaction.response.send_message(f"{target.display_name} has {strikes} strikes and {warnings} warnings.")


@client.tree.command(name="reset", description="Resets a persons strikes and warns")
async def reset(interaction: discord.Interaction, target: discord.Member):
    if await admin_check(interaction):
        db.reset_strikes(target.id)
        db.reset_warnings(target.id)
        await interaction.response.send_message(f"{target.display_name} has been reset.")


@client.tree.error
async def on_app_command_error(interaction: discord.Interaction, error: app_commands.AppCommandError):
    if isinstance(error, app_commands.CommandInvokeError):
        await interaction.response.send_message("Something went wrong in the command.", ephemeral=True)
    else:
        await interaction.response.send_message(f"Error: {error}", ephemeral=True)
@client.event
async def on_raw_reaction_add(payload: discord.RawReactionActionEvent):
    db.remove_expired_role_cooldown()
    if payload.message_id == client.user.id:
        return
    if payload.message_id == discord_msg_id:
        cooldown = db.get_role_cooldown(payload.user_id)
        cooldown_time = db.get_role_cooldown_remaining(payload.user_id)
        print(cooldown_time)
        guild = client.get_guild(payload.guild_id)
        channel = guild.get_channel(payload.channel_id) or await guild.fetch_channel(payload.channel_id)
        message = await channel.fetch_message(payload.message_id)
        user = payload.member
        user_roles = user.roles
        if cooldown:
            await channel.send(f"{user.mention} is on cooldown for {cooldown_time} seconds",delete_after=30)
            await message.remove_reaction(payload.emoji, user)
        else:
            target_names = {"charlie squadmember", "bravo squadmember"}  # prefer a set for O(1) lookups
            roles_to_remove = [r for r in user.roles if r.name in target_names]
            if roles_to_remove:
                try:
                    await user.remove_roles(*roles_to_remove, reason="Auto removal of disallowed roles")
                    await channel.send(f"You had the role: {' and '.join(r.name for r in roles_to_remove)} and it got removed", delete_after=30)
                except discord.Forbidden:
                    await channel.send("Error: Missing permissions or role hierarchy issue.")
            if payload.emoji.name == "🟩":
                role = discord.utils.get(user.guild.roles, name="charlie squadmember")
                await user.add_roles(role)
            elif payload.emoji.name == "🟦":
                role = discord.utils.get(user.guild.roles, name="bravo squadmember")
                await user.add_roles(role)
            await message.remove_reaction(payload.emoji, user)
            await channel.send(f"{user.mention} has been assigned to {role}", delete_after=30)
            db.add_role_cooldown(payload.user_id, 7*24*60*60)

client.run(bot_token)
