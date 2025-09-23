import random
import discord
from attr.filters import exclude
from discord import app_commands
from database import ModerationDatabase
import json


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
intents = discord.Intents.default()
intents.message_content = True
intents.guilds = True
intents.members = True  # Needed to access member roles

# !!!!!! FOR TESTING, CHANGE WHEN UPLOADING TO ORANGEPI !!!!
GUILD_ID = 1401612201596555285
class MyClient(discord.Client):
    def __init__(self):
        super().__init__(intents=discord.Intents.default())
        self.tree = app_commands.CommandTree(self)
    async def setup_hook(self):
        guild = discord.Object(id=GUILD_ID)
        self.tree.copy_global_to(guild=guild)
        await self.tree.sync(guild=guild)

# Subclassing commands.Bot to register slash commands
# class MyClient(discord.Client):
#     def __init__(self):
#         super().__init__(intents=discord.Intents.default())
#         self.tree = app_commands.CommandTree(self)
#     async def setup_hook(self):
#         # Sync commands with Discord
#         await self.tree.sync()
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
@client.tree.command(name="factcheck",description="The silly factcheck, totally fair and all knowing.")
async def factcheck(interaction: discord.Interaction):
    author = interaction.user
    # Check if they have a role named "Admin"
    if any(role.name in AUTHORIZED_ROLES for role in author.roles):
        await interaction.response.send_message(random.choice(SILLY_FACT_CHECK_POSITIVE))
    else:
        await interaction.response.send_message(random.choice(SILLY_FACT_CHECK_NEGATIVE))

# Start of the promote command

@client.tree.command(name="promote",description="Promotes users mentioned in the arguments.")
async def promote(
        interaction: discord.Interaction,
        target1: discord.Member ,
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
    targets_unfiltered = [target1,target2,target3,target4,target5,target6,target7,target7,target8,target9,target10]
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
                await promotion(user_ranks_ground, target, branch,prefix_type,interaction)
            if nco_ranks:
                branch = NCO_ROLE_HIERARCHY
                prefix_type = NCO_ROLE_PREFIX
                await promotion(nco_ranks, target, branch, prefix_type,interaction)
            if air_ranks:
                branch = AIR_ROLE_HIERARCHY
                prefix_type = AIR_ROLE_PREFIX
                await promotion(air_ranks, target, branch, prefix_type,interaction)
            if armor_ranks:
                branch = ARMOR_ROLE_HIERARCHY
                prefix_type = ARMOR_ROLE_PREFIX
                await promotion(armor_ranks, target, branch, prefix_type,interaction)
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
        await interaction.channel.send("Congrats " + target.mention + " you got promoted from " + str(current_rank_name) + " to " + str(next_rank_name) + " by " + author.mention)
    else:
        await interaction.channel.send(target.display_name + " is already the highest rank in his/her branch")





client.run('MTQwOTEyNTgxMDM3MTI5NzMxNQ.GEHqA4.OaPQOqb6lT6qAIaGenU7ChjuWZ8uNNYLaCjiU8')