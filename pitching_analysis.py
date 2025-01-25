import sqlite3
from collections import defaultdict
import matplotlib.pyplot as plt
import numpy as np
from search_player import get_player_pitching_pas_by_id, get_player_by_id
from helpers import get_result_color, calculate_delta

def get_pitch_distribution(player_id):
    """Returns distribution of pitches in 100-number buckets"""
    pas = get_player_pitching_pas_by_id(player_id)
    buckets = defaultdict(int)
    
    # Initialize all buckets from 1-1000 in steps of 100
    for i in range(0, 1000, 100):
        buckets[i] = 0
    
    for pa in pas:
        if pa.pitch is not None:
            bucket = ((pa.pitch - 1) // 100) * 100
            bucket = max(0, min(900, bucket))
            buckets[bucket] += 1
    
    total = sum(buckets.values())
    if total == 0:
        return {}
    
    return {bucket: (count/total)*100 for bucket, count in sorted(buckets.items())}

def get_delta_history(player_id):
    """Returns chronological list of deltas between consecutive pitches"""
    pas = get_player_pitching_pas_by_id(player_id)
    sorted_pas = sorted(pas, key=lambda x: x.paID)
    
    deltas = []
    for i in range(len(sorted_pas)-1):
        pa1 = sorted_pas[i]
        pa2 = sorted_pas[i+1]
        if pa1.pitch is not None and pa2.pitch is not None:
            delta = calculate_delta(pa1.pitch, pa2.pitch)
            deltas.append(delta)
    
    return deltas

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
    fig.suptitle(f'Pitching Distributions for {player.playerName}')
    
    # Pitch distribution
    dist = get_pitch_distribution(player_id)
    buckets = list(dist.keys())
    percentages = list(dist.values())
    
    ax1.bar(buckets, percentages, width=80)
    ax1.set_title('Pitch Distribution')
    ax1.set_xlabel('Pitch Range')
    ax1.set_ylabel('Percentage')
    ax1.set_xticks(buckets)
    ax1.set_xticklabels([f'{b+1}-{b+100}' for b in buckets], rotation=45)
    
    # Delta distribution
    dist = get_delta_distribution(player_id)
    buckets = list(dist.keys())
    percentages = list(dist.values())
    
    ax2.bar(buckets, percentages, width=80)
    ax2.set_title('Delta Distribution')
    ax2.set_xlabel('Delta Range')
    ax2.set_ylabel('Percentage')
    ax2.set_xticks(buckets)
    ax2.set_xticklabels([
        f'{b}-{b+99}' if b != 401 else f'{b}-500' 
        for b in buckets
    ], rotation=45)
    
    plt.tight_layout()
    plt.show()

def plot_game_sequences_overlay(player_id, num_games=5):
    """Plot pitch sequences for the last N games overlaid on one plot"""
    player = get_player_by_id(player_id)
    if not player:
        return
    
    pas = get_player_pitching_pas_by_id(player_id)
    
    # Group PAs by game
    games = defaultdict(list)
    for pa in pas:
        if pa.gameID and pa.pitch:
            games[pa.gameID].append(pa)
    
    # Sort games by most recent and take last N
    sorted_games = sorted(games.items(), key=lambda x: max(pa.paID for pa in x[1]), reverse=True)[:num_games]
    
    # Create figure
    plt.figure(figsize=(15, 8))
    plt.title(f'Game Sequences Overlay for {player.playerName} (Last {num_games} Games)')
    
    # Different colors for each game
    colors = ['b', 'r', 'g', 'c', 'm', 'y', 'k', 'orange', 'purple', 'brown']
    
    # Track maximum number of pitches for x-axis
    max_pitches = 0
    
    # Plot each game
    for idx, (game_id, game_pas) in enumerate(sorted_games):
        # Sort PAs within game by paID
        game_pas = sorted(game_pas, key=lambda x: x.paID)
        
        # Get pitches and their order numbers
        pitches = [pa.pitch for pa in game_pas if pa.pitch is not None]
        pitch_numbers = range(1, len(pitches) + 1)
        max_pitches = max(max_pitches, len(pitches))
        
        # Plot pitches with different color for each game
        color = colors[idx % len(colors)]
        plt.plot(pitch_numbers, pitches, f'{color}-o', linewidth=2, 
                label=f'Game {game_id}', markersize=8)
        
        # Add pitch numbers above points
        for i, pitch in enumerate(pitches):
            plt.annotate(str(pitch), (i+1, pitch), textcoords="offset points",
                        xytext=(0,10), ha='center', color=color)
    
    plt.xlabel('Pitch Order in Game')
    plt.ylabel('Pitch Number')
    plt.grid(True, alpha=0.3)
    plt.ylim(0, 1000)
    plt.xlim(0.5, max_pitches + 0.5)
    plt.xticks(range(1, max_pitches + 1))
    plt.legend()
    
    plt.tight_layout()
    plt.show()

def print_game_sequences(player_id, num_games=5):
    """Print pitch sequences for the last N games"""
    player = get_player_by_id(player_id)
    if not player:
        return
    
    pas = get_player_pitching_pas_by_id(player_id)
    
    # Group PAs by game
    games = defaultdict(list)
    for pa in pas:
        if pa.gameID and pa.pitch:
            games[pa.gameID].append(pa)
    
    # Sort games by most recent and take last N
    sorted_games = sorted(games.items(), key=lambda x: max(pa.paID for pa in x[1]), reverse=True)[:num_games]
    
    print(f"\nPitching Sequences for {player.playerName} (Last {num_games} Games)")
    
    for game_id, game_pas in sorted_games:
        # Sort PAs within game by paID
        game_pas = sorted(game_pas, key=lambda x: x.paID)
        
        print(f"\nGame {game_id}:")
        for i, pa in enumerate(game_pas, 1):
            result = pa.exactResult or pa.oldResult or "N/A"
            print(f"Pitch {i}: {pa.pitch} (Result: {result})")

def get_diff_pitch_distribution(player_id):
    """Returns distribution of pitches following specific diffs"""
    pas = get_player_pitching_pas_by_id(player_id)
    sorted_pas = sorted(pas, key=lambda x: (x.gameID, x.paID))
    
    # Create a 10x10 matrix for ranges
    matrix = np.zeros((10, 10))
    
    for i in range(len(sorted_pas)-1):
        pa1 = sorted_pas[i]
        pa2 = sorted_pas[i+1]
        
        # Only consider consecutive PAs in same game
        if (pa1.gameID == pa2.gameID and 
            pa1.diff is not None and pa2.pitch is not None):
            
            # Get diff bucket (previous diff, 0-500 in steps of 50)
            diff_bucket = (pa1.diff // 50)
            diff_bucket = max(0, min(9, diff_bucket))
            
            # Get pitch bucket
            pitch_bucket = ((pa2.pitch - 1) // 100)
            pitch_bucket = max(0, min(9, pitch_bucket))
            
            matrix[diff_bucket][pitch_bucket] += 1
    
    # Convert to percentages by row
    row_sums = matrix.sum(axis=1, keepdims=True)
    row_sums[row_sums == 0] = 1  # Avoid division by zero
    matrix = (matrix / row_sums) * 100
    
    return matrix

def get_pitch_pitch_distribution(player_id):
    """Returns distribution of pitches following specific pitches"""
    pas = get_player_pitching_pas_by_id(player_id)
    sorted_pas = sorted(pas, key=lambda x: (x.gameID, x.paID))
    
    # Create a 10x10 matrix for ranges
    matrix = np.zeros((10, 10))
    
    for i in range(len(sorted_pas)-1):
        pa1 = sorted_pas[i]
        pa2 = sorted_pas[i+1]
        
        # Only consider consecutive PAs in same game
        if (pa1.gameID == pa2.gameID and 
            pa1.pitch is not None and pa2.pitch is not None):
            
            # Get pitch buckets
            prev_bucket = ((pa1.pitch - 1) // 100)
            next_bucket = ((pa2.pitch - 1) // 100)
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
    pas = get_player_pitching_pas_by_id(player_id)
    sorted_pas = sorted(pas, key=lambda x: (x.gameID, x.paID))
    
    # Create a 10x10 matrix for ranges
    matrix = np.zeros((10, 10))
    
    for i in range(len(sorted_pas)-2):  # Need 3 PAs to get two consecutive deltas
        pa1 = sorted_pas[i]
        pa2 = sorted_pas[i+1]
        pa3 = sorted_pas[i+2]
        
        # Only consider consecutive PAs in same game
        if (pa1.gameID == pa2.gameID == pa3.gameID and 
            pa1.pitch is not None and pa2.pitch is not None and pa3.pitch is not None):
            
            # Calculate deltas
            delta1 = calculate_delta(pa1.pitch, pa2.pitch)
            delta2 = calculate_delta(pa2.pitch, pa3.pitch)
            
            # Get delta buckets
            prev_bucket = ((delta1 + 499) // 100)
            next_bucket = ((delta2 + 499) // 100)
            prev_bucket = max(0, min(9, prev_bucket))
            next_bucket = max(0, min(9, next_bucket))
            
            matrix[prev_bucket][next_bucket] += 1
    
    # Convert to percentages by row
    row_sums = matrix.sum(axis=1, keepdims=True)
    row_sums[row_sums == 0] = 1  # Avoid division by zero
    matrix = (matrix / row_sums) * 100
    
    return matrix

def plot_matrices(player_id):
    """Plot all distribution matrices"""
    player = get_player_by_id(player_id)
    if not player:
        return
        
    # Create figure with 2x2 subplots
    fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(20, 16))
    fig.suptitle(f'Pattern Analysis for {player.playerName}')
    
    # Diff to Next Pitch
    matrix = get_diff_pitch_distribution(player_id)
    im1 = ax1.imshow(matrix, cmap='YlOrRd')
    ax1.set_title('Previous Diff to Next Pitch')
    ax1.set_xlabel('Next Pitch Range')
    ax1.set_ylabel('Previous Diff Range')
    
    # Add numbers to cells
    for i in range(10):
        for j in range(10):
            ax1.text(j, i, f'{matrix[i, j]:.0f}', ha='center', va='center')
    
    # Labels
    diff_ranges = [f'{i*50}-{(i+1)*50-1}' for i in range(10)]
    pitch_ranges = [f'{i*100+1}-{(i+1)*100}' for i in range(10)]
    ax1.set_xticks(range(10))
    ax1.set_yticks(range(10))
    ax1.set_xticklabels(pitch_ranges, rotation=45, ha='right')
    ax1.set_yticklabels(diff_ranges)
    
    # Pitch to Next Pitch
    matrix = get_pitch_pitch_distribution(player_id)
    im2 = ax2.imshow(matrix, cmap='YlOrRd')
    ax2.set_title('Previous Pitch to Next Pitch')
    ax2.set_xlabel('Next Pitch Range')
    ax2.set_ylabel('Previous Pitch Range')
    
    # Add numbers to cells
    for i in range(10):
        for j in range(10):
            ax2.text(j, i, f'{matrix[i, j]:.0f}', ha='center', va='center')
    
    ax2.set_xticks(range(10))
    ax2.set_yticks(range(10))
    ax2.set_xticklabels(pitch_ranges, rotation=45, ha='right')
    ax2.set_yticklabels(pitch_ranges)
    
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
    plt.show()

def get_first_pitches(player_id):
    """Returns list of first pitches in each game"""
    pas = get_player_pitching_pas_by_id(player_id)
    games = defaultdict(list)
    
    # Group PAs by game
    for pa in pas:
        if pa.gameID and pa.pitch:
            games[pa.gameID].append(pa)
    
    # Get first PA from each game
    first_pitches = []
    for game_pas in games.values():
        sorted_game_pas = sorted(game_pas, key=lambda x: x.paID)
        if sorted_game_pas:
            first_pitches.append(sorted_game_pas[0].pitch)
    
    return first_pitches

def plot_first_pitch_trends(player_id):
    """Plot first pitch distribution and history"""
    player = get_player_by_id(player_id)
    if not player:
        return
    
    first_pitches = get_first_pitches(player_id)
    if not first_pitches:
        return
    
    # Create figure with two subplots
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(15, 12))
    fig.suptitle(f'First Pitch Analysis for {player.playerName}')
    
    # Distribution plot
    buckets = defaultdict(int)
    for i in range(0, 1000, 100):
        buckets[i] = 0
    
    for pitch in first_pitches:
        bucket = ((pitch - 1) // 100) * 100
        bucket = max(0, min(900, bucket))
        buckets[bucket] += 1
    
    total = sum(buckets.values())
    if total > 0:
        percentages = {b: (c/total)*100 for b, c in buckets.items()}
        
        ax1.bar(list(percentages.keys()), list(percentages.values()), width=80)
        ax1.set_title('First Pitch Distribution')
        ax1.set_xlabel('Pitch Range')
        ax1.set_ylabel('Percentage')
        ax1.set_xticks(list(percentages.keys()))
        ax1.set_xticklabels([f'{b+1}-{b+100}' for b in percentages.keys()], rotation=45)
    
    # History plot
    indices = range(len(first_pitches))
    ax2.plot(indices, first_pitches, 'b-o', linewidth=2)
    ax2.set_title('First Pitch History')
    ax2.set_xlabel('Game Number (Most Recent Last)')
    ax2.set_ylabel('Pitch Number')
    ax2.grid(True, alpha=0.3)
    ax2.set_ylim(0, 1000)
    
    # Add pitch numbers above points
    for i, pitch in enumerate(first_pitches):
        ax2.annotate(str(pitch), (i, pitch), textcoords="offset points",
                    xytext=(0,10), ha='center')
    
    plt.tight_layout()
    plt.show()

def print_first_pitch_stats(player_id):
    """Print statistics about first pitches"""
    player = get_player_by_id(player_id)
    if not player:
        return
    
    first_pitches = get_first_pitches(player_id)
    if not first_pitches:
        return
    
    print(f"\nFirst Pitch Analysis for {player.playerName}")
    print(f"Number of games: {len(first_pitches)}")
    print(f"Average first pitch: {sum(first_pitches)/len(first_pitches):.1f}")
    print(f"Most common range: {((max(set(first_pitches), key=first_pitches.count)-1)//100)*100+1}-{((max(set(first_pitches), key=first_pitches.count)-1)//100)*100+100}")
    
    print("\nLast 5 first pitches:")
    for i, pitch in enumerate(first_pitches[-5:], 1):
        print(f"{i}. {pitch}")

if __name__ == '__main__':
    from search_player import search_player
    player_id = search_player()
    if player_id:
        print_game_sequences(player_id)
        plot_distributions(player_id)
        plot_game_sequences_overlay(player_id)
        plot_matrices(player_id)
        plot_first_pitch_trends(player_id)
        print_first_pitch_stats(player_id) 