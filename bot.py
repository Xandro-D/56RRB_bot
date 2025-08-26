import discord
from discord.ext import commands
from database import ModerationDatabase


db = ModerationDatabase()

#setup variables
# ------- Ground gooners --------
GROUND_ROLE_HIERARCHY = [
    '[Private Third Class]',
    '[Private Second Class]',
    '[Private First Class]',
    '[Specialist Third Class]',
    '[Specialist Second Class]',
    '[Specialist First Class]',
    '[Master Specialist]',
    '[First Specialist]',
    '[Specialist Major]'
]

GROUND_ROLE_PREFIX = ['PV3.', 'PV2.', 'PFC.', 'SP3.', 'SP2.', 'SP1.', 'MSP.', 'FSP.', 'SPM.']

# ------- NCO nerds -------
NCO_ROLE_HIERARCHY = [
    '[Corporal]',
    '[Sergeant]',
    '[Staff Sergeant]',
    '[Sergeant First Class]',
    '[Master Sergeant]'
]

NCO_ROLE_PREFIX = ['CPL.','SGT.','SSG.','SFC.','MSG.']

# ----- AIR Giga chads ------
AIR_ROLE_HIERARCHY = [
    '[Airman Basic]',
    '[Airman]',
    '[Airman 1st Class]',
    '[Airman Specialist]',
    '[Senior Airman]',
    '[Staff Sergeаnt]',
    '[Technical Sergeаnt]',
    '[Master Sergeаnt]'
]

AIR_ROLE_PREFIX = ['AMB.','AMN.','AFC.','AMS.','SRA.','SSG.','TSG.','MSG.']

# ------ ARMOR gays -------
ARMOR_ROLE_HIERARCHY = [
    '[Crewman]',
    '[Technical Crewman]',
    '[Armor Sergeant]',
    '[Armor Staff Sergeant]',
    '[Gunnery Sergeant]',
]

ARMOR_ROLE_PREFIX = [
    'CMN.','TCMD.','ASGT.','ASSG.','GYSGT.'
]

AUTHORIZED_ROLES = ['Admin',]

# Initializing discord bot
intents = discord.Intents.default()
intents.message_content = True
intents.guilds = True
intents.members = True  # Needed to access member roles

bot = commands.Bot(command_prefix="!", intents=intents)

async def admin_check(ctx):
    author = ctx.author
    role_names = [role.name for role in author.roles]
    user_level = [role for role in AUTHORIZED_ROLES if role in role_names]
    db.remove_expired_strikes()
    if user_level:
        return True
    else:
        await ctx.send("You are not authorized to use this command.")
        return False


@bot.event
async def on_ready():
    print(f'Logged in as {bot.user}')

# Actually commands
# doctorate @user nick
@bot.command()
async def doc(ctx):
    if await admin_check(ctx):
        # get the roles for new people
        role2 = discord.utils.get(ctx.guild.roles, name="Waiting for BCT")
        target = ctx.message.mentions[0]
        content = ctx.message.content
        split_content = content.split()
        new_nick = (" " + split_content[2])
        await target.add_roles(role2)
        await target.edit(nick=new_nick)
        await ctx.send(new_nick + " has been drafted")
# -----------------------------------
async def promotion(user_ranks, target, branch, prefix_type,ctx):
    current_index = branch.index(user_ranks[0])
    next_index = current_index + 1
    if next_index < len(branch):
        # Get the name of the current rank and next rank, then search up the corresponding role
        curent_rank_name = branch[current_index]
        next_rank_name = branch[next_index]
        current_role = discord.utils.get(target.guild.roles, name=curent_rank_name)
        next_role = discord.utils.get(target.guild.roles, name=next_rank_name)
        author = ctx.message.author
        author_name = author.display_name
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
        await ctx.send("Congrats " + str(target.display_name) + " you got promoted from " + str(curent_rank_name) + " to " + str(next_rank_name) + " by " + author_name)
    else:
        await ctx.send(target.display_name + " is already the highest rank in his/her branch")

@bot.command()
# the !promote command
async def promote(ctx):
    # First check to see if the sender has enough privilege to execute command
    if await admin_check(ctx):
        # Check who the user mentioned, that is the target.
        targets = ctx.message.mentions
        # If the target is in ground branch call promotion function with branch
        for target in targets:
            # Filter for roles in each branch separately
            # Get the roles of the suer.
            role_names = [role.name for role in target.roles]
            user_ranks_ground = [role for role in GROUND_ROLE_HIERARCHY if role in role_names]
            nco_ranks = [role for role in NCO_ROLE_HIERARCHY if role in role_names]
            air_ranks = [role for role in AIR_ROLE_HIERARCHY if role in role_names]
            armor_ranks = [role for role in ARMOR_ROLE_HIERARCHY if role in role_names]
            if user_ranks_ground:
                branch = GROUND_ROLE_HIERARCHY
                prefix_type = GROUND_ROLE_PREFIX
                await promotion(user_ranks_ground, target, branch,prefix_type,ctx)
            if nco_ranks:
                branch = NCO_ROLE_HIERARCHY
                prefix_type = NCO_ROLE_PREFIX
                await promotion(nco_ranks, target, branch, prefix_type,ctx)
            if air_ranks:
                branch = AIR_ROLE_HIERARCHY
                prefix_type = AIR_ROLE_PREFIX
                await promotion(air_ranks, target, branch, prefix_type,ctx)
            if armor_ranks:
                branch = ARMOR_ROLE_HIERARCHY
                prefix_type = ARMOR_ROLE_PREFIX
                await promotion(armor_ranks, target, branch, prefix_type,ctx)
        await ctx.message.delete()
#         ---------------------------------------------
@bot.command()
# the silly fact check command
async def admin_check(ctx):
    author = ctx.author
    role_names = [role.name for role in author.roles]
    user_level = [role for role in AUTHORIZED_ROLES if role in role_names]
    db.remove_expired_strikes()
    if user_level:
        await ctx.send("You are absolutely correct")
    else:
        await ctx.send("You are wrong dipshit.")

#           ------------------------------------------

@bot.command()
#The strike command
# Check if user is admin, if yes continue
# Get he user_id from each mentioned person and send a strike along side the expire date(how long untill expires) too the b
async def strike(ctx):
    if await admin_check(ctx):
        targets = ctx.message.mentions
        for target in targets:
            target_user_id = target.id
            db.add_strike(target_user_id,15778463)
            if db.get_strikes(target_user_id) < 3:
                await ctx.send(f"{target.display_name} has been struck and now has {db.get_strikes(target_user_id)} strikes.  ")
            else:
                await ctx.send(f"{target.display_name} has three or more strikes and should be banned, get em boys.")
@bot.command()
async def remove_strike(ctx):
    if await admin_check(ctx):
        targets = ctx.message.mentions
        for target in targets:
            target_user_id = target.id
            if db.get_strikes(target_user_id) > 0:
                db.remove_strike(target_user_id)
                await ctx.send(f"{target.display_name} now has {db.get_strikes(target_user_id)} strikes.")
            else:
                await ctx.send(f"{target.display_name} has no strikes to remove.")

@bot.command()
# warning command
# Check for admin privilage, if admin continue
# for all mention user get user_id and put a warning in the db
async def warn(ctx):
    if await admin_check(ctx):
        targets = ctx.message.mentions
        for target in targets:
            target_user_id = target.id
            if db.get_warnings(target_user_id) < 3:
                db.add_warning(target_user_id,)
                await ctx.send(f"{target.display_name} has been warned.")
            else:
                db.reset_warnings(target_user_id)
                db.add_strike(target_user_id,15778463)
                await ctx.send(f"{target.display_name} has 3 or more warnings and has been striked. Now he has {db.get_strikes(target_user_id)} strikes and {db.get_warnings(target_user_id)} warns.")

@bot.command()
async def remove_warn(ctx):
    if await admin_check(ctx):
        targets = ctx.message.mentions
        for target in targets:
            target_user_id = target.id
            if db.get_warnings(target_user_id) > 0:
                db.remove_warning(target_user_id)
                await ctx.send(f"{target.display_name} now has {db.get_warnings(target_user_id)} warnings.")
            else:
                await ctx.send(f"{target.display_name} has no warnings to remove.")

@bot.command()
async def info(ctx):
    targets = ctx.message.mentions
    for target in targets:
        strikes = db.get_strikes(target.id)
        warnings = db.get_warnings(target.id)
        await ctx.send(f"{target.display_name} has {strikes} strikes and {warnings} warnings.")

@bot.command()
async def reset(ctx):
    if await admin_check(ctx):
        targets = ctx.message.mentions
        for target in targets:
            target_user_id = target.id
            db.reset_strikes(target_user_id)
            db.reset_warnings(target.id)
            await ctx.send(f"{target.display_name} has been reset.")
bot.run('MTQwOTEyNTgxMDM3MTI5NzMxNQ.GEHqA4.OaPQOqb6lT6qAIaGenU7ChjuWZ8uNNYLaCjiU8')