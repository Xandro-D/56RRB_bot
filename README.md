# 60RRB_bot

A Discord bot for the 60th Rifle Regiment Brigade with moderation and promotion features.

## Features

- **Moderation System**: Strike and warning system with automatic expiration
- **Promotion System**: Automatic rank promotions within different military branches
- **Role Management**: Automated role assignment and nickname updates
- **Fact Checking**: Fun fact-checking command with role-based responses

## Setup

1. **Environment Variables**: 
   - Copy `.env.example` to `.env`
   - Set your Discord bot token: `DISCORD_BOT_TOKEN=your_actual_token_here`

2. **Dependencies**:
   ```bash
   pip install discord.py
   ```

3. **Configuration**:
   - Update `hierarchy.json` with your server's role hierarchies
   - Update `GUILD_ID` in `bot.py` for your Discord server

## Security

This bot uses environment variables for sensitive data like bot tokens. Never commit actual tokens to version control.

## Commands

- `/strike @user` - Strike a user (expires in 6 months)
- `/remove_strike @user` - Remove a strike from a user
- `/warn @user` - Warn a user (converts to strike after 2 warnings)
- `/remove_warn @user` - Remove a warning from a user
- `/promote @user` - Promote a user within their branch
- `/info @user` - Display user's strikes and warnings
- `/reset @user` - Reset all strikes and warnings for a user
- `/factcheck` - Fun fact-checking command
