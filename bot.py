import discord
from discord import app_commands
from discord.ext import commands, tasks
import asyncio
from datetime import datetime, timedelta
import batting_analysis
import pitching_analysis
import getData
import io
import matplotlib.pyplot as plt
from search_player import search_player_by_name, get_player_by_id
import sqlite3

# Bot setup
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents)

# Store active player lookups
active_lookups = {}

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user.name}')
    try:
        print("Syncing commands...")
        synced = await bot.tree.sync()
        print(f"Synced {len(synced)} command(s)")
    except Exception as e:
        print(f"Failed to sync commands: {str(e)}")
    update_database.start()

@tasks.loop(hours=24)
async def update_database():
    """Update database daily"""
    print("Updating database...")
    getData.main()
    print("Database update complete!")

@bot.tree.command(name="pitcher", description="Set active pitcher for analysis")
async def set_pitcher(interaction: discord.Interaction, player_name: str):
    await interaction.response.defer()
    
    player_id = search_player_by_name(player_name)
    if not player_id:
        await interaction.followup.send(f"Could not find player: {player_name}")
        return
        
    player = get_player_by_id(player_id)
    if not player.pitchType:
        await interaction.followup.send(f"{player.playerName} is not a pitcher!")
        return
    
    # Update player's data
    conn = sqlite3.connect('baseball.db')
    try:
        await interaction.followup.send(f"Fetching data for {player.playerName}...")
        getData.getPlayerPitchingPlateAppearances(player_id, conn)
        getData.getPlayerBattingPlateAppearances(player_id, conn)
        conn.commit()
        
        # Verify we got data
        c = conn.cursor()
        c.execute('SELECT COUNT(*) FROM plate_appearances WHERE pitcherID = ?', (player_id,))
        count = c.fetchone()[0]
        if count == 0:
            await interaction.followup.send(f"No pitching data found for {player.playerName}")
            return
            
    except Exception as e:
        await interaction.followup.send(f"Error updating data: {str(e)}")
        return
    finally:
        conn.close()
    
    active_lookups[interaction.user.id] = {'type': 'pitcher', 'id': player_id}
    await interaction.followup.send(f"Set active pitcher to {player.playerName} with {count} plate appearances")

@bot.tree.command(name="batter", description="Set active batter for analysis")
async def set_batter(interaction: discord.Interaction, player_name: str):
    await interaction.response.defer()
    
    player_id = search_player_by_name(player_name)
    if not player_id:
        await interaction.followup.send(f"Could not find player: {player_name}")
        return
        
    player = get_player_by_id(player_id)
    
    # Update player's data
    conn = sqlite3.connect('baseball.db')
    try:
        await interaction.followup.send(f"Fetching data for {player.playerName}...")
        getData.getPlayerBattingPlateAppearances(player_id, conn)
        getData.getPlayerPitchingPlateAppearances(player_id, conn)
        conn.commit()
        
        # Verify we got data
        c = conn.cursor()
        c.execute('SELECT COUNT(*) FROM plate_appearances WHERE hitterID = ?', (player_id,))
        count = c.fetchone()[0]
        if count == 0:
            await interaction.followup.send(f"No batting data found for {player.playerName}")
            return
            
    except Exception as e:
        await interaction.followup.send(f"Error updating data: {str(e)}")
        return
    finally:
        conn.close()
    
    active_lookups[interaction.user.id] = {'type': 'batter', 'id': player_id}
    await interaction.followup.send(f"Set active batter to {player.playerName} with {count} plate appearances")

@bot.tree.command(name="pitcherdist", description="Show pitcher's distributions")
async def pitcher_dist(interaction: discord.Interaction):
    await interaction.response.defer()
    
    if not check_active_pitcher(interaction):
        return
    
    player_id = active_lookups[interaction.user.id]['id']
    player = get_player_by_id(player_id)
    
    plt.switch_backend('Agg')
    fig = pitching_analysis.plot_distributions(player_id)
    if fig is None:
        await interaction.followup.send("Error generating plot")
        return
        
    buffer = io.BytesIO()
    fig.savefig(buffer, format='png', bbox_inches='tight')
    plt.close(fig)
    buffer.seek(0)
    
    await interaction.followup.send(
        f"**Pitch Distributions for {player.playerName}**",
        file=discord.File(buffer, 'distributions.png')
    )

@bot.tree.command(name="pitchermatrices", description="Show pitcher's pattern matrices")
async def pitcher_matrices(interaction: discord.Interaction):
    await interaction.response.defer()
    
    if not check_active_pitcher(interaction):
        return
    
    player_id = active_lookups[interaction.user.id]['id']
    player = get_player_by_id(player_id)
    
    plt.switch_backend('Agg')
    fig = pitching_analysis.plot_matrices(player_id)
    if fig is None:
        await interaction.followup.send("Error generating plot")
        return
        
    buffer = io.BytesIO()
    fig.savefig(buffer, format='png', bbox_inches='tight')
    plt.close(fig)
    buffer.seek(0)
    
    await interaction.followup.send(
        f"**Pattern Matrices for {player.playerName}**",
        file=discord.File(buffer, 'matrices.png')
    )

@bot.tree.command(name="pitcherfirst", description="Show pitcher's first pitch trends")
async def pitcher_first(interaction: discord.Interaction):
    if not check_active_pitcher(interaction):
        await interaction.response.send_message("Please select a pitcher first using /pitcher")
        return
        
    await interaction.response.defer()
    
    player_id = active_lookups[interaction.user.id]['id']
    player = get_player_by_id(player_id)
    
    plt.switch_backend('Agg')
    fig = pitching_analysis.plot_first_pitch_trends(player_id)
    if fig is None:
        await interaction.followup.send("Error generating plot")
        return
        
    buffer = io.BytesIO()
    fig.savefig(buffer, format='png', bbox_inches='tight')
    plt.close(fig)
    buffer.seek(0)
    
    await interaction.followup.send(
        f"**First Pitch Analysis for {player.playerName}**",
        file=discord.File(buffer, 'first_pitches.png')
    )

@bot.tree.command(name="batterdist", description="Show batter's distributions")
async def batter_dist(interaction: discord.Interaction):
    if not check_active_batter(interaction):
        await interaction.response.send_message("Please select a batter first using /batter")
        return
        
    await interaction.response.defer()
    
    player_id = active_lookups[interaction.user.id]['id']
    player = get_player_by_id(player_id)
    
    plt.switch_backend('Agg')
    fig = batting_analysis.plot_distributions(player_id)
    if fig is None:
        await interaction.followup.send("Error generating plot")
        return
        
    buffer = io.BytesIO()
    fig.savefig(buffer, format='png', bbox_inches='tight')
    plt.close(fig)
    buffer.seek(0)
    
    await interaction.followup.send(
        f"**Swing Distributions for {player.playerName}**",
        file=discord.File(buffer, 'distributions.png')
    )

@bot.tree.command(name="battermatrices", description="Show batter's pattern matrices")
async def batter_matrices(interaction: discord.Interaction):
    if not check_active_batter(interaction):
        await interaction.response.send_message("Please select a batter first using /batter")
        return
        
    await interaction.response.defer()
    
    player_id = active_lookups[interaction.user.id]['id']
    player = get_player_by_id(player_id)
    
    plt.switch_backend('Agg')
    fig = batting_analysis.plot_matrices(player_id)
    if fig is None:
        await interaction.followup.send("Error generating plot")
        return
        
    buffer = io.BytesIO()
    fig.savefig(buffer, format='png', bbox_inches='tight')
    plt.close(fig)
    buffer.seek(0)
    
    await interaction.followup.send(
        f"**Pattern Matrices for {player.playerName}**",
        file=discord.File(buffer, 'matrices.png')
    )

@bot.tree.command(name="battersequence", description="Show batter's game sequences")
async def batter_sequence(interaction: discord.Interaction):
    await interaction.response.defer()
    
    if not check_active_batter(interaction):
        return
    
    player_id = active_lookups[interaction.user.id]['id']
    player = get_player_by_id(player_id)
    
    plt.switch_backend('Agg')
    fig = batting_analysis.plot_game_sequences_overlay(player_id)
    if fig is None:
        await interaction.followup.send("Error generating plot")
        return
        
    buffer = io.BytesIO()
    fig.savefig(buffer, format='png', bbox_inches='tight')
    plt.close(fig)
    buffer.seek(0)
    
    await interaction.followup.send(
        f"**Game Sequences for {player.playerName}**",
        file=discord.File(buffer, 'sequences.png')
    )

@bot.tree.command(name="pitchersequence", description="Show pitcher's game sequences")
async def pitcher_sequence(interaction: discord.Interaction):
    if not check_active_pitcher(interaction):
        await interaction.response.send_message("Please select a pitcher first using /pitcher")
        return
        
    await interaction.response.defer()
    
    player_id = active_lookups[interaction.user.id]['id']
    player = get_player_by_id(player_id)
    
    plt.switch_backend('Agg')
    fig = pitching_analysis.plot_game_sequences_overlay(player_id)
    if fig is None:
        await interaction.followup.send("Error generating plot")
        return
        
    buffer = io.BytesIO()
    fig.savefig(buffer, format='png', bbox_inches='tight')
    plt.close(fig)
    buffer.seek(0)
    
    await interaction.followup.send(
        f"**Game Sequences for {player.playerName}**",
        file=discord.File(buffer, 'sequences.png')
    )

@bot.tree.command(name="guesspitch", description="Predict pitcher's next pitch")
async def guess_pitch(interaction: discord.Interaction, prev_pitch: int = None, prev_diff: int = None):
    if not check_active_pitcher(interaction):
        await interaction.response.send_message("Please select a pitcher first using /pitcher")
        return
    
    player_id = active_lookups[interaction.user.id]['id']
    player = get_player_by_id(player_id)
    
    prediction, confidence, sample_size = pitching_analysis.predict_next_pitch(
        player_id, prev_pitch, prev_diff
    )
    
    if prediction is None:
        await interaction.response.send_message(
            f"Not enough data to make a prediction for {player.playerName}"
        )
        return
    
    # Format confidence as percentage
    confidence_pct = round(confidence * 100)
    
    # Create confidence description
    if confidence_pct >= 80:
        confidence_desc = "Very High"
    elif confidence_pct >= 60:
        confidence_desc = "High"
    elif confidence_pct >= 40:
        confidence_desc = "Moderate"
    elif confidence_pct >= 20:
        confidence_desc = "Low"
    else:
        confidence_desc = "Very Low"
    
    message = [
        f"**Pitch Prediction for {player.playerName}**",
        f"Predicted next pitch: **{prediction}**",
        f"Confidence: {confidence_pct}% ({confidence_desc})",
        f"Based on {sample_size} historical sequences",
    ]
    
    if prev_pitch:
        message.append(f"Previous pitch: {prev_pitch}")
    if prev_diff:
        message.append(f"Previous diff: {prev_diff}")
    
    message.append("\n*Prediction uses sliding window of 3 pitches and weights recent data more heavily*")
        
    await interaction.response.send_message("\n".join(message))

@bot.tree.command(name="guessswing", description="Predict batter's next swing")
async def guess_swing(interaction: discord.Interaction, prev_swing: int = None, prev_diff: int = None):
    if not check_active_batter(interaction):
        await interaction.response.send_message("Please select a batter first using /batter")
        return
    
    player_id = active_lookups[interaction.user.id]['id']
    player = get_player_by_id(player_id)
    
    prediction, confidence, sample_size = batting_analysis.predict_next_swing(
        player_id, prev_swing, prev_diff
    )
    
    if prediction is None:
        await interaction.response.send_message(
            f"Not enough data to make a prediction for {player.playerName}"
        )
        return
    
    # Format confidence as percentage
    confidence_pct = round(confidence * 100)
    
    # Create confidence description
    if confidence_pct >= 80:
        confidence_desc = "Very High"
    elif confidence_pct >= 60:
        confidence_desc = "High"
    elif confidence_pct >= 40:
        confidence_desc = "Moderate"
    elif confidence_pct >= 20:
        confidence_desc = "Low"
    else:
        confidence_desc = "Very Low"
    
    message = [
        f"**Swing Prediction for {player.playerName}**",
        f"Predicted next swing: **{prediction}**",
        f"Confidence: {confidence_pct}% ({confidence_desc})",
        f"Based on {sample_size} historical sequences",
    ]
    
    if prev_swing:
        message.append(f"Previous swing: {prev_swing}")
    if prev_diff:
        message.append(f"Previous diff: {prev_diff}")
    
    message.append("\n*Prediction uses sliding window of 3 swings and combines player & team patterns*")
        
    await interaction.response.send_message("\n".join(message))

def check_active_pitcher(interaction):
    """Check if user has an active pitcher selected"""
    if interaction.user.id not in active_lookups or active_lookups[interaction.user.id]['type'] != 'pitcher':
        return False
    return True

def check_active_batter(interaction):
    """Check if user has an active batter selected"""
    if interaction.user.id not in active_lookups or active_lookups[interaction.user.id]['type'] != 'batter':
        return False
    return True

@bot.tree.command(name="update", description="Force update the database")
@app_commands.checks.has_permissions(administrator=True)
async def update(interaction: discord.Interaction):
    await interaction.response.defer()
    getData.main()
    await interaction.followup.send("Database updated!")

@bot.tree.command(name="sync", description="Force sync all slash commands")
@app_commands.checks.has_permissions(administrator=True)
async def sync_commands(interaction: discord.Interaction):
    """Force sync all slash commands"""
    await interaction.response.defer()
    try:
        synced = await bot.tree.sync()
        await interaction.followup.send(f"Synced {len(synced)} command(s)!")
    except Exception as e:
        await interaction.followup.send(f"Failed to sync commands: {str(e)}")

@bot.command()
@commands.is_owner()  # Only bot owner can use this
async def sync(ctx):
    """Sync all slash commands to the current guild"""
    try:
        await bot.tree.sync()
        await ctx.send("Commands synced!")
    except Exception as e:
        await ctx.send(f"Failed to sync commands: {str(e)}")

def run_bot():
    with open('token.txt', 'r') as f:
        token = f.read().strip()
    bot.run(token)

if __name__ == "__main__":
    run_bot() 