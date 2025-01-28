# MLR Scout Bot

## Overview
A Discord bot for analyzing MLR player patterns and tendencies.

## Setup
1. Install requirements:
```bash
pip install discord.py matplotlib numpy requests tabulate
```

2. Create token.txt with your Discord bot token

3. Run initial database setup:
```bash
python getData.py
```

4. Start the bot:
```bash
python bot.py
```

## Commands
### Player Selection
- `/pitcher [player_name]` - Set active pitcher for analysis
- `/batter [player_name]` - Set active batter for analysis

### Pitcher Analysis
- `/pitcherdist` - Show pitcher's distributions
- `/pitchermatrices` - Show pitcher's pattern matrices
- `/pitcherfirst` - Show pitcher's first pitch trends

### Batter Analysis
- `/batterdist` - Show batter's distributions
- `/battermatrices` - Show batter's pattern matrices
- `/battersequence` - Show batter's game sequences

### Admin
- `/update` - Force update database (admin only)

## Features
- Automatic daily database updates
- Batting analysis
- Pitching analysis
- Visual charts and distributions
- Pattern matrices

## Bot Setup

### Creating the Bot Application
1. Go to [Discord Developer Portal](https://discord.com/developers/applications)
2. Click "New Application"
3. Give your bot a name
4. Go to the "Bot" section
5. Click "Add Bot"
6. Copy the token and paste it into `token.txt`
7. Under "Privileged Gateway Intents", enable "Message Content Intent"

### Adding Bot to Server
1. Go to OAuth2 > URL Generator
2. Select scopes:
   - `bot`
   - `applications.commands`
3. Select bot permissions:
   - `Send Messages`
   - `Attach Files`
   - `Use Slash Commands`
   - `Read Messages/View Channels`
4. Copy generated URL
5. Open URL in browser
6. Select server and authorize

### Running the Bot
1. Follow setup instructions above
2. Run `python bot.py`
3. Bot should appear online in your server
4. Use `/scout [player_name]` to analyze players