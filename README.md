# 60RRB Bot

A comprehensive Discord bot built for the 60th Rifle Regiment Brigade featuring automated moderation, promotion systems, role management, and squad assignment capabilities.

## Features

### 🛡️ Moderation System
- **Strike System**: Issue strikes to users that automatically expire after 6 months
- **Warning System**: Issue warnings that convert to strikes after 2 warnings
- **User Info Tracking**: View strikes and warnings for any user
- **Reset Capabilities**: Reset user moderation records when needed

### 🎖️ Promotion System
- **Multi-Branch Support**: Automatic rank promotions across four military branches:
  - Ground Forces
  - NCO (Non-Commissioned Officers)
  - Air Force
  - Armor Division
- **Cooldown Management**: 7-day promotion cooldowns to prevent abuse
- **Automatic Role Updates**: Seamlessly updates Discord roles and nicknames
- **Batch Promotions**: Promote up to 10 users simultaneously

### 👥 Role Management
- **Reaction-Based Assignment**: Users can self-assign roles via message reactions
- **Squad Auto-Assignment**: Automatically suggests squad assignments (Bravo/Charlie)
- **Role Cooldowns**: 7-day cooldown between role changes
- **Smart Reset**: Remove all tracked roles with a single reaction

### 📊 Utility Commands
- **Who's In**: List all members with specific role(s)
- **Who's In Both**: Find members with multiple specified roles
- **Fact Check**: Fun command with role-based responses

## Prerequisites

- Python 3.8+
- Discord.py library
- A Discord Bot Token
- Discord Server (Guild) with appropriate permissions

## Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/Xandro-Diels/60RRB_bot.git
   cd 60RRB_bot
   ```

2. **Install dependencies**
   ```bash
   pip install discord.py python-dotenv
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

## Configuration

### hierarchy.json Structure
The bot uses `hierarchy.json` to define:
- Role hierarchies for each military branch
- Role prefixes for nickname formatting
- Authorized admin roles
- Fact check responses
- Reaction-to-role mappings

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
| Command                             | Description                       | Permission Required |
|-------------------------------------|-----------------------------------|---------------------|
| `/whoisin @role1 [@role2] [@role3]` | List members in specified role(s) | Everyone            |
| `/whoisinboth @role1 @role2`        | List members who have both roles  | Everyone            |
| `/factcheck`                        | Fun fact-checking command         | Everyone            |

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

## Database

The bot uses a local SQLite database (`database.py`) to track:
- User strikes with expiration timestamps
- User warnings
- Promotion cooldowns
- Role change cooldowns

All moderation data includes automatic expiration handling.

## Security Notes

⚠️ **Important Security Information:**
- Never commit your `.env` file to version control
- Keep your `DISCORD_BOT_TOKEN` secret
- Regularly review authorized admin roles in `hierarchy.json`
- The bot requires elevated permissions - use appropriate role hierarchy settings in Discord

## Project Structure

```
60RRB_bot/
├── bot.py              # Main bot logic and command handlers
├── database.py         # Database operations and moderation tracking
├── hierarchy.json      # Role configurations and server settings
├── .env.example        # Environment variable template
├── .env               # Your actual configuration (not committed)
└── README.md          # This file
```

## Contributing

This is a private repository for the 60th Rifle Regiment Brigade. If you have suggestions or find bugs, please contact the repository owner.

## License

Private - All rights reserved

## Support

For issues or questions about the bot, please contact the server administrators or open an issue in this repository.