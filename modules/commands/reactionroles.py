import datetime
import discord
from discord.ext import commands
from modules import database
from modules.config import discord_channel_id, discord_msg_id
from modules.json_reader import ROLE_DICTIONARY
db = database.ModerationDatabase()


class ReactionRoles(commands.Cog):
    def __init__(self, client: commands.Bot):
        self.client = client

    @commands.Cog.listener()
    async def on_ready(self):
        print("Logged in")
        try:
            channel = await self.client.fetch_channel(discord_channel_id)
            message = await channel.fetch_message(discord_msg_id)

            for reaction in ROLE_DICTIONARY.keys():
                await message.add_reaction(reaction)
        except Exception as e:
            print(f"Failed to add startup reactions: {e}")

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload: discord.RawReactionActionEvent):
        db.remove_expired_role_cooldown()

        if self.client.user and payload.user_id == self.client.user.id:
            return

        if payload.message_id != discord_msg_id:
            return

        guild = self.client.get_guild(payload.guild_id)
        if guild is None:
            return

        channel = guild.get_channel(payload.channel_id) or await guild.fetch_channel(payload.channel_id)
        message = await channel.fetch_message(payload.message_id)

        member = payload.member or guild.get_member(payload.user_id)
        if member is None:
            return

        await message.remove_reaction(payload.emoji, member)

        cooldown = db.get_role_cooldown(payload.user_id)
        cooldown_time = db.get_role_cooldown_remaining(payload.user_id)

        if cooldown:
            await channel.send(
                f"{member.mention} is on cooldown for {str(datetime.timedelta(seconds=cooldown_time))} seconds",
                delete_after=30
            )
            return

        emoji_str = str(payload.emoji)
        if emoji_str not in ROLE_DICTIONARY:
            return

        role_name_to_assign = ROLE_DICTIONARY[emoji_str]
        role_dictionary_values = ROLE_DICTIONARY.values()

        if role_name_to_assign == "reset":
            roles_to_remove = [v for v in role_dictionary_values if v != "reset"]
            for role_name in roles_to_remove:
                role_to_remove = discord.utils.get(guild.roles, name=role_name)
                if role_to_remove:
                    await member.remove_roles(role_to_remove)
            await channel.send(f"{member.mention} has been reset.", delete_after=30)
            return

        for role_name in role_dictionary_values:
            role_to_remove = discord.utils.get(guild.roles, name=role_name)
            if role_to_remove:
                try:
                    await member.remove_roles(role_to_remove)
                except Exception:
                    pass

        role_to_assign = discord.utils.get(guild.roles, name=role_name_to_assign)
        if role_to_assign is None:
            await channel.send(f"Role '{role_name_to_assign}' not found.", delete_after=30)
            return

        await member.add_roles(role_to_assign)
        await channel.send(f"{member.mention} has been assigned to {role_to_assign.mention}", delete_after=30)
        db.add_role_cooldown(payload.user_id, 7 * 24 * 60 * 60)


async def setup(client: commands.Bot):
    await client.add_cog(ReactionRoles(client))