import random
import os
import datetime
import discord
from discord import (app_commands)
from discord.app_commands import AppCommandError
from database import ModerationDatabase
import json
from dotenv import load_dotenv
import gooleapi as google

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
ROLE_DICTIONARY = data["ROLE_DICTIONARY"]

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
discord_channel_id = int(os.getenv("DISCORD_CHANNEL_ID"))


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
        await interaction.followup.send_message("You are not authorized to use this command")
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
success_count = 0
fail_count = 0
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
    global success_count
    global fail_count
    success_count = 0
    fail_count = 0
    if await admin_check(interaction):
        for target in targets:
            if db.get_promote_cooldown(target.id):
                fail_count += 1
                cooldown_time = db.get_promote_cooldown_remaining(target.id)
                await interaction.channel.send(f"{target.display_name} is on cooldown for {datetime.timedelta(seconds=cooldown_time)}")
                continue
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
        await interaction.followup.send(f"A total of {success_count} people have been promoted\n"
                                        f" {fail_count} promotions have failed",)


async def promotion(ranks, target, branch, prefix_type, interaction):
    global success_count
    global fail_count
    current_index = branch.index(ranks[0])
    next_index = current_index + 1
    if not next_index < len(branch):
        await interaction.channel.send(target.display_name + " is already the highest rank in his/her branch")
    else:
        try:
            # Get the name of the current rank and next rank, then search up the corresponding role
            current_rank_name = branch[current_index]
            next_rank_name = branch[next_index]
            current_role = discord.utils.get(target.guild.roles, name=current_rank_name)
            next_role = discord.utils.get(target.guild.roles, name=next_rank_name)
            author = interaction.user
            # Add the next role (promotion) and remove the old role.
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
            # Send cooldown to database with target ID and time to expire in seconds (1week 60*60*24*7)
            db.add_promote_cooldown(target.id,60*60*24*7)
            # Join squads reminders ! its hardcoded sadly ;(
            success_count += 1
        except on_app_command_error(interaction,AppCommandError[0]):
            fail_count +=1
            await interaction.channel.send(f"Something went wrong with {target.display_name} 's promotion.")
        target_role_names = {r.name for r in target.roles if r != target.guild.default_role}
        if not set(target_role_names) & set(ROLE_DICTIONARY.values()):
            try:
                bravo_role = discord.utils.get(target.guild.roles, name="bravo squadmember")
                bravo_role_count = len(bravo_role.members)
                charlie_role = discord.utils.get(target.guild.roles, name="charlie squadmember")
                charlie_role_count = len(charlie_role.members)
                if bravo_role_count > charlie_role_count:
                    squad_to_join = "Charlie"
                else:
                    squad_to_join = "Bravo"
                await target.send(f'Join the **{squad_to_join}** squad now ! \n https://discord.com/channels/1090564451201196122/1125143726528934060 ')
            except:
                pass

@client.tree.command(name='reset_promote_cooldown',description="Sets the promotion cooldown of the target to 0")
async def reset_promote_cooldown(interaction: discord.Interaction,target: discord.Member,):
    db.reset_promote_cooldown(target.id)
    interaction.response(f"The promotion cooldown for {target.display_name} has been reset.")
# End of promotion commands

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

# error handling
async def on_app_command_error(interaction: discord.Interaction, error: app_commands.AppCommandError):
    try:
        if not interaction.response.is_done():
            await interaction.response.send_message(f"Something went wrong in the command.\n ```{error}```", ephemeral=True)
        else:
            # If already responded to, use followup instead
            await interaction.followup.send("Something went wrong in the command.\n ```{error}```" , ephemeral=True)
    except Exception as e:
        print(f"Error in error handler: {e}")

#         Start of bot reaction role assignment
# Make the bot react wth all listened to reaction on read
@client.event
async def on_ready():
    print(f"Logged in")
    channel = await client.fetch_channel(discord_channel_id)
    message = await channel.fetch_message(discord_msg_id)
    reactions = ROLE_DICTIONARY.keys()
    for reaction in reactions:
        await message.add_reaction(reaction)

# The actual role assignment
@client.event
async def on_raw_reaction_add(payload: discord.RawReactionActionEvent):
    db.remove_expired_role_cooldown()
    # Check if the reaction is from the bot if it is, stop
    if payload.user_id == client.user.id:
        return
    # If the message someone reacted to is the correct message, continue
    if payload.message_id == discord_msg_id:
        cooldown = db.get_role_cooldown(payload.user_id)
        cooldown_time = db.get_role_cooldown_remaining(payload.user_id)
        guild = client.get_guild(payload.guild_id)
        channel = guild.get_channel(payload.channel_id) or await guild.fetch_channel(payload.channel_id)
        message = await channel.fetch_message(payload.message_id)
        role_dictionary_values =  ROLE_DICTIONARY.values()
        role_name_to_assign = ROLE_DICTIONARY.get(str(payload.emoji))
        user = payload.member
        await message.remove_reaction(payload.emoji, user)
        # Check of the user is on cooldown, if yes send msg and stop
        if cooldown:
            await channel.send(f"{user.mention} is on cooldown for {str(datetime.timedelta(seconds=cooldown_time))} seconds",delete_after=30)
        else:
            # Check if the emote that was reacted is one we track
            if str(payload.emoji) not in ROLE_DICTIONARY:
                return
            # Is the value of the emote == reset, reset the person and let them know.
            if  role_name_to_assign == "reset":
                roles_to_remove = [v for v in ROLE_DICTIONARY.values() if v != "reset"]
                for role_name in roles_to_remove:
                    role_to_remove = discord.utils.get(user.guild.roles, name=role_name)
                    await user.remove_roles(role_to_remove)
                await channel.send(f"{user.mention} has been reset.", delete_after=30)
            # The value isn't reset so it's a role we want to assign
            # We must make sure the user only has 1 of the roles in the list at a time (no charlie and bravo at the same time)
            # If the user has a role that isn't the one they requested and is also in the dictionary, remove it first
            else:
                role_to_assign = discord.utils.get(user.guild.roles, name=role_name_to_assign)
                try:
                    for role_name in role_dictionary_values:
                        role_to_remove = discord.utils.get(user.guild.roles, name=role_name)
                        await user.remove_roles(role_to_remove)
                except:
                    pass
                # Final give them the role they want and add a cooldown to the db

                await user.add_roles(role_to_assign)
                await channel.send(f"{user.mention} has been assigned to {role_to_assign}", delete_after=30)
                db.add_role_cooldown(payload.user_id, 7*24*60*60)
        # cleanup
# !CHANGE COOLDOWN !
# end of role assignment by reaction
# Start of whoisin section
@client.tree.command(name="whoisin", description="Dm's a list of people who are in either of the asked for roles.")
async def whoisin(
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

@client.tree.command(name="whoisinboth", description="Dms a list of people who are in both role1 and role2.")
async def whoisinboth(
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

@client.tree.command(name="sheet",description="Update the google spreadsheet information.")
async def sheet(
        interaction:discord.Interaction,
):
    await interaction.response.defer(ephemeral=True)
    if await admin_check(interaction):
        author = interaction.user
        sheet_data = []
        bravo_role = discord.utils.get(author.guild.roles, name="bravo squadmember")
        charlie_role = discord.utils.get(author.guild.roles, name="charlie squadmember")
        bravo_members = bravo_role.members
        charlie_members = charlie_role.members
        list_to_append = []
        list_to_append2 = []
        roles_to_display = ["Combat Life Saver", "Anti Tank", "Combat Engineer"]
        sheet_data = [["Bravo", "Combat Life Saver", "Anti Tank", "Combat Engineer"]]  # Header row

        for member in bravo_members:
            member_row = [member.display_name]
            member_roles_names = [role.name for role in member.roles if role.name != "@everyone"]

            for role in roles_to_display:
                if role in member_roles_names:
                    member_row.append("✅")
                else:
                    member_row.append("❌")

            sheet_data.append(member_row)
        sheet_data.append(["Charlie", "Combat Life Saver", "Anti Tank","Combat Engineer"])
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


client.run(bot_token)