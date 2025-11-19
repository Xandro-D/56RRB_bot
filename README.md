# 56RRB Bot

A comprehensive Discord bot built for the 56th rapid respondse Brigade featuring automated moderation, promotion systems, role management, squad assignment capabilities, and Google Sheets integration.

## Features

### 🛡️ Moderation System
- **Strike System**: Issue strikes to users that automatically expire after 6 months
- **Warning System**: Issue warnings that convert to strikes after 2 warnings (automatic conversion)
- **User Info Tracking**: View strikes and warnings for any user
- **Reset Capabilities**: Reset user moderation records when needed
- **Automatic Expiration**: All moderation records include automatic expiration handling

### 🎖️ Promotion System
- **Multi-Branch Support**: Automatic rank promotions across four military branches:
  - Ground Forces
  - NCO (Non-Commissioned Officers)
  - Air Force
  - Armor Division
- **Cooldown Management**: 7-day promotion cooldowns to prevent abuse
- **Automatic Role Updates**: Seamlessly updates Discord roles and nicknames with proper rank prefixes
- **Batch Promotions**: Promote up to 10 users simultaneously
- **Smart Squad Suggestions**: Automatically suggests squad assignments (Bravo/Charlie) based on current squad sizes

### 👥 Role Management
- **Reaction-Based Assignment**: Users can self-assign roles via message reactions
- **Role Cooldowns**: 7-day cooldown between role changes
- **Smart Reset**: Remove all tracked roles with a single reaction
- **Automatic Cleanup**: Expired role cooldowns are automatically removed

### 📊 Google Sheets Integration
- **Automated Data Export**: Export squad member information to Google Sheets
- **Role Tracking**: Track specialized roles (Combat Life Saver, Anti Tank, Combat Engineer)
- **Squad Organization**: Separate sections for Bravo and Charlie squads
- **Visual Indicators**: Uses ✅/❌ to show which members have which specialized roles

### 🔧 Utility Commands
- **Who's In**: List all members with specific role(s)
- **Who's In Both**: Find members with multiple specified roles
- **Fact Check**: Fun command with role-based responses

## Prerequisites

- Python 3.8+
- Discord.py library
- A Discord Bot Token
- Discord Server (Guild) with appropriate permissions
- (Optional) Google Cloud project with Sheets API enabled for spreadsheet integration

## Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/Xandro-Diels/56RRB_bot.git
   cd 56RRB_bot
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure environment variables**
   - Copy `.env.example` to `.env`
   - Fill in your Discord bot credentials:
     ```env
     DISCORD_GUILD_ID=your_guild_id
     DISCORD_BOT_TOKEN=your_bot_token
     DISCORD_MSG_ID=your_reaction_message_id
     DISCORD_CHANNEL_ID=your_reaction_channel_id
     ```

4. **Configure role hierarchies**
   - Edit `hierarchy.json` to match your server's role structure
   - Set up authorized admin roles
   - Configure branch hierarchies and prefixes
   - Define reaction-to-role mappings

5. **(Optional) Set up Google Sheets integration**
   - Create a Google Cloud project and enable the Google Sheets API
   - Download `credentials.json` and place it in the bot directory
   - Update the `SPREADSHEET_ID` in `googleapi.py` with your Google Sheet ID

## Configuration

### hierarchy.json Structure
The bot uses `hierarchy.json` to define:
- Role hierarchies for each military branch (Ground, NCO, Air Force, Armor)
- Role prefixes for nickname formatting
- Authorized admin roles
- Fact check responses
- Reaction-to-role mappings (emoji -> role name dictionary)

### Required Bot Permissions
- Manage Roles
- Manage Nicknames
- Send Messages
- Read Message History
- Add Reactions
- Use Slash Commands

## Commands

### Moderation Commands
| Command                | Description                                 | Permission Required |
|------------------------|---------------------------------------------|---------------------|
| `/strike @user`        | Issue a strike (expires in 6 months)        | Admin Role          |
| `/remove_strike @user` | Remove one strike from a user               | Admin Role          |
| `/warn @user`          | Issue a warning (2 warnings = 1 strike)     | Admin Role          |
| `/remove_warn @user`   | Remove one warning from a user              | Admin Role          |
| `/info @user`          | Display user's current strikes and warnings | Everyone            |
| `/reset @user`         | Reset all strikes and warnings for a user   | Admin Role          |

### Promotion Commands
| Command                         | Description                                | Permission Required |
|---------------------------------|--------------------------------------------|---------------------|
| `/promote @user1 [@user2...]`   | Promote up to 10 users within their branch | Admin Role          |
| `/reset_promote_cooldown @user` | Reset promotion cooldown for a user        | Admin Role          |

### Utility Commands
| Command                             | Description                                    | Permission Required |
|-------------------------------------|------------------------------------------------|---------------------|
| `/whoisin @role1 [@role2] [@role3]` | List members in specified role(s) (ephemeral)  | Everyone            |
| `/whoisinboth @role1 @role2`        | List members who have both roles (ephemeral)   | Everyone            |
| `/factcheck`                        | Fun fact-checking command with role responses  | Everyone            |
| `/sheet`                            | Update Google Sheets with squad role data     | Admin Role          |

## Usage

Run the bot with:
```bash
python bot.py
```

The bot will:
1. Connect to Discord
2. Sync slash commands to your guild
3. Set up reaction listeners on the configured message
4. Begin processing commands
5. Initialize the SQLite database for moderation tracking

## Database

The bot uses a local SQLite database (`database.py`) to track:
- User strikes with expiration timestamps (6 months)
- User warnings (reset when converted to strikes)
- Promotion cooldowns (7 days)
- Role change cooldowns (7 days)

All moderation data includes automatic expiration handling and cleanup.

## Google Sheets Integration

The `/sheet` command exports squad member data to a Google Sheet with the following format:
- Squad name headers (Bravo, Charlie)
- Member display names
- Role indicators for Combat Life Saver, Anti Tank, and Combat Engineer
- Visual ✅/❌ indicators for easy reading

**Setup Requirements:**
1. Enable Google Sheets API in Google Cloud Console
2. Download OAuth 2.0 credentials as `credentials.json`
3. First run will prompt for authentication
4. `token.json` will be created for subsequent runs

## Security Notes

⚠️ **Important Security Information:**
- Never commit your `.env` file to version control
- Keep your `DISCORD_BOT_TOKEN` secret
- Do not commit `credentials.json` or `token.json` (Google API credentials)
- Regularly review authorized admin roles in `hierarchy.json`
- The bot requires elevated permissions - use appropriate role hierarchy settings in Discord

## Project Structure

```
56RRB_bot/
├── bot.py              # Main bot logic and command handlers
├── database.py         # Database operations and moderation tracking
├── googleapi.py        # Google Sheets API integration
├── hierarchy.json      # Role configurations and server settings
├── .env.example        # Environment variable template
├── .env               # Your actual configuration (not committed)
├── .gitignore         # Git ignore rules
├── requirements.txt   # Python dependencies
├── credentials.json   # Google API credentials (not committed)
├── token.json         # Google API token (not committed, auto-generated)
└── README.md          # This file
```

## Contributing

This is a private repository for the 56th rapid response Brigade. If you have suggestions or find bugs, please contact the repository owner.

## Support

For issues or questions about the bot, please contact the server administrators or open an issue in this repository.

---

**Last Updated**: November 2025
