from dotenv import load_dotenv
import os

load_dotenv()

GUILD_ID = int(os.getenv("DISCORD_GUILD_ID"))
bot_token = os.getenv("DISCORD_BOT_TOKEN")
discord_msg_id = int(os.getenv("DISCORD_MSG_ID"))
discord_channel_id = int(os.getenv("DISCORD_CHANNEL_ID"))


# Arma server tracking.
server_ip = str(os.getenv("SERVER_IP"))
server_port = int(os.getenv("SERVER_PORT"))

# Arma server sftp
sftp_ip = str(os.getenv("SFTP_IP"))
sftp_port = int(os.getenv("SFTP_PORT"))
sftp_user = os.getenv("SFTP_USERNAME")
sftp_password = os.getenv("SFTP_PASSWORD")
ptero_api_key = os.getenv("PTERO_API_KEY")