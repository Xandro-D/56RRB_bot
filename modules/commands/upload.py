import os
import discord
from discord import app_commands
from discord.ext import commands
from modules import utils
from ptero import PteroControl, Panel
import paramiko
import io
from modules.config import sftp_password, sftp_user, sftp_port,sftp_ip,ptero_api_key
from modules.ui import confirm_view

SERVER_ID = "95635e32-7745-45ee-bae6-2ec458113233"


async def upload_file(attachment, host=sftp_ip, port=sftp_port, username=sftp_user, password=sftp_password, remote_dir="/"):
    # Download file from Discord into memory
    data = await attachment.read()
    file_obj = io.BytesIO(data)

    # Connect to SFTP
    transport = paramiko.Transport((host, port))
    transport.connect(username=username, password=password)
    sftp = paramiko.SFTPClient.from_transport(transport)

    try:
        remote_path = f"{remote_dir}/{attachment.filename}"
        sftp.putfo(file_obj, remote_path)
    finally:
        sftp.close()
        transport.close()


# IMPORTANT: move these to environment variables in production
panel = Panel(
    id="main",
    base_url=os.getenv("PTERO_BASE_URL", "http://65.109.37.23/api"),
    client_key=os.getenv("PTERO_CLIENT_KEY", ptero_api_key),
)

ptero = PteroControl([panel])


class Upload(commands.Cog):
    def __init__(self, client: commands.Bot):
        self.client = client
        self._ptero_ready = False

    @app_commands.command(
        name="upload_main",
        description="Upload a modpack to the main server.",
    )
    async def upload_main(
        self,
        interaction: discord.Interaction,
        mission: discord.Attachment = None,
        modpack: discord.Attachment = None,
    ):
        if not await utils.admin_check(interaction):
            return

        await interaction.response.defer(ephemeral=True)

        try:

            if mission:
                await upload_file(attachment=mission,remote_dir="/mpmissions")
                await interaction.followup.send(
                    f"Uploaded `{mission.filename}`",
                    ephemeral=True,
                )

            if modpack:
                modpack.filename = "modlist.html"
                await upload_file(modpack)
                await interaction.followup.send(
                    f"Uploaded `{modpack}` as modlist.html to server",
                    ephemeral=True,
                )
                view = confirm_view.ConfirmView(
                    "Restart",
                    "Keep running"
                )
                await interaction.followup.send(
                    content=(
                        f"Do you want to restart the server?"
                    ),
                    view=view,
                    ephemeral=True
                )
                await view.wait()
                if not view.value:
                    await interaction.followup.send(f"Not restarting!", ephemeral=True)

                if view.value:
                    await interaction.followup.send("Sending restart command!",ephemeral=True)
                    server = await ptero.get_server(SERVER_ID)
                    await server.restart()
                    await interaction.followup.send("Restart command send !",ephemeral=True)



        except Exception as e:
            await interaction.followup.send(
                f"Upload failed: `{e}`",
                ephemeral=True,
            )


async def setup(client: commands.Bot):
    await client.add_cog(Upload(client))