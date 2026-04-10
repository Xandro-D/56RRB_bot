import discord
from discord import app_commands
from discord.ext import commands
from modules import utils
from modules import json_reader as js
from modules import database
import datetime

db = database.ModerationDatabase()


async def promotion(ranks, target, branch, prefix_type, interaction, target_roles=None):
    global success_count
    global fail_count
    current_index = branch.index(ranks[0])
    next_index = current_index + 1
    # Check if target has enough required trainings (only for ground gooners)
    if branch == js.GROUND_ROLE_HIERARCHY:
        if next_index >= 3:
            needed_roles = await utils.check_needed_roles(target)
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
            db.add_promote_cooldown(target.id, 60 * 60 * 24 * 7)
            # Join squads reminders ! its hardcoded sadly ;(
            success_count += 1
        except:
            fail_count += 1
            await interaction.channel.send(f"Something went wrong with {target.display_name} 's promotion.")
        target_role_names = {r.name for r in target.roles if r != target.guild.default_role}
        if not set(target_role_names) & set(js.ROLE_DICTIONARY.values()):
            try:
                bravo_role = discord.utils.get(target.guild.roles, name="bravo squadmember")
                bravo_role_count = len(bravo_role.members)
                charlie_role = discord.utils.get(target.guild.roles, name="charlie squadmember")
                charlie_role_count = len(charlie_role.members)
                if bravo_role_count > charlie_role_count:
                    squad_to_join = "Charlie"
                else:
                    squad_to_join = "Bravo"
                await target.send(
                    f'Join the **{squad_to_join}** squad now ! \n https://discord.com/channels/1090564451201196122/1125143726528934060 ')
            except:
                pass



success_count = 0
fail_count = 0

class Promote(commands.Cog):
    def __init__(self, client: commands.Bot):
        self.client = client
    @app_commands.command(name="promote", description="Promotes users mentioned in the arguments.")
    async def promote(
            self,
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
        if await utils.admin_check(interaction):
            for target in targets:
                if db.get_promote_cooldown(target.id):
                    fail_count += 1
                    cooldown_time = db.get_promote_cooldown_remaining(target.id)
                    await interaction.channel.send(
                        f"{target.display_name} is on cooldown for {datetime.timedelta(seconds=cooldown_time)}")
                    continue
                role_names = [role.name for role in target.roles if role.name != "@everyone"]
                user_ranks_ground = [role for role in js.GROUND_ROLE_HIERARCHY if role in role_names]
                nco_ranks = [role for role in js.NCO_ROLE_HIERARCHY if role in role_names]
                air_ranks = [role for role in js.AIR_ROLE_HIERARCHY if role in role_names]
                armor_ranks = [role for role in js.ARMOR_ROLE_HIERARCHY if role in role_names]
                if user_ranks_ground:
                    branch = js.GROUND_ROLE_HIERARCHY
                    prefix_type = js.GROUND_ROLE_PREFIX
                    await promotion(user_ranks_ground, target, branch, prefix_type, interaction)
                if nco_ranks:
                    branch = js.NCO_ROLE_HIERARCHY
                    prefix_type = js.NCO_ROLE_PREFIX
                    await promotion(nco_ranks, target, branch, prefix_type, interaction)
                if air_ranks:
                    branch = js.AIR_ROLE_HIERARCHY
                    prefix_type = js.AIR_ROLE_PREFIX
                    await promotion(air_ranks, target, branch, prefix_type, interaction)
                if armor_ranks:
                    branch = js.ARMOR_ROLE_HIERARCHY
                    prefix_type = js.ARMOR_ROLE_PREFIX
                    await promotion(armor_ranks, target, branch, prefix_type, interaction)
            await interaction.followup.send(f"A total of {success_count} people have been promoted\n"
                                            f" {fail_count} promotions have failed", )

        @app_commands.command(
            name="reset_promotion_cooldown"
            , description="Reset promotion cooldown.",
        )
        async def reset_promotion_cooldown(
                self,
                interaction: discord.Interaction,
                target: discord.Member, ):
            db.reset_promote_cooldown(target.id)
            await interaction.channel.send(f"The promotion cooldown for {target.display_name} has been reset.")





async def setup(client: commands.Bot):
    await client.add_cog(Promote(client))
