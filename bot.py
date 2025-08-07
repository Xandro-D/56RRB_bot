import discord
from discord.ext import commands

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

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user}')

# Actually commands
# docternate @user nick
@bot.command()
async def doc(ctx):
    author = ctx.message.author
    # Get the roles of the suer.
    role_names = [role.name for role in author.roles]
    # Filter for roles in the HIERARCHY
    user_level = [role for role in AUTHORIZED_ROLES if role in role_names]
    if user_level:
        # get the roles for new people
        role1 = discord.utils.get(ctx.guild.roles, name="Member")
        role2 = discord.utils.get(ctx.guild.roles, name="Waiting for BCT")
        target = ctx.message.mentions[0]
        content = ctx.message.content
        split_content = content.split()
        new_nick = (" " + split_content[2])
        await target.add_roles(role1, role2)
        await target.edit(nick=new_nick)
        await ctx.send(new_nick + " has been drafted")
    else:
        await ctx.send("You are not authorized to do that.")

async def promotion(user_ranks, target, branch, prefix_type,ctx):
    current_index = branch.index(user_ranks[0])
    next_index = current_index + 1
    if next_index < len(branch):
        # Get the name of the current rank and next rank, then search up the corresponding role
        curent_rank_name = branch[current_index]
        next_rank_name = branch[next_index]
        current_role = discord.utils.get(target.guild.roles, name=curent_rank_name)
        next_role = discord.utils.get(target.guild.roles, name=next_rank_name)
        # Add the next role (promotion) and remove the cleanup.
        await target.add_roles(next_role)
        await target.remove_roles(current_role)
        # Get the prefix for the current role IE PFC.
        # Split the current username by the Space inbetween the prefix and nickname, thn replace the prefix.
        new_prefix = prefix_type[next_index]
        nickname = target.display_name
        nickname_parts = nickname.split(' ', 1)
        # nickanme_parts [0] PFC
        # nickanme_parts[1] User
        new_nickname = new_prefix + " " + nickname_parts[1]
        await target.edit(nick=new_nickname)
        await ctx.send("Congrats " + str(target.display_name) + " you got promoted from " + str(curent_rank_name) + " to " + str(next_rank_name))
    else:
        await ctx.send(target.display_name + " is already the highest rank in his/her branch")

@bot.command()
# the !promote command
async def promote(ctx):
    # First check to see if the sender has enough privelge to execurte command
    author = ctx.author
    role_names = [role.name for role in author.roles]
    user_level = [role for role in AUTHORIZED_ROLES if role in role_names]
    if user_level:
        # Check who the user mentioned, that is the target.
        target = ctx.message.mentions[0]
        # Get the roles of the suer.
        role_names = [role.name for role in target.roles]

        # Filter for roles in each branch sepperatly
        user_ranks_ground = [role for role in GROUND_ROLE_HIERARCHY if role in role_names]
        nco_ranks = [role for role in NCO_ROLE_HIERARCHY if role in role_names]
        air_ranks = [role for role in AIR_ROLE_HIERARCHY if role in role_names]
        armor_ranks = [role for role in ARMOR_ROLE_HIERARCHY if role in role_names]
        # If the target is in ground branch call promotion function with branch
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

    else:
        await ctx.send("You are not authorized to use this command.")




positive_reply = [
    'Our independent analysts at RT and TASS confirms this as true',
    "Fact checked as true by real american patriots",
    "The CCP approves this message",
]

negative_reply = [
    "Grok tells me this is false",
    "You are wrong dipshit.",
    "This is as true as epstein having committed suicide",
]
@bot.command()
# the silly fact check command
async def factcheck(ctx):
    # First check to see if the sender is an admin and therefore correct
    author = ctx.author
    role_names = [role.name for role in author.roles]
    user_level = [role for role in AUTHORIZED_ROLES if role in role_names]
    if user_level:
        responds = random.choice()
        await ctx.send(responds)
    else:
        responds = random.choice(negative_reply)
        await ctx.send(responds)










































bot.run('MTQwMTU3MTAwMzE0NTkxNjQzNw.GOPDNy.tbh9qsuCJC5GwPzMnG067yWFJoH7VwjgRMK9n8')