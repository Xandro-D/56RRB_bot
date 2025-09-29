# 60RRB_bot

A Discord moderation and role management bot designed for military-themed servers. This bot provides comprehensive moderation tools including strikes, warnings, and automatic role promotions across different military branches.

## Features

- **Moderation System**: Strike and warning system with automatic expiration
- **Role Hierarchy Management**: Support for Ground, NCO, Air, and Armor branches
- **Promotion System**: Automatic role promotions within branch hierarchies  
- **Member Onboarding**: Draft new members with appropriate roles and nicknames
- **Administrative Controls**: Role-based command authorization
- **Database Integration**: SQLite database for persistent moderation records

## Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/Xandro-Diels/60RRB_bot.git
   cd 60RRB_bot
   ```

2. **Install dependencies:**
   ```bash
   pip install discord.py
   ```

3. **Configure the bot:**
   - Update the bot token in `bot.py` (line 217)
   - Modify `hierarchy.json` to match your server's role structure
   - Ensure your Discord server has the roles defined in `hierarchy.json`

4. **Run the bot:**
   ```bash
   python bot.py
   ```

## Commands

All commands use the `!` prefix and require appropriate permissions.

### Moderation Commands

#### Strike System
- **`!strike @user`** - Issues a strike to the mentioned user (expires after ~6 months)
- **`!remove_strike @user`** - Removes the oldest strike from the mentioned user

#### Warning System  
- **`!warn @user`** - Issues a warning to the mentioned user
- **`!remove_warn @user`** - Removes a warning from the mentioned user

### Role Management

#### Promotions
- **`!promote @user`** - Promotes user to the next rank within their branch
- **`!demote @user`** - *(Work in Progress)* Demotes user within their branch

#### Member Onboarding
- **`!doc @user nickname`** - Assigns "Waiting for BCT" role and sets nickname for new members

### Information Commands
- **`!info @user`** - Displays strike and warning information for the mentioned user
- **`!reset @user`** - Resets all strikes and warnings for the mentioned user
- **`!factcheck`** - Fun command that returns random "fact check" responses

## Role Hierarchy

The bot supports four military branches with defined hierarchies:

### Ground Branch
- Private Third Class (PV3.)
- Private Second Class (PV2.) 
- Private First Class (PFC.)
- Specialist Third Class (SP3.)
- Specialist Second Class (SP2.)
- Specialist First Class (SP1.)
- Master Specialist (MSP.)
- First Specialist (FSP.)
- Specialist Major (SPM.)

### NCO Branch
- Corporal (CPL.)
- Sergeant (SGT.)
- Staff Sergeant (SSG.)
- Sergeant First Class (SFC.)
- Master Sergeant (MSG.)

### Air Branch
- Airman Basic (AMB.)
- Airman (AMN.)
- Airman 1st Class (AFC.)
- Airman Specialist (AMS.)
- Senior Airman (SRA.)
- Staff Sergeant (SSG.)
- Technical Sergeant (TSG.)
- Master Sergeant (MSG.)

### Armor Branch
- Crewman (CMN.)
- Technical Crewman (TCMD.)
- Armor Sergeant (ASGT.)
- Armor Staff Sergeant (ASSG.)
- Gunnery Sergeant (GYSGT.)

## Configuration

### hierarchy.json
This file contains all role hierarchies, prefixes, and configuration data:
- `GROUND_ROLE_HIERARCHY`: Array of ground branch roles
- `NCO_ROLE_HIERARCHY`: Array of NCO branch roles  
- `AIR_ROLE_HIERARCHY`: Array of air branch roles
- `ARMOR_ROLE_HIERARCHY`: Array of armor branch roles
- `AUTHORIZED_ROLES`: Roles that can use admin commands (default: "Admin")
- `SILLY_FACT_CHECK_POSITIVE/NEGATIVE`: Random responses for the factcheck command

### Database
The bot uses SQLite (`moderation.db`) to store:
- User warnings (persistent)
- User strikes (with expiration timestamps)

## Permissions

Commands are restricted based on Discord roles:
- **Admin Commands**: Users with roles listed in `AUTHORIZED_ROLES` 
- **Info Command**: Available to all users
- **Fact Check**: Available to all users (responses vary by permission level)

## Development

### File Structure
- `bot.py` - Main bot code with all commands and logic
- `database.py` - Database operations for moderation records
- `hierarchy.json` - Role hierarchy and configuration data
- `commands.txt` - Quick reference for available commands

### Key Functions
- `admin_check(ctx)` - Verifies user has admin permissions  
- `promotion(user_ranks, target, branch, prefix_type, ctx)` - Handles role promotions
- Database operations in `ModerationDatabase` class

## Troubleshooting

### Common Issues
1. **Bot not responding**: Check bot token and ensure bot is online
2. **Permission errors**: Verify user has required roles in `AUTHORIZED_ROLES`
3. **Role promotion fails**: Ensure Discord server has exact role names from `hierarchy.json`
4. **Database errors**: Check file permissions for `moderation.db`

### Bot Permissions Required
The bot needs the following Discord permissions:
- Send Messages
- Manage Roles  
- Manage Nicknames
- Read Message History
- Use Slash Commands

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly with a test Discord server
5. Submit a pull request

## License

This project is provided as-is for military simulation communities.
