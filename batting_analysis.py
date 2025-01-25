import sqlite3
from collections import defaultdict
import matplotlib.pyplot as plt
import numpy as np
from search_player import get_player_batting_pas_by_id, get_player_by_id
from helpers import get_result_color, calculate_delta

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
    """Returns distribution of deltas in 100-number buckets from -499 to 500"""
    deltas = get_delta_history(player_id)
    buckets = defaultdict(int)
    
    # Initialize buckets from -499 to 500 in steps of 100
    for i in range(-499, 501, 100):
        buckets[i] = 0
    
    for delta in deltas:
        # Round to nearest 100, but offset by -49 to get -499 start
        bucket = ((delta + 49) // 100) * 100 - 49
        # Clamp to our range
        bucket = max(-499, min(401, bucket))  # 401 is the start of the last bucket (401-500)
        buckets[bucket] += 1
    
    total = sum(buckets.values())
    if total == 0:
        return {}
    
    return {bucket: (count/total)*100 for bucket, count in sorted(buckets.items())}

def plot_distributions(player_id):
    player = get_player_by_id(player_id)
    if not player:
        return
    
    # Create figure with two subplots
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(15, 12))
    fig.suptitle(f'Distributions for {player.playerName}')
    
    # Swing distribution
    dist = get_swing_distribution(player_id)
    buckets = list(dist.keys())
    percentages = list(dist.values())
    
    # Make bars wider by adjusting width parameter
    ax1.bar(buckets, percentages, width=80)  # Wider bars
    ax1.set_title('Swing Distribution')
    ax1.set_xlabel('Swing Range')
    ax1.set_ylabel('Percentage')
    ax1.set_xticks(buckets)
    ax1.set_xticklabels([f'{b+1}-{b+100}' for b in buckets], rotation=45)
    
    # Delta distribution
    dist = get_delta_distribution(player_id)
    buckets = list(dist.keys())
    percentages = list(dist.values())
    
    # Make bars wider by adjusting width parameter
    ax2.bar(buckets, percentages, width=80)  # Wider bars
    ax2.set_title('Delta Distribution')
    ax2.set_xlabel('Delta Range')
    ax2.set_ylabel('Percentage')
    ax2.set_xticks(buckets)
    ax2.set_xticklabels([
        f'{b}-{b+99}' if b != 500 else f'{b}' 
        for b in buckets
    ], rotation=45)
    
    plt.tight_layout()
    plt.show()

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
    plt.show()

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
    plt.show()

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
    plt.show()

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
    plt.show()

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
    plt.show()

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
    plt.figure(figsize=(15, 8))
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
    plt.show()

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