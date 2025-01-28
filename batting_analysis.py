import sqlite3
from collections import defaultdict
import matplotlib.pyplot as plt
import numpy as np
from search_player import get_player_batting_pas_by_id, get_player_by_id
from helpers import get_result_color, calculate_delta
import statistics
from getData import PlateAppearance

def get_swing_distribution(player_id):
    """Returns distribution of swings in 200-number buckets"""
    pas = get_player_batting_pas_by_id(player_id)
    buckets = defaultdict(int)
    
    # Initialize all buckets from 1-1000 in steps of 200
    for i in range(0, 1001, 100):
        buckets[i] = 0
    
    for pa in pas:
        if pa.swing is not None:
            bucket = ((pa.swing - 1) // 100) * 100
            bucket = max(0, min(900, bucket))  # Clamp to 0-900
            buckets[bucket] += 1
    
    total = sum(buckets.values())
    if total == 0:
        return {}
    
    return {bucket: (count/total)*100 for bucket, count in sorted(buckets.items())}

def get_delta_history(player_id):
    """Returns chronological list of deltas between consecutive swings"""
    pas = get_player_batting_pas_by_id(player_id)
    # Sort by paID to get chronological order
    sorted_pas = sorted(pas, key=lambda x: x.paID)
    
    deltas = []
    for i in range(len(sorted_pas)-1):
        pa1 = sorted_pas[i]
        pa2 = sorted_pas[i+1]
        if pa1.swing is not None and pa2.swing is not None:
            delta = calculate_delta(pa1.swing, pa2.swing)
            deltas.append(delta)
    
    return deltas

def get_first_swings(player_id):
    """Returns list of first swings in each game"""
    pas = get_player_batting_pas_by_id(player_id)
    games = defaultdict(list)
    
    # Group PAs by game
    for pa in pas:
        if pa.gameID and pa.swing:
            games[pa.gameID].append(pa)
    
    # Get first PA from each game
    first_swings = []
    for game_pas in games.values():
        sorted_game_pas = sorted(game_pas, key=lambda x: x.paID)
        if sorted_game_pas:
            first_swings.append(sorted_game_pas[0].swing)
    
    return first_swings

def get_delta_distribution(player_id):
    """Returns distribution of deltas in 50-number buckets from -450 to 500"""
    deltas = get_delta_history(player_id)
    buckets = defaultdict(int)
    
    # Initialize buckets from -450 to 450 in steps of 50, plus special 451-500 bucket
    for i in range(-450, 451, 50):
        buckets[i] = 0
    buckets[451] = 0  # Special bucket for 451-500
    
    for delta in deltas:
        if delta > 450:
            # Special case for 451-500
            buckets[451] += 1
        else:
            # Round to nearest 50
            bucket = (delta // 50) * 50
            # Clamp to our range
            bucket = max(-450, min(450, bucket))
            buckets[bucket] += 1
    
    total = sum(buckets.values())
    if total == 0:
        return {}
    
    return {bucket: (count/total)*100 for bucket, count in sorted(buckets.items())}

def plot_distributions(player_id):
    player = get_player_by_id(player_id)
    if not player:
        return None
    
    # Debug prints
    print(f"\nPlotting distributions for {player.playerName}")
    
    # Get distributions
    dist = get_swing_distribution(player_id)
    delta_dist = get_delta_distribution(player_id)
    print(f"Swing distribution: {dist}")
    print(f"Delta distribution: {delta_dist}")
    
    # Create figure
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(15, 12))
    fig.suptitle(f'Distributions for {player.playerName}')
    
    # Plot swing distribution
    buckets = list(dist.keys())
    percentages = list(dist.values())
    ax1.bar(buckets, percentages, width=80)
    ax1.set_title('Swing Distribution')
    ax1.set_xlabel('Swing Range')
    ax1.set_ylabel('Percentage')
    ax1.set_xticks(buckets)
    ax1.set_xticklabels([f'{b+1}-{b+100}' for b in buckets], rotation=45)
    
    # Plot delta distribution
    buckets = list(delta_dist.keys())
    percentages = list(delta_dist.values())
    ax2.bar(buckets, percentages, width=40)  # Reduced width since buckets are smaller
    ax2.set_title('Delta Distribution')
    ax2.set_xlabel('Delta Range')
    ax2.set_ylabel('Percentage')
    ax2.set_xticks(buckets)
    ax2.set_xticklabels([
        f'{b} to {b+49}' if b != 451 else '451 to 500'
        for b in buckets
    ], rotation=45)
    
    # Add gridlines for better readability
    ax2.grid(True, alpha=0.3)
    
    plt.tight_layout()
    return fig  # Return the figure instead of closing it

def print_distributions(player_id):
    player = get_player_by_id(player_id)
    if not player:
        return
        
    print(f"\nDistributions for {player.playerName}")
    
    # Swing distribution
    print("\nSwing Distribution (percentage per 100):")
    dist = get_swing_distribution(player_id)
    for bucket, percentage in dist.items():
        print(f"{bucket+1}-{bucket+100}: {percentage:.1f}%")
    
    # Delta distribution
    print("\nDelta Distribution (percentage per 100):")
    dist = get_delta_distribution(player_id)
    for bucket, percentage in dist.items():
        if bucket == 500:
            print(f"{bucket}: {percentage:.1f}%")
        else:
            print(f"{bucket}-{bucket+99}: {percentage:.1f}%")

def plot_histories(player_id):
    player = get_player_by_id(player_id)
    if not player:
        return
        
    pas = get_player_batting_pas_by_id(player_id)
    sorted_pas = sorted(pas, key=lambda x: x.paID)[-25:]  # Last 25 PAs
    
    # Create figure with two subplots
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(15, 12))
    fig.suptitle(f'Recent History for {player.playerName}')
    
    # Swing History
    swings = [pa.swing for pa in sorted_pas if pa.swing is not None]
    indices = range(len(swings))
    
    ax1.plot(indices, swings, 'b-o', linewidth=2)
    ax1.set_title('Swing History')
    ax1.set_ylabel('Swing Number')
    ax1.grid(True, alpha=0.3)
    ax1.set_ylim(0, 1000)
    
    # Add swing numbers above points
    for i, swing in enumerate(swings):
        ax1.annotate(str(swing), (i, swing), textcoords="offset points", 
                    xytext=(0,10), ha='center')
    
    # Delta History
    deltas = []
    for i in range(len(sorted_pas)-1):
        pa1 = sorted_pas[i]
        pa2 = sorted_pas[i+1]
        if pa1.swing is not None and pa2.swing is not None:
            delta = calculate_delta(pa1.swing, pa2.swing)
            deltas.append(delta)
    
    indices = range(len(deltas))
    ax2.plot(indices, deltas, 'r-o', linewidth=2)
    ax2.set_title('Delta History')
    ax2.set_ylabel('Delta')
    ax2.grid(True, alpha=0.3)
    
    # Add delta numbers above points
    for i, delta in enumerate(deltas):
        ax2.annotate(str(delta), (i, delta), textcoords="offset points", 
                    xytext=(0,10), ha='center')
    
    # Remove x-axis labels
    ax1.set_xticks([])
    ax2.set_xticks([])
    
    plt.tight_layout()
    plt.close()

def get_diff_swing_distribution(player_id):
    """Returns distribution of swings following specific diffs (0-500)"""
    pas = get_player_batting_pas_by_id(player_id)
    sorted_pas = sorted(pas, key=lambda x: (x.gameID, x.paID))
    
    # Create a 10x10 matrix for ranges
    matrix = np.zeros((10, 10))
    
    for i in range(len(sorted_pas)-1):
        pa1 = sorted_pas[i]
        pa2 = sorted_pas[i+1]
        
        # Only consider consecutive PAs in same game
        if (pa1.gameID == pa2.gameID and 
            pa1.diff is not None and pa2.swing is not None):
            
            # Get diff bucket (previous diff, 0-500 in steps of 50)
            diff_bucket = (pa1.diff // 50)
            diff_bucket = max(0, min(9, diff_bucket))
            
            # Get swing bucket (next swing)
            swing_bucket = ((pa2.swing - 1) // 100)
            swing_bucket = max(0, min(9, swing_bucket))
            
            matrix[diff_bucket][swing_bucket] += 1
    
    # Convert to percentages by row
    row_sums = matrix.sum(axis=1, keepdims=True)
    row_sums[row_sums == 0] = 1  # Avoid division by zero
    matrix = (matrix / row_sums) * 100
    
    return matrix

def plot_diff_swing_matrix(player_id):
    player = get_player_by_id(player_id)
    if not player:
        return
    
    matrix = get_diff_swing_distribution(player_id)
    
    plt.figure(figsize=(12, 10))
    plt.imshow(matrix, cmap='YlOrRd')
    
    # Add numbers to cells - show 0 for empty cells
    for i in range(10):
        for j in range(10):
            value = matrix[i, j]
            plt.text(j, i, f'{value:.0f}', ha='center', va='center')
    
    # Labels
    plt.title(f'Previous Diff to Next Swing Distribution for {player.playerName}')
    plt.xlabel('Next Swing Range')
    plt.ylabel('Previous Diff Range')
    
    # Tick labels
    diff_ranges = [f'{i*50}-{(i+1)*50-1}' for i in range(10)]  # 0-49, 50-99, etc.
    swing_ranges = [f'{i*100+1}-{(i+1)*100}' for i in range(10)]
    
    plt.xticks(range(10), swing_ranges, rotation=45, ha='right')
    plt.yticks(range(10), diff_ranges)
    
    plt.colorbar(label='Percentage')
    plt.tight_layout()
    plt.close()

def print_histories(player_id):
    player = get_player_by_id(player_id)
    if not player:
        return
        
    pas = get_player_batting_pas_by_id(player_id)
    sorted_pas = sorted(pas, key=lambda x: x.paID)[-10:]  # Last 10 PAs
    
    print(f"\nRecent History for {player.playerName}")
    
    print("\nLast 10 swings:")
    for i, pa in enumerate(sorted_pas, 1):
        if pa.swing is not None:
            print(f"{i}. Swing: {pa.swing}")
    
    print("\nLast 10 deltas:")
    for i in range(len(sorted_pas)-1):
        pa1 = sorted_pas[i]
        pa2 = sorted_pas[i+1]
        if pa1.swing is not None and pa2.swing is not None:
            delta = calculate_delta(pa1.swing, pa2.swing)
            print(f"{i+1}. Delta: {delta} ({pa1.swing} → {pa2.swing})")

def get_swing_swing_distribution(player_id):
    """Returns distribution of swings following specific swings"""
    pas = get_player_batting_pas_by_id(player_id)
    sorted_pas = sorted(pas, key=lambda x: (x.gameID, x.paID))
    
    # Create a 10x10 matrix for ranges
    matrix = np.zeros((10, 10))
    
    for i in range(len(sorted_pas)-1):
        pa1 = sorted_pas[i]
        pa2 = sorted_pas[i+1]
        
        # Only consider consecutive PAs in same game
        if (pa1.gameID == pa2.gameID and 
            pa1.swing is not None and pa2.swing is not None):
            
            # Get swing buckets
            prev_bucket = ((pa1.swing - 1) // 100)
            next_bucket = ((pa2.swing - 1) // 100)
            prev_bucket = max(0, min(9, prev_bucket))
            next_bucket = max(0, min(9, next_bucket))
            
            matrix[prev_bucket][next_bucket] += 1
    
    # Convert to percentages by row
    row_sums = matrix.sum(axis=1, keepdims=True)
    row_sums[row_sums == 0] = 1  # Avoid division by zero
    matrix = (matrix / row_sums) * 100
    
    return matrix

def get_delta_delta_distribution(player_id):
    """Returns distribution of deltas following specific deltas"""
    pas = get_player_batting_pas_by_id(player_id)
    sorted_pas = sorted(pas, key=lambda x: (x.gameID, x.paID))
    
    # Create a 10x10 matrix for ranges
    matrix = np.zeros((10, 10))
    
    for i in range(len(sorted_pas)-2):  # Need 3 PAs to get two consecutive deltas
        pa1 = sorted_pas[i]
        pa2 = sorted_pas[i+1]
        pa3 = sorted_pas[i+2]
        
        # Only consider consecutive PAs in same game
        if (pa1.gameID == pa2.gameID == pa3.gameID and 
            pa1.swing is not None and pa2.swing is not None and pa3.swing is not None):
            
            # Calculate deltas
            delta1 = calculate_delta(pa1.swing, pa2.swing)
            delta2 = calculate_delta(pa2.swing, pa3.swing)
            
            # Get delta buckets
            prev_bucket = ((delta1 + 499) // 100)  # Changed from +500 to +499
            next_bucket = ((delta2 + 499) // 100)  # Changed from +500 to +499
            prev_bucket = max(0, min(9, prev_bucket))
            next_bucket = max(0, min(9, next_bucket))
            
            matrix[prev_bucket][next_bucket] += 1
    
    # Convert to percentages by row
    row_sums = matrix.sum(axis=1, keepdims=True)
    row_sums[row_sums == 0] = 1  # Avoid division by zero
    matrix = (matrix / row_sums) * 100
    
    return matrix

def plot_swing_swing_matrix(player_id):
    player = get_player_by_id(player_id)
    if not player:
        return
    
    matrix = get_swing_swing_distribution(player_id)
    
    plt.figure(figsize=(12, 10))
    plt.imshow(matrix, cmap='YlOrRd')
    
    # Add numbers to cells - show 0 for empty cells
    for i in range(10):
        for j in range(10):
            value = matrix[i, j]
            plt.text(j, i, f'{value:.0f}', ha='center', va='center')
    
    # Labels
    plt.title(f'Swing After Swing Distribution for {player.playerName}')
    plt.xlabel('Next Swing Range')
    plt.ylabel('Previous Swing Range')
    
    # Tick labels
    swing_ranges = [f'{i*100+1}-{(i+1)*100}' for i in range(10)]
    
    plt.xticks(range(10), swing_ranges, rotation=45, ha='right')
    plt.yticks(range(10), swing_ranges)
    
    plt.colorbar(label='Percentage')
    plt.tight_layout()
    plt.close()

def plot_delta_delta_matrix(player_id):
    player = get_player_by_id(player_id)
    if not player:
        return
    
    matrix = get_delta_delta_distribution(player_id)
    
    plt.figure(figsize=(12, 10))
    plt.imshow(matrix, cmap='YlOrRd')
    
    # Add numbers to cells - show 0 for empty cells
    for i in range(10):
        for j in range(10):
            value = matrix[i, j]
            plt.text(j, i, f'{value:.0f}', ha='center', va='center')
    
    # Labels
    plt.title(f'Delta After Delta Distribution for {player.playerName}')
    plt.xlabel('Next Delta Range')
    plt.ylabel('Previous Delta Range')
    
    # Tick labels
    delta_ranges = [f'{-499+i*100}-{-400+i*100}' for i in range(10)]  # Changed ranges
    
    plt.xticks(range(10), delta_ranges, rotation=45, ha='right')
    plt.yticks(range(10), delta_ranges)
    
    plt.colorbar(label='Percentage')
    plt.tight_layout()
    plt.close()

def plot_game_sequences(player_id, num_games=5):
    """Plot swing sequences for the last N games"""
    player = get_player_by_id(player_id)
    if not player:
        return
    
    pas = get_player_batting_pas_by_id(player_id)
    
    # Group PAs by game
    games = defaultdict(list)
    for pa in pas:
        if pa.gameID and pa.swing:
            games[pa.gameID].append(pa)
    
    # Sort games by most recent and take last N
    sorted_games = sorted(games.items(), key=lambda x: max(pa.paID for pa in x[1]), reverse=True)[:num_games]
    
    # Create figure
    fig, axes = plt.subplots(num_games, 1, figsize=(15, 4*num_games))
    fig.suptitle(f'Game Sequences for {player.playerName} (Last {num_games} Games)')
    
    if num_games == 1:
        axes = [axes]
    
    for idx, (game_id, game_pas) in enumerate(sorted_games):
        # Sort PAs within game by paID
        game_pas = sorted(game_pas, key=lambda x: x.paID)
        
        # Get swings and their order numbers
        swings = [pa.swing for pa in game_pas if pa.swing is not None]
        swing_numbers = range(1, len(swings) + 1)
        
        # Plot swings
        axes[idx].plot(swing_numbers, swings, 'b-o', linewidth=2)
        axes[idx].set_title(f'Game {game_id}')
        axes[idx].set_ylabel('Swing Number')
        axes[idx].grid(True, alpha=0.3)
        axes[idx].set_ylim(0, 1000)
        
        # Add swing numbers above points
        for i, swing in enumerate(swings):
            axes[idx].annotate(str(swing), (i+1, swing), textcoords="offset points", 
                             xytext=(0,10), ha='center')
        
        # Set x-axis to show swing order
        axes[idx].set_xticks(swing_numbers)
        axes[idx].set_xlabel('Swing Order in Game')
    
    plt.tight_layout()
    plt.close()

def print_game_sequences(player_id, num_games=5):
    """Print swing sequences for the last N games"""
    player = get_player_by_id(player_id)
    if not player:
        return
    
    pas = get_player_batting_pas_by_id(player_id)
    
    # Group PAs by game
    games = defaultdict(list)
    for pa in pas:
        if pa.gameID and pa.swing:
            games[pa.gameID].append(pa)
    
    # Sort games by most recent and take last N
    sorted_games = sorted(games.items(), key=lambda x: max(pa.paID for pa in x[1]), reverse=True)[:num_games]
    
    print(f"\nGame Sequences for {player.playerName} (Last {num_games} Games)")
    
    for game_id, game_pas in sorted_games:
        # Sort PAs within game by paID
        game_pas = sorted(game_pas, key=lambda x: x.paID)
        
        print(f"\nGame {game_id}:")
        for i, pa in enumerate(game_pas, 1):
            result = pa.exactResult or pa.oldResult or "N/A"
            print(f"Swing {i}: {pa.swing} (Result: {result})")

def plot_game_sequences_overlay(player_id, num_games=5):
    """Plot swing sequences for the last N games overlaid on one plot"""
    player = get_player_by_id(player_id)
    if not player:
        return None
    
    pas = get_player_batting_pas_by_id(player_id)
    
    # Group PAs by game
    games = defaultdict(list)
    for pa in pas:
        if pa.gameID and pa.swing:
            games[pa.gameID].append(pa)
    
    # Sort games by most recent and take last N
    sorted_games = sorted(games.items(), key=lambda x: max(pa.paID for pa in x[1]), reverse=True)[:num_games]
    
    if not sorted_games:
        return None
    
    # Create figure
    fig = plt.figure(figsize=(15, 8))
    plt.title(f'Game Sequences Overlay for {player.playerName} (Last {num_games} Games)')
    
    # Different colors for each game
    colors = ['b', 'r', 'g', 'c', 'm', 'y', 'k', 'orange', 'purple', 'brown']
    
    # Track maximum number of swings for x-axis
    max_swings = 0
    
    # Plot each game
    for idx, (game_id, game_pas) in enumerate(sorted_games):
        # Sort PAs within game by paID
        game_pas = sorted(game_pas, key=lambda x: x.paID)
        
        # Get swings and their order numbers
        swings = [pa.swing for pa in game_pas if pa.swing is not None]
        if not swings:  # Skip if no swings
            continue
            
        swing_numbers = range(1, len(swings) + 1)
        max_swings = max(max_swings, len(swings))
        
        # Plot swings with different color for each game
        color = colors[idx % len(colors)]
        plt.plot(swing_numbers, swings, f'{color}-o', linewidth=2, 
                label=f'Game {game_id}', markersize=8)
        
        # Add swing numbers above points
        for i, swing in enumerate(swings):
            plt.annotate(str(swing), (i+1, swing), textcoords="offset points",
                        xytext=(0,10), ha='center', color=color)
    
    plt.xlabel('Swing Order in Game')
    plt.ylabel('Swing Number')
    plt.grid(True, alpha=0.3)
    plt.ylim(0, 1000)
    plt.xlim(0.5, max_swings + 0.5)
    plt.xticks(range(1, max_swings + 1))
    plt.legend()
    
    plt.tight_layout()
    return fig  # Return the figure instead of closing it

def plot_matrices(player_id):
    """Plot all distribution matrices"""
    player = get_player_by_id(player_id)
    if not player:
        return None
        
    # Create figure with 2x2 subplots
    fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(20, 16))
    fig.suptitle(f'Pattern Analysis for {player.playerName}')
    
    # Diff to Next Swing
    matrix = get_diff_swing_distribution(player_id)
    im1 = ax1.imshow(matrix, cmap='YlOrRd')
    ax1.set_title('Previous Diff to Next Swing')
    ax1.set_xlabel('Next Swing Range')
    ax1.set_ylabel('Previous Diff Range')
    
    # Add numbers to cells
    for i in range(10):
        for j in range(10):
            ax1.text(j, i, f'{matrix[i, j]:.0f}', ha='center', va='center')
    
    # Labels
    diff_ranges = [f'{i*50}-{(i+1)*50-1}' for i in range(10)]
    swing_ranges = [f'{i*100+1}-{(i+1)*100}' for i in range(10)]
    ax1.set_xticks(range(10))
    ax1.set_yticks(range(10))
    ax1.set_xticklabels(swing_ranges, rotation=45, ha='right')
    ax1.set_yticklabels(diff_ranges)
    
    # Swing to Next Swing
    matrix = get_swing_swing_distribution(player_id)
    im2 = ax2.imshow(matrix, cmap='YlOrRd')
    ax2.set_title('Previous Swing to Next Swing')
    ax2.set_xlabel('Next Swing Range')
    ax2.set_ylabel('Previous Swing Range')
    
    # Add numbers to cells
    for i in range(10):
        for j in range(10):
            ax2.text(j, i, f'{matrix[i, j]:.0f}', ha='center', va='center')
    
    ax2.set_xticks(range(10))
    ax2.set_yticks(range(10))
    ax2.set_xticklabels(swing_ranges, rotation=45, ha='right')
    ax2.set_yticklabels(swing_ranges)
    
    # Delta to Delta
    matrix = get_delta_delta_distribution(player_id)
    im3 = ax3.imshow(matrix, cmap='YlOrRd')
    ax3.set_title('Previous Delta to Next Delta')
    ax3.set_xlabel('Next Delta Range')
    ax3.set_ylabel('Previous Delta Range')
    
    # Add numbers to cells
    for i in range(10):
        for j in range(10):
            ax3.text(j, i, f'{matrix[i, j]:.0f}', ha='center', va='center')
    
    delta_ranges = [f'{-499+i*100}-{-400+i*100}' for i in range(10)]
    ax3.set_xticks(range(10))
    ax3.set_yticks(range(10))
    ax3.set_xticklabels(delta_ranges, rotation=45, ha='right')
    ax3.set_yticklabels(delta_ranges)
    
    # Add colorbars
    plt.colorbar(im1, ax=ax1, label='Percentage')
    plt.colorbar(im2, ax=ax2, label='Percentage')
    plt.colorbar(im3, ax=ax3, label='Percentage')
    
    # Remove the empty subplot
    ax4.remove()
    
    plt.tight_layout()
    return fig  # Return the figure instead of closing it

def predict_next_swing(player_id, prev_swing=None, prev_diff=None):
    """Predict next swing based on player and team patterns using sliding windows"""
    pas = get_player_batting_pas_by_id(player_id)
    player = get_player_by_id(player_id)
    if not player or not player.Team:
        return None, 0, 0
        
    # Get all team PAs
    conn = sqlite3.connect('baseball.db')
    c = conn.cursor()
    c.execute('''
        SELECT 
            pa.paID, pa.gameID, pa.inning, pa.outs, pa.pitcherID, pa.hitterID,
            pa.pitch, pa.swing, pa.diff, pa.result, pa.exactResult, pa.oldResult,
            pa.pitchType, pa.pitchSpeed, pa.pitchMovement, pa.pitchLocation,
            pa.pitchSpin, pa.pitchAngle, pa.pitchConfidence, pa.batterTiming,
            pa.batterContact, pa.batterPower, pa.batterEye, pa.batterConfidence,
            pa.inningScore, pa.gameScore, pa.leverageIndex, pa.weather,
            pa.stadium, pa.temperature, pa.windSpeed, pa.windDirection,
            pa.humidity, pa.fieldCondition
        FROM plate_appearances pa
        JOIN players p ON pa.hitterID = p.playerID
        WHERE p.Team = ? AND pa.hitterID != ?
        ORDER BY pa.paID
    ''', (player.Team, player_id))
    team_pas = [PlateAppearance(*row) for row in c.fetchall()]
    conn.close()
    
    # Sort PAs chronologically
    sorted_player_pas = sorted(pas, key=lambda x: x.paID)
    sorted_team_pas = sorted(team_pas, key=lambda x: x.paID)
    
    # Get sequences of 3 consecutive swings
    player_sequences = []
    team_sequences = []
    diff_sequences = []
    
    # Get player sequences
    for i in range(len(sorted_player_pas)-2):
        pa1, pa2, pa3 = sorted_player_pas[i:i+3]
        
        if (pa1.gameID == pa2.gameID == pa3.gameID):
            if all(pa.swing is not None for pa in [pa1, pa2, pa3]):
                player_sequences.append((pa1.swing, pa2.swing, pa3.swing))
            if pa1.diff is not None and all(pa.swing is not None for pa in [pa2, pa3]):
                diff_sequences.append((pa1.diff, pa2.swing, pa3.swing))
    
    # Get team sequences (from other players)
    for i in range(len(sorted_team_pas)-2):
        pa1, pa2, pa3 = sorted_team_pas[i:i+3]
        
        if (pa1.gameID == pa2.gameID == pa3.gameID and 
            pa1.hitterID == pa2.hitterID == pa3.hitterID):  # Same player within team
            if all(pa.swing is not None for pa in [pa1, pa2, pa3]):
                team_sequences.append((pa1.swing, pa2.swing, pa3.swing))
    
    if not player_sequences and not team_sequences and not diff_sequences:
        return None, 0, 0
    
    # Calculate weights based on patterns
    weights = defaultdict(float)
    total_weight = 0
    
    if prev_swing is not None:
        # Weight based on player's previous swing patterns
        if player_sequences:
            for idx, (s1, s2, s3) in enumerate(player_sequences):
                # More weight for:
                # 1. Similar previous swings
                # 2. More recent sequences
                # 3. Player's own patterns over team patterns
                recency_weight = 1 + (idx / len(player_sequences))
                similarity = 1 / (abs(s2 - prev_swing) + 1)
                sequence_weight = recency_weight * similarity * 2  # Double weight for player's own patterns
                
                weights[s3] += sequence_weight
                total_weight += sequence_weight
        
        # Weight based on team's patterns
        if team_sequences:
            for idx, (s1, s2, s3) in enumerate(team_sequences):
                recency_weight = 1 + (idx / len(team_sequences))
                similarity = 1 / (abs(s2 - prev_swing) + 1)
                sequence_weight = recency_weight * similarity
                
                weights[s3] += sequence_weight
                total_weight += sequence_weight
    
    if prev_diff is not None and diff_sequences:
        # Weight based on previous diff patterns
        for idx, (d1, s2, s3) in enumerate(diff_sequences):
            recency_weight = 1 + (idx / len(diff_sequences))
            similarity = 1 / (abs(d1 - prev_diff) + 1)
            sequence_weight = recency_weight * similarity * 1.5  # 1.5x weight for diff patterns
            
            weights[s3] += sequence_weight
            total_weight += sequence_weight
    
    if total_weight == 0:
        # Use overall distribution with recency weighting
        all_sequences = (
            [(pa1.swing, pa2.swing, pa3.swing) 
             for pa1, pa2, pa3 in zip(sorted_player_pas[:-2], sorted_player_pas[1:-1], sorted_player_pas[2:])
             if pa1.gameID == pa2.gameID == pa3.gameID 
             and all(pa.swing is not None for pa in [pa1, pa2, pa3])] +
            [(pa1.swing, pa2.swing, pa3.swing)
             for pa1, pa2, pa3 in zip(sorted_team_pas[:-2], sorted_team_pas[1:-1], sorted_team_pas[2:])
             if pa1.gameID == pa2.gameID == pa3.gameID
             and all(pa.swing is not None for pa in [pa1, pa2, pa3])]
        )
        
        if not all_sequences:
            return None, 0, 0
            
        # Weight by recency and player vs team
        weighted_sum = 0
        total_weight = 0
        for idx, (_, _, swing) in enumerate(all_sequences):
            weight = 1 + (idx / len(all_sequences))
            weighted_sum += swing * weight
            total_weight += weight
            
        prediction = weighted_sum / total_weight
        confidence = 0.1
        sample_size = len(all_sequences)
    else:
        # Calculate weighted average
        prediction = sum(swing * (weight/total_weight) 
                       for swing, weight in weights.items())
        
        # Calculate confidence based on:
        # 1. Sample size (both player and team)
        # 2. Pattern strength
        # 3. Consistency of predictions
        # 4. Ratio of player to team data
        sample_size = len(player_sequences) + len(team_sequences) + len(diff_sequences)
        pattern_strength = max(weights.values()) / total_weight
        
        # Calculate variance of top predictions
        top_predictions = sorted(weights.items(), key=lambda x: x[1], reverse=True)[:3]
        if len(top_predictions) >= 2:
            variance = statistics.variance(p[0] for p in top_predictions)
            consistency = 1 / (1 + (variance / 1000))
        else:
            consistency = 0.5
            
        # Calculate player data ratio
        player_data_ratio = len(player_sequences) / (len(player_sequences) + len(team_sequences) + 0.1)
        
        confidence = min(0.95,
                       (sample_size/100) *    # More samples = higher confidence
                       pattern_strength *      # Stronger pattern = higher confidence
                       consistency *          # More consistent predictions = higher confidence
                       (0.5 + 0.5 * player_data_ratio))  # More player data = higher confidence
    
    # Round prediction to nearest 10
    prediction = round(prediction / 10) * 10
    
    return prediction, confidence, sample_size

if __name__ == '__main__':
    from search_player import search_player
    player_id = search_player()
    if player_id:
        print_distributions(player_id)
        plot_distributions(player_id)
        plot_histories(player_id)
        plot_diff_swing_matrix(player_id)
        print_histories(player_id)
        plot_swing_swing_matrix(player_id)
        plot_delta_delta_matrix(player_id)
        plot_game_sequences(player_id)
        print_game_sequences(player_id)
        plot_game_sequences_overlay(player_id)
        plot_matrices(player_id) 