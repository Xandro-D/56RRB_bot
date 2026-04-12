import discord
from modules import json_reader



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
    if any(role.name in json_reader.AUTHORIZED_ROLES for role in author.roles):
        return True
    else:
        await interaction.followup.send_message("You are not authorized to use this command")
        return False


async def check_needed_roles(target: discord.Member,
    list_to_check: list = ("Combat Life Saver", "Combat Engineer", "Anti Tank")):
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

async def role_check(interaction,role_name:str):
    '''
    Checks if the target has a role or not
    :param interaction:
    :param role_name:
    :return: True if target has role False if not
    '''
    # Check if they have a role named "Admin"
    author = interaction.user
    roles = author.roles
    role_names = []
    for i in roles:
        role_names.append(i.name)
    if role_name in roles.name:
        return True
    else:
        return False