import random
import os
import datetime
import re
import discord
from discord import (app_commands)
from discord.app_commands import AppCommandError
from discord.ext import tasks
from database import ModerationDatabase
import json
from dotenv import load_dotenv
import googleapi as google
from lxml import html,etree
import io
import a2s
db = ModerationDatabase()

with open("data.json", "r") as f:
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
CLIENT_SIDE_MOD_LIST = data["CLIENT_SIDE_MOD_LIST"]

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
async def admin_check(
        interaction
):
    '''
    Return True if author of the command has a role from [authorized roles]
    Returns false if author does not.
    :param interaction:
    :return:
    '''
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
        # -----------------------------------------------------------------------------------
        # Start of the promote command


async def check_needed_roles(target: discord.Member,list_to_check: list = ("Combat Life Saver", "Combat Engineer", "Anti Tank") ):
    '''
    Give discord member and list, will return a list of roles that are in the list to check but the member doesn't have
    ex. If member has the admin role and you check for admin it will return an empty list.
    If that member doesn't have admin it will return admin in the list.
    :param target: Discord.member object who's roles we need to check
    :param list_to_check: the list of role names to check
    :return: list of roles the user doesn't have but are in list to check
    '''
    roles_needed_list = []
    role_names = [role.name for role in target.roles if role.name != "@everyone"]
    for role in list_to_check:
        if role in role_names:
            continue
        else:
            roles_needed_list.append(role)
    return roles_needed_list


async def promotion(ranks, target, branch, prefix_type, interaction,target_roles=None):
    global success_count
    global fail_count
    current_index = branch.index(ranks[0])
    next_index = current_index + 1
    # Check if target has enough required trainings (only for ground gooners)
    if branch == GROUND_ROLE_HIERARCHY:
        if next_index >= 3:
            needed_roles = await check_needed_roles(target)
            if len(needed_roles) > 0:
                await interaction.channel.send(f"{target.mention} needs {', '.join(needed_roles)} to promote")
                return
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

@client.tree.command(name="check_roles",description="A temporary command to check who still needs trainings.")
async def check_roles(
        interaction: discord.Interaction,
        role : discord.Role
):
    message = f""
    await interaction.response.defer(ephemeral=True)
    for member in role.members:
        role_names = [role.name for role in member.roles if role.name != "@everyone"]
        user_ranks_ground = [role for role in GROUND_ROLE_HIERARCHY if role in role_names]
        if user_ranks_ground:
            if GROUND_ROLE_HIERARCHY.index(user_ranks_ground[0]) >= 3:
                needed_roles = await check_needed_roles(member)
                if needed_roles:
                    text = f"{member.display_name} still needs {', '.join(needed_roles)}\n"
                    message += text
                    await interaction.followup.send(f"{member.mention} still needs {', '.join(needed_roles)}'",ephemeral=True)
    await interaction.followup.send(f"```{message}```", ephemeral=True)

# Make buttons
class ConfirmView(discord.ui.View):
    def __init__(self,true_lable:str, false_lable:str):
        super().__init__(timeout=60*4)
        self.value = None  # True = kick, False = skip
        self.kick.label = true_lable
        self.skip.label = false_lable

    @discord.ui.button(label="Kick", style=discord.ButtonStyle.danger)
    async def kick(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button
    ):
        self.value = True
        self.stop()
        await interaction.response.defer()

    @discord.ui.button(label="Skip", style=discord.ButtonStyle.secondary)
    async def skip(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button
    ):
        self.value = False
        self.stop()
        await interaction.response.defer()



@client.tree.command(name="bct_check",description="Checks if people need to be kicked cause they haven't signed up.")
async def bct_check(
    interaction = discord.Interaction
):
    if not await admin_check(interaction):
        return
    await interaction.response.defer(ephemeral=True)
    await interaction.followup.send("Checking users...",ephemeral=True)
    list_of_members_to_kick = []
    guild = interaction.guild
    guild_members = guild.members
    for member in guild_members:
        if await check_needed_roles(member,["Member"]):
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

        view = ConfirmView(
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

@client.tree.command(name="bct_training",description="Send a private message to everyone who still needs a bct.")
async def bct_training(
        interaction: discord.Interaction,
):
    await interaction.response.defer()
    if not await admin_check(interaction):
        return
    guild = interaction.guild
    members = guild.members
    success_list =[]
    fail_list = []
    for member in members:
        if not await check_needed_roles(member,["Waiting for BCT"]):
            try:
                await member.send(f'Hello, you have joined the 56th RRB. To be able to join OPs follow the installation guide and request a BCT https://discord.com/channels/1090564451201196122/1346494156410716281.')
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


async def reset_promote_cooldown(interaction: discord.Interaction,
                                 target: discord.Member,):
    db.reset_promote_cooldown(target.id)
    await interaction.channel.send(f"The promotion cooldown for {target.display_name} has been reset.")
# End of promotion commands

# Start of moderation commands
# Strike command

@client.tree.command(name="strike", description="Strike a person, strikes last 6 months.")
async def strike(interaction: discord.Interaction, target: discord.Member,reason:str):
    if await admin_check(interaction):
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
async def warn(interaction: discord.Interaction, target: discord.Member,reason:str):
    if await admin_check(interaction):
        if db.get_warnings(target.id) <= 4:
            db.add_warning(target.id)
            await interaction.response.send_message(f"{target.display_name} has been warned."
                                                    f"\nreason:```{reason}```")
        else:
            db.reset_warnings(target.id)
            db.add_strike(target.id, 15778463)
            message = (f"{target.display_name} has 4 or more warnings and has been struck. "
                       f"Now he has {db.get_strikes(target.id)} strikes and {db.get_warnings(target.id)} warns."
                       f"\nreason:```{reason}```")
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
    server_status_loop.start()

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
#--------------------------------------------------------------------------------------------------------------------------
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
#         End of who is in section
# ------------------------------------------------------------------------------------------------
# Start of modpack checking section.
def get_mods(content):
    tree = html.fromstring(content)
    mods = []
    for row in tree.xpath('//tr[@data-type="ModContainer"]'):
        mod = {
            'name': row.xpath('./td[@data-type="DisplayName"]/text()')[0],
            'link': row.xpath('.//a[@data-type="Link"]/@href')[0]
        }
        mods.append(mod)
    return mods

def get_dlc(content):
    tree = html.fromstring(content)
    dlcs = []
    for row in tree.xpath('//tr[@data-type="DlcContainer"]'):
        dlc = {
            "name": row.xpath('./td[@data-type="DisplayName"]/text()')[0],
        }
        dlcs.append(dlc)
    return dlcs

def add_mod(html_string,modname,modlink):
    html_string = html_string.replace(b'\r\n', b'\n').replace(b'\r', b'\n')

    tree = html.fromstring(html_string)

    mod_table = tree.xpath('//div[@class="mod-list"]//table')[0]

    new_row = etree.Element("tr")
    new_row.set("data-type","ModContainer")

    name_cell = etree.SubElement(new_row,"td")
    name_cell.set("data-type","DisplayName")
    name_cell.text = modname

    from_cell = etree.SubElement(new_row,"td")
    from_span = etree.SubElement(from_cell,"span")
    from_span.set("class","from-steam")
    from_span.text = "Steam"

    link_cell = etree.SubElement(new_row,"td")
    link_a = etree.SubElement(link_cell,"a")
    link_a.set("href",modlink)
    link_a.set("data-type","Link")
    link_a.text = modlink

    mod_table.append(new_row)

    html_string = html.tostring(tree,encoding="utf-8",pretty_print=False,method="xml")

    return html_string

def remove_mod(html_string,modname):
    html_string = html_string.replace(b'\r\n', b'\n').replace(b'\r', b'\n')

    tree = html.fromstring(html_string)

    mod_to_remove = tree.xpath(f'//td[text()="{modname}"]')[0]

    row = mod_to_remove.getparent()
    row.getparent().remove(row)

    html_string = html.tostring(tree,encoding="utf-8",pretty_print=False,method="xml")

    return html_string

def add_dlc(html_string,dlc_name,dlc_link):
    html_string = html_string.replace(b'\r\n', b'\n').replace(b'\r', b'\n')

    tree = html.fromstring(html_string)

    dlc_table = tree.xpath(f'//div[@class="dlc-list"]//table')[0]

    new_row = etree.Element("tr")
    new_row.set("data-type","DlcContainer")

    name_cell = etree.SubElement(new_row,"td")
    name_cell.set("data-type","DisplayName")
    name_cell.text = dlc_name

    link_cell = etree.SubElement(new_row,"td")
    a_link = etree.SubElement(link_cell,"a")
    a_link.set("href",dlc_link)
    a_link.set("data-type","link")
    a_link.text = dlc_link

    dlc_table.append(new_row)
    html_string = html.tostring(tree,encoding="utf-8",pretty_print=False,method="xml")
    return html_string

def remove_dlc(html_string,dlc_name):
    html_string = html_string.replace(b'\r\n', b'\n').replace(b'\r', b'\n')

    tree = html.fromstring(html_string)

    dlc_to_remove = tree.xpath(f'//tr[@data-type="DlcContainer"]//td[text()="{dlc_name}"]')[0]

    row = dlc_to_remove.getparent()
    row.getparent().remove(row)

    html_string = html.tostring(tree,encoding="utf-8",pretty_print=False,method="xml")
    return html_string

def get_load_order(html_string):
    mods = get_mods(html_string)
    load_order = ""
    for mod in mods:
        if mod["name"] in CLIENT_SIDE_MOD_LIST:
            continue
        else:
            load_order += f'@{mod["name"]};'
    load_order = re.sub(r'[&(),!:.|\\/]', '', load_order).replace("@@", "@")
    return load_order

@client.tree.command(name="modpack", description="Description")
async def modpack(
        interaction: discord.Interaction,
        html_file: discord.Attachment,
        op_date:str,
        modpack_name:str=None
):
    await interaction.response.defer(ephemeral=True)
    await interaction.followup.send(f"reading file... ",ephemeral=True)
    author=interaction.user

    if not modpack_name:
        modpack_name = html_file.filename.replace(".html","")
    html_content = await html_file.read()
    mods = get_mods(html_content)
    dlcs = get_dlc(html_content)
#     Check if western sahara mod is enabled
    western_sahara_mod = False
    for mod in mods:
        if mod["name"] == "Western Sahara - Creator DLC Compatibility Data for Non-Owners":
            western_sahara_mod = True
#      Check if mod has western sahara dlc:
    western_sahara_dlc = False
    for dlc in dlcs:
        if dlc["name"] == "Western Sahara":
            western_sahara_dlc = True
    await interaction.followup.send(f"DLC: {western_sahara_dlc}  Mod: {western_sahara_mod}",ephemeral=True)


    if not western_sahara_dlc:
        # If the pack does not have the dlc, remove the compat if its there and add the dlc.
        if western_sahara_mod:
            new_pack_no_compat = remove_mod(html_content, "Western Sahara - Creator DLC Compatibility Data for Non-Owners")
            new_pack_dlc_no_compat = add_dlc(new_pack_no_compat, "Western Sahara", "https://store.steampowered.com/app/1681170")
        else:
            new_pack_dlc_no_compat = add_dlc(html_content, "Western Sahara", "https://store.steampowered.com/app/1681170")

        if isinstance(new_pack_dlc_no_compat, str):
            new_pack = new_pack_dlc_no_compat.encode('utf-8')
        file_with_dlc = discord.File(fp=io.BytesIO(new_pack_dlc_no_compat), filename=f"{modpack_name}_without_compat.html")
    #  If we do have the dlc, remove the compat if there. dont add the dlc. (the input file is corect.)
    else:
        if western_sahara_mod:
            new_pack_no_compat = remove_mod(html_content, "Western Sahara - Creator DLC Compatibility Data for Non-Owners")
            new_pack_dlc_no_compat_str = add_dlc(new_pack_no_compat, "Western Sahara","https://store.steampowered.com/app/1681170")
        else:
            new_pack_dlc_no_compat_str = html_content

        if isinstance(html_content, str):
            html_content = html_content.encode('utf-8')
        file_with_dlc = discord.File(fp=io.BytesIO(new_pack_dlc_no_compat_str), filename=f"{modpack_name}_without_compat.html")
    # If we don't have the mod, check if we have the dlc and remove it if we do, then add the mod
    if not western_sahara_mod:
        if western_sahara_dlc:
            new_pack_no_dlc = remove_dlc(html_content, "Western Sahara")
            new_pack_no_dlc_compat_str = add_mod(new_pack_no_dlc, "Western Sahara - Creator DLC Compatibility Data for Non-Owners","https://steamcommunity.com/sharedfiles/filedetails/?id=2636962953")
        else:
            new_pack_no_dlc_compat_str = add_mod(html_content, "Western Sahara - Creator DLC Compatibility Data for Non-Owners","https://steamcommunity.com/sharedfiles/filedetails/?id=2636962953")


        if isinstance(new_pack_no_dlc_compat_str, str):
            new_pack_no_dlc_compat_str = new_pack_no_dlc_compat_str.encode('utf-8')
        new_pack_no_dlc_compat = discord.File(fp=io.BytesIO(new_pack_no_dlc_compat_str), filename=f"{modpack_name}_with_compat.html")

    # If we do have the mod, just remove the dlc if its there else the input pack is correct.
    else:
        if western_sahara_dlc:
            new_pack_no_dlc_compat = remove_dlc(html_content, "Western Sahara")
        else:
            new_pack_no_dlc_compat = html_content
        new_pack_no_dlc_compat_str = (
            new_pack_no_dlc_compat.encode("utf-8")
            if isinstance(new_pack_no_dlc_compat, str)
            else new_pack_no_dlc_compat
        )

        new_pack_no_dlc_compat = discord.File(fp=io.BytesIO(new_pack_no_dlc_compat_str), filename=f"{modpack_name}_with_compat.html")

    load_order = get_load_order(new_pack_no_dlc_compat_str)
    if isinstance(load_order,str):
        load_order = load_order.encode("utf-8")
    file_with_load_order = discord.File(fp=io.BytesIO(load_order),filename=f"{modpack_name} load order.txt")

    await interaction.followup.send(content=f"Load order:",file=file_with_load_order,ephemeral=True)
    await interaction.channel.send(content=f"[{op_date}] {modpack_name} **Without the compat**, make sure the western sahara dlc is loaded. Made by {author.mention}", file=file_with_dlc)
    await interaction.channel.send(content=f"[{op_date}] {modpack_name} **with the compact**, only loading the modpack is needed. Made by {author.mention}",file=new_pack_no_dlc_compat)

#     Server tracking stuff

# Live player vieuw
server_status = None
server_ip = str(os.getenv("SERVER_IP"))
server_port = int(os.getenv("SERVER_PORT"))
def get_data(server_ip,server_port):
    server_address = (server_ip, server_port)
    info = a2s.info(server_address)
    players = a2s.players(server_address)
    return info, players



@tasks.loop(minutes=0.2)
async def server_status_loop():
    global server_status
    if server_status is None:
        channel = discord.utils.get(client.get_all_channels(), name="server-status")
        if channel is None:
            print("Error: 'server-status' channel not found!")
            return
        server_status = await channel.send("Getting server status...")

    try:
        server_data = get_data(server_ip,server_port)
        info = server_data[0]
        players = server_data[1]

        embed = discord.Embed(
            title="Server Status",
            description=f"Online !",
            color=discord.Color.green(),
            timestamp=discord.utils.utcnow()
        )

        # Add players list
        if players:
            player_list = "\n".join([f"• {player.name}" for player in players])
            embed.add_field(name=f"Players Online ({len(players)})", value=player_list, inline=False)
        else:
            embed.add_field(name="Players Online", value="*No players online*", inline=False)
        embed.add_field(name="Mission:", value=info.game)
        embed.set_footer(text="Last updated")

        await server_status.edit(content=None, embed=embed)

    except Exception as e:
        # Handle errors
        error_embed = discord.Embed(
            title="Server Status",
            description="Could not connect to server",
            color=discord.Color.red(),
            timestamp=discord.utils.utcnow()
        )
        error_embed.set_footer(text=f"Error: {str(e)}")
        await server_status.edit(content=None, embed=error_embed)


client.run(bot_token)