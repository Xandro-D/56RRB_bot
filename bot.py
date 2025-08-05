# This example requires the 'message_content' intent.
import discord
from aiohttp.test_utils import TestClient
from discord.ext import commands
from discord import app_commands

#setup variebles

ROLE_HIERARCHY = [
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

ROLE_PREFIX = ['PV3.', 'PV2.', 'PFC.', 'SP3.', 'SP2.', 'SP1.', 'MSP.', 'FSP.', 'SPM.']

AUTHORIZED_ROLES = ['Admin',]


# Initializing discord bot
intents = discord.Intents.default()
intents.message_content = True
intents.guilds = True
intents.members = True  # Needed to access member roles

bot = commands.Bot(command_prefix="!", intents=intents)


# Actually commands
@bot.event
async def on_ready():
    print(f'Logged in as {bot.user}')



# docternate @user nick
@bot.command()
async def doc(ctx):
    author = ctx.message.author
    # Get the roles of the suer.
    role_names = [role.name for role in author.roles]
    # Filter for roles in the HIERACHY
    user_level = [role for role in AUTHORIZED_ROLES if role in role_names]
    if user_level is not None:
        # get the roles for new poeple
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





@bot.command()
# the !promote command
async def promote(ctx):
    author = ctx.author
    role_names = [role.name for role in author.roles]
    user_level = [role for role in AUTHORIZED_ROLES if role in role_names]

    print(author)
    if user_level is not None:
        # Check who the user mentiont, that is the target.
        target = ctx.message.mentions[0]
        # Get the roles of the suer.
        role_names = [role.name for role in target.roles]
        # Filter for roles in the HIERACHY
        user_ranks = [role for role in ROLE_HIERARCHY if role in role_names]
        # Get the index of the rank from the target.
        if user_ranks is not None:
            current_index = ROLE_HIERARCHY.index(user_ranks[0])
            print(current_index)
            next_index = current_index + 1
            if next_index < len(ROLE_HIERARCHY):

                # Get the name of the curent rank and next rank, then search up the coresponding role
                curent_rank_name = ROLE_HIERARCHY[current_index]
                next_rank_name = ROLE_HIERARCHY[next_index]
                curent_role = discord.utils.get(target.guild.roles, name=curent_rank_name)
                next_role = discord.utils.get(target.guild.roles, name=next_rank_name)
                # Add the next role (promotion) and remove the cleanup.
                await target.add_roles(next_role)
                await target.remove_roles(curent_role)

                # Get the prefix for the current role IE PFC.
                # Split the current username by the Space inbetween the prefix and nickname, thn replace the prefix.
                new_prefix = ROLE_PREFIX[next_index]
                nickname = target.display_name
                nickname_parts = nickname.split(' ', 1)
                # nickanme_parts [0] PFC
                # nickanme_parts[1] User
                print(nickname_parts)
                new_nickname = new_prefix + " " +nickname_parts[1]
                await target.edit(nick=new_nickname)
                print(new_nickname)
                await ctx.send("Congrats " + str(target.display_name) + "You got promoted from " + str(curent_rank_name) + " Too " + str(next_rank_name))
    else:
        await ctx.send("You are not authorized to use this command.")




bot.run('MTQwMTU3MTAwMzE0NTkxNjQzNw.GOPDNy.tbh9qsuCJC5GwPzMnG067yWFJoH7VwjgRMK9n8')
