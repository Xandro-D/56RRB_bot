# 56RRB Bot

A Discord bot built for the 56th Rapid Response Brigade. It handles moderation, promotions, role management, server status tracking, Arma 3 modpack processing, and Google Sheets integration.

## Features

### Moderation
- Issue and remove strikes (expire after 6 months) and warnings
- Warnings automatically convert to a strike after 5 accumulated warnings
- View and reset a user's moderation record

### Promotions
- Promote up to 10 users at once across four branches: Ground Forces, NCO, Air Force, and Armor
- Automatically updates Discord roles and nickname prefixes on promotion
- Enforces a 7-day promotion cooldown per user
- Suggests Bravo or Charlie squad assignment based on current squad sizes after promotion

### Role Management
- Reaction-based self-assignment: users react to a configured message to pick up a role
- 7-day cooldown between role changes
- Reacting with the reset emoji removes all tracked roles
- Expired cooldowns are cleaned up automatically

### BCT (Basic Combat Training)
- Remind members who still need a BCT via direct message
- Review and optionally kick members who have been in the server for over 2 months without completing onboarding

### Server Status
- Automatically updates a "server-status" channel every 10 minutes with live player count and current mission

### Arma 3 Modpack Tools
- Process a modpack HTML file to produce two variants: one for players with the Western Sahara DLC and one using the compatibility mod
- Upload a mission file or modpack directly to the Arma 3 server via SFTP, with an optional server restart through the Pterodactyl panel

### Google Sheets Integration
- Export Bravo and Charlie squad member data to a Google Sheet
- Tracks specialized roles: Combat Life Saver, Anti Tank, Combat Engineer, International Scientific Group

## Prerequisites

- Python 3.8 or higher
- A Discord bot token with a bot application in the Discord developer portal
- A Discord server with appropriate permissions granted to the bot
- (Optional) Google Cloud project with Sheets API enabled
- (Optional) Pterodactyl panel and SFTP access for server file uploads

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/Xandro-Diels/56RRB_bot.git
   cd 56RRB_bot
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Configure environment variables by copying `.env.example` to `.env` and filling in all values:
   ```env
   DISCORD_GUILD_ID=your_guild_id
   DISCORD_BOT_TOKEN=your_bot_token
   DISCORD_MSG_ID=your_reaction_message_id
   DISCORD_CHANNEL_ID=your_reaction_channel_id

   # Arma 3 server status
   SERVER_IP=your_server_ip
   SERVER_PORT=your_server_port

   # SFTP / Pterodactyl (for upload_main)
   SFTP_IP=your_sftp_ip
   SFTP_PORT=your_sftp_port
   SFTP_USERNAME=your_sftp_user
   SFTP_PASSWORD=your_sftp_password
   PTERO_API_KEY=your_pterodactyl_api_key
   PTERO_SERVER_ID=your_pterodactyl_server_id
   ```

4. Configure the bot by editing `data.json` to match your server's role structure:
   - Role hierarchies and prefixes for each branch (Ground, NCO, Air Force, Armor)
   - Authorized admin roles
   - Reaction-to-role mappings (emoji to role name)
   - Fact check response lists

5. (Optional) Set up Google Sheets integration:
   - Enable the Google Sheets API in Google Cloud Console
   - Download OAuth 2.0 credentials as `credentials.json` and place it in the project directory
   - Update the spreadsheet ID in `modules/googleapi.py`
   - On first run the bot will prompt for authentication and save `token.json` for future runs

## Required Bot Permissions

- Manage Roles
- Manage Nicknames
- Kick Members
- Send Messages
- Read Message History
- Add Reactions
- Use Slash Commands

## Running the Bot

```bash
python bot.py
```

On startup the bot will:
1. Load all command modules from `modules/commands/`
2. Sync slash commands to the configured guild
3. Add reactions to the configured reaction-roles message
4. Start the server status tracking loop
5. Begin processing commands and events

## Commands

### Moderation

| Command | Arguments | Description | Permission |
|---|---|---|---|
| `/strike` | `@user` `reason` | Issue a strike to a user. Strikes expire after 6 months. If the user reaches 3 or more strikes the bot flags them for a ban. | Admin |
| `/remove_strike` | `@user` | Remove one strike from a user. | Admin |
| `/warn` | `@user` `reason` | Issue a warning. Once a user accumulates 5 warnings they are automatically struck and their warnings are reset. | Admin |
| `/remove_warn` | `@user` | Remove one warning from a user. | Admin |
| `/info` | `@user` | Show the current strike and warning count for a user. | Everyone |
| `/reset` | `@user` | Clear all strikes and warnings for a user. | Admin |

### Promotions

| Command | Arguments | Description | Permission |
|---|---|---|---|
| `/promote` | `@user1` (up to `@user10`) | Promote up to 10 users. The bot determines each user's branch automatically, advances their role, updates their nickname prefix, and applies a 7-day promotion cooldown. Ground force members at rank index 3 or higher require training roles before being promoted. After promotion the bot suggests Bravo or Charlie squad to users who are not yet in a squad. | Admin |

### BCT and Onboarding

| Command | Arguments | Description | Permission |
|---|---|---|---|
| `/bct_training` | - | Send a direct message to every member who still needs a BCT, directing them to the installation guide and BCT request channel. | Admin |
| `/bct_check` | - | Scan all members who do not have the Member role and joined more than 60 days ago. For each one, the bot presents a prompt to kick or skip them. | Admin |

### Arma 3 Server Tools

| Command | Arguments | Description | Permission |
|---|---|---|---|
| `/modpack` | `html_file` `op_date` `modpack_name` (optional) | Parse a modpack HTML export file and produce two output files: one for players who own the Western Sahara DLC and one that uses the compatibility mod instead. Both files are posted to the channel. | Admin |
| `/upload_main` | `mission` (optional) `modpack` (optional) | Upload a mission file to the server's `mpmissions` folder and/or replace the server's `modlist.html` over SFTP. After a modpack upload the bot asks whether to restart the server via Pterodactyl. | Admin |

### Role and Training Utilities

| Command | Arguments | Description | Permission |
|---|---|---|---|
| `/whoisin` | `@role1` `@role2` (optional) `@role3` (optional) | List all members in each of the specified roles. Response is ephemeral (visible only to you). | Everyone |
| `/whoisinboth` | `@role1` `@role2` | List all members who have both roles at the same time. Response is ephemeral. | Everyone |
| `/check_roles` | `@role` | For every member of the given role who is at ground force rank index 3 or higher, show which required training roles they are still missing. | Admin |
| `/factcheck` | - | Returns a random response. Admins receive a positive response; everyone else receives a negative one. | Everyone |
| `/sheet` | - | Export current Bravo and Charlie squad member data to the configured Google Sheet, including Combat Life Saver, Anti Tank, Combat Engineer, and International Scientific Group role status. | Admin |

### Reaction Roles (Automatic)

Users interact with a designated message in a configured channel to self-assign roles. Reacting with a mapped emoji assigns the corresponding role and removes any previously held reaction roles. Reacting with the reset emoji removes all tracked roles. A 7-day cooldown is enforced between role changes.

### Server Status (Automatic)

The bot queries the Arma 3 server using the A2S protocol every 10 minutes and updates a single message in the `server-status` channel with the current player list and active mission name.

## Database

The bot uses a local SQLite database to track:
- Strikes per user with expiration timestamps (6 months)
- Warnings per user
- Promotion cooldowns per user (7 days)
- Reaction role cooldowns per user (7 days)

## Project Structure

```
56RRB_bot/
├── bot.py                       # Entry point, loads all modules
├── data.json                    # Role hierarchies, prefixes, admin roles, reaction mappings
├── .env.example                 # Environment variable template
├── modules/
│   ├── config.py                # Reads environment variables
│   ├── database.py              # SQLite operations for moderation and cooldown tracking
│   ├── googleapi.py             # Google Sheets API integration
│   ├── json_reader.py           # Reads data.json into module-level constants
│   ├── utils.py                 # Shared helpers (admin check, role checks)
│   ├── commands/
│   │   ├── moderation.py        # strike, remove_strike, warn, remove_warn, info, reset
│   │   ├── promote.py           # promote
│   │   ├── bct_training.py      # bct_training
│   │   ├── bct_check.py         # bct_check
│   │   ├── whoisin.py           # whoisin, whoisinboth
│   │   ├── check_role.py        # check_roles
│   │   ├── factcheck.py         # factcheck
│   │   ├── sheet.py             # sheet
│   │   ├── modpack.py           # modpack
│   │   ├── upload.py            # upload_main
│   │   ├── reactionroles.py     # reaction role event listeners
│   │   └── server_tracking.py   # server status background loop
│   └── ui/
│       └── confirm_view.py      # Confirm/skip button view
```

## Security Notes

- Never commit your `.env` file to version control.
- Keep your `DISCORD_BOT_TOKEN` and all credentials secret.
- Do not commit `credentials.json` or `token.json`.
- Do not commit `sftp_password`, `ptero_api_key`, or any other secrets. Use environment variables exclusively.
- Review authorized admin roles in `data.json` regularly.

## Support

For issues or questions about the bot, contact the server administrators or open an issue in this repository.
