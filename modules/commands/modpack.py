import discord
from discord import app_commands
from discord.ext import commands
from modules import json_reader as js
from lxml import html,etree
import re
import io



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
        if mod["name"] in js.CLIENT_SIDE_MOD_LIST:
            continue
        else:
            load_order += f'@{mod["name"]};'
    load_order = re.sub(r'[&(),!:.|\\/]', '', load_order).replace("@@", "@")
    return load_order







class ModPack(commands.Cog):
    def __init__(self, client: commands.Bot):
        self.client = client

    @app_commands.command(name="modpack", description="Description")
    async def modpack(
            self,
            interaction: discord.Interaction,
            html_file: discord.Attachment,
            op_date: str,
            modpack_name: str = None
    ):
        await interaction.response.defer(ephemeral=True)
        await interaction.followup.send(f"reading file... ", ephemeral=True)
        author = interaction.user

        if not modpack_name:
            modpack_name = html_file.filename.replace(".html", "")
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
        await interaction.followup.send(f"DLC: {western_sahara_dlc}  Mod: {western_sahara_mod}", ephemeral=True)

        if not western_sahara_dlc:
            # If the pack does not have the dlc, remove the compat if its there and add the dlc.
            if western_sahara_mod:
                new_pack_no_compat = remove_mod(html_content,
                                                "Western Sahara - Creator DLC Compatibility Data for Non-Owners")
                new_pack_dlc_no_compat = add_dlc(new_pack_no_compat, "Western Sahara",
                                                 "https://store.steampowered.com/app/1681170")
            else:
                new_pack_dlc_no_compat = add_dlc(html_content, "Western Sahara",
                                                 "https://store.steampowered.com/app/1681170")

            if isinstance(new_pack_dlc_no_compat, str):
                new_pack = new_pack_dlc_no_compat.encode('utf-8')
            file_with_dlc = discord.File(fp=io.BytesIO(new_pack_dlc_no_compat),
                                         filename=f"{modpack_name}_without_compat.html")
            modlist_file = discord.File(fp=io.BytesIO(new_pack_dlc_no_compat), filename=f"modlist.html")
        #  If we do have the dlc, remove the compat if there. dont add the dlc. (the input file is corect.)
        else:
            if western_sahara_mod:
                new_pack_no_compat = remove_mod(html_content,
                                                "Western Sahara - Creator DLC Compatibility Data for Non-Owners")
                new_pack_dlc_no_compat_str = add_dlc(new_pack_no_compat, "Western Sahara",
                                                     "https://store.steampowered.com/app/1681170")
            else:
                new_pack_dlc_no_compat_str = html_content

            if isinstance(html_content, str):
                html_content = html_content.encode('utf-8')
            file_with_dlc = discord.File(fp=io.BytesIO(new_pack_dlc_no_compat_str),
                                         filename=f"{modpack_name}_without_compat.html")
            modlist_file = discord.File(fp=io.BytesIO(new_pack_dlc_no_compat_str), filename=f"modlist.html")
        # If we don't have the mod, check if we have the dlc and remove it if we do, then add the mod
        if not western_sahara_mod:
            if western_sahara_dlc:
                new_pack_no_dlc = remove_dlc(html_content, "Western Sahara")
                new_pack_no_dlc_compat_str = add_mod(new_pack_no_dlc,
                                                     "Western Sahara - Creator DLC Compatibility Data for Non-Owners",
                                                     "https://steamcommunity.com/sharedfiles/filedetails/?id=2636962953")
            else:
                new_pack_no_dlc_compat_str = add_mod(html_content,
                                                     "Western Sahara - Creator DLC Compatibility Data for Non-Owners",
                                                     "https://steamcommunity.com/sharedfiles/filedetails/?id=2636962953")

            if isinstance(new_pack_no_dlc_compat_str, str):
                new_pack_no_dlc_compat_str = new_pack_no_dlc_compat_str.encode('utf-8')
            new_pack_no_dlc_compat = discord.File(fp=io.BytesIO(new_pack_no_dlc_compat_str),
                                                  filename=f"{modpack_name}_with_compat.html")

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

            new_pack_no_dlc_compat = discord.File(fp=io.BytesIO(new_pack_no_dlc_compat_str),
                                                  filename=f"{modpack_name}_with_compat.html")

        # Load order is old, new server doesn't need it. Now needs modpack.html

        # load_order = get_load_order(new_pack_no_dlc_compat_str)
        # if isinstance(load_order,str):
        #     load_order = load_order.encode("utf-8")
        # file_with_load_order = discord.File(fp=io.BytesIO(load_order),filename=f"{modpack_name} load order.txt")

        # await interaction.followup.send(content=f"Load order:",file=file_with_load_order,ephemeral=True)

        await interaction.followup.send(content=f"Upload this to the server!", file=modlist_file, ephemeral=True)
        await interaction.channel.send(
            content=f"[{op_date}] {modpack_name} **Without the compat**, make sure the western sahara dlc is loaded. Made by {author.mention}",
            file=file_with_dlc)
        await interaction.channel.send(
            content=f"[{op_date}] {modpack_name} **with the compat**, only loading the modpack is needed. Made by {author.mention}",
            file=new_pack_no_dlc_compat)


async def setup(client: commands.Bot):
    await client.add_cog(ModPack(client))