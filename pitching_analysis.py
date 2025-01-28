import sqlite3
from collections import defaultdict
import matplotlib.pyplot as plt
import numpy as np
from search_player import get_player_pitching_pas_by_id, get_player_by_id
from helpers import get_result_color, calculate_delta
import statistics

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
    
    # Create figure with two subplots
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(15, 12))
    fig.suptitle(f'Pitching Distributions for {player.playerName}')
    
    # Get distributions
    dist = get_pitch_distribution(player_id)
    delta_dist = get_delta_distribution(player_id)
    
    # Plot pitch distribution
    buckets = list(dist.keys())
    percentages = list(dist.values())
    ax1.bar(buckets, percentages, width=80)
    ax1.set_title('Pitch Distribution')
    ax1.set_xlabel('Pitch Range')
    ax1.set_ylabel('Percentage')
    ax1.set_xticks(buckets)
    ax1.set_xticklabels([f'{b+1}-{b+100}' for b in buckets], rotation=45)
    
    # Plot delta distribution
    buckets = list(delta_dist.keys())
    percentages = list(delta_dist.values())
    ax2.bar(buckets, percentages, width=40)
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
    return fig

def plot_game_sequences_overlay(player_id, num_games=5):
    """Plot pitch sequences for the last N games overlaid on one plot"""
    player = get_player_by_id(player_id)
    if not player:
        return None
    
    pas = get_player_pitching_pas_by_id(player_id)
    
    # Group PAs by game
    games = defaultdict(list)
    for pa in pas:
        if pa.gameID and pa.pitch:
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
    
    # Track maximum number of pitches for x-axis
    max_pitches = 0
    
    # Plot each game
    for idx, (game_id, game_pas) in enumerate(sorted_games):
        # Sort PAs within game by paID
        game_pas = sorted(game_pas, key=lambda x: x.paID)
        
        # Get pitches and their order numbers
        pitches = [pa.pitch for pa in game_pas if pa.pitch is not None]
        if not pitches:  # Skip if no pitches
            continue
            
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
    return fig  # Return figure instead of closing

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

def get_diff_delta_distribution(player_id):
    """Returns distribution of deltas following specific diffs"""
    pas = get_player_pitching_pas_by_id(player_id)
    sorted_pas = sorted(pas, key=lambda x: (x.gameID, x.paID))
    
    # Create a 10x10 matrix for ranges
    matrix = np.zeros((10, 10))
    
    for i in range(len(sorted_pas)-2):  # Need 3 PAs to get delta after diff
        pa1 = sorted_pas[i]
        pa2 = sorted_pas[i+1]
        pa3 = sorted_pas[i+2]
        
        # Only consider consecutive PAs in same game
        if (pa1.gameID == pa2.gameID == pa3.gameID and 
            pa1.diff is not None and pa2.pitch is not None and pa3.pitch is not None):
            
            # Get diff bucket (0-500 in steps of 50)
            diff_bucket = (pa1.diff // 50)
            diff_bucket = max(0, min(9, diff_bucket))
            
            # Calculate and bucket the delta
            delta = calculate_delta(pa2.pitch, pa3.pitch)
            delta_bucket = ((delta + 499) // 100)
            delta_bucket = max(0, min(9, delta_bucket))
            
            matrix[diff_bucket][delta_bucket] += 1
    
    # Convert to percentages by row
    row_sums = matrix.sum(axis=1, keepdims=True)
    row_sums[row_sums == 0] = 1  # Avoid division by zero
    matrix = (matrix / row_sums) * 100
    
    return matrix

def plot_matrices(player_id):
    player = get_player_by_id(player_id)
    if not player:
        return None
        
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
    
    # Diff to Next Delta
    matrix = get_diff_delta_distribution(player_id)
    im4 = ax4.imshow(matrix, cmap='YlOrRd')
    ax4.set_title('Previous Diff to Next Delta')
    ax4.set_xlabel('Next Delta Range')
    ax4.set_ylabel('Previous Diff Range')
    
    # Add numbers to cells
    for i in range(10):
        for j in range(10):
            ax4.text(j, i, f'{matrix[i, j]:.0f}', ha='center', va='center')
    
    ax4.set_xticks(range(10))
    ax4.set_yticks(range(10))
    ax4.set_xticklabels(delta_ranges, rotation=45, ha='right')
    ax4.set_yticklabels(diff_ranges)
    
    # Add colorbars
    plt.colorbar(im1, ax=ax1, label='Percentage')
    plt.colorbar(im2, ax=ax2, label='Percentage')
    plt.colorbar(im3, ax=ax3, label='Percentage')
    plt.colorbar(im4, ax=ax4, label='Percentage')
    
    plt.tight_layout()
    return fig

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
    player = get_player_by_id(player_id)
    if not player:
        return None
    
    first_pitches = get_first_pitches(player_id)
    if not first_pitches:
        return None
    
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
    return fig  # Return figure instead of closing

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

def predict_next_pitch(player_id, prev_pitch=None, prev_diff=None):
    """Predict next pitch based on previous patterns using sliding windows"""
    pas = get_player_pitching_pas_by_id(player_id)
    sorted_pas = sorted(pas, key=lambda x: (x.gameID, x.paID))
    
    # Get sequences of 3 consecutive pitches
    pitch_sequences = []
    diff_sequences = []
    
    for i in range(len(sorted_pas)-2):
        pa1, pa2, pa3 = sorted_pas[i:i+3]
        
        # Only consider consecutive PAs in same game
        if (pa1.gameID == pa2.gameID == pa3.gameID):
            if all(pa.pitch is not None for pa in [pa1, pa2, pa3]):
                pitch_sequences.append((pa1.pitch, pa2.pitch, pa3.pitch))
            if pa1.diff is not None and all(pa.pitch is not None for pa in [pa2, pa3]):
                diff_sequences.append((pa1.diff, pa2.pitch, pa3.pitch))
    
    if not pitch_sequences and not diff_sequences:
        return None, 0, 0  # No data to predict from
    
    # Calculate weights based on patterns
    weights = defaultdict(float)
    total_weight = 0
    
    if prev_pitch is not None and len(pitch_sequences) > 0:
        # Weight based on previous pitch patterns
        for idx, (p1, p2, p3) in enumerate(pitch_sequences):
            # More weight for:
            # 1. Similar previous pitches
            # 2. More recent sequences
            recency_weight = 1 + (idx / len(pitch_sequences))  # Newer sequences get higher weight
            similarity = 1 / (abs(p2 - prev_pitch) + 1)  # How close the previous pitch is
            sequence_weight = recency_weight * similarity
            
            weights[p3] += sequence_weight
            total_weight += sequence_weight
    
    if prev_diff is not None and len(diff_sequences) > 0:
        # Weight based on previous diff patterns
        for idx, (d1, p2, p3) in enumerate(diff_sequences):
            # More weight for:
            # 1. Similar diffs
            # 2. More recent sequences
            recency_weight = 1 + (idx / len(diff_sequences))
            similarity = 1 / (abs(d1 - prev_diff) + 1)
            sequence_weight = recency_weight * similarity
            
            weights[p3] += sequence_weight
            total_weight += sequence_weight
    
    if total_weight == 0:
        # If no weights, use overall distribution with recency weighting
        all_sequences = [(pa1.pitch, pa2.pitch, pa3.pitch) 
                        for pa1, pa2, pa3 in zip(sorted_pas[:-2], sorted_pas[1:-1], sorted_pas[2:])
                        if pa1.gameID == pa2.gameID == pa3.gameID 
                        and all(pa.pitch is not None for pa in [pa1, pa2, pa3])]
        
        if not all_sequences:
            return None, 0, 0
            
        # Weight by recency
        weighted_sum = 0
        total_weight = 0
        for idx, (_, _, pitch) in enumerate(all_sequences):
            weight = 1 + (idx / len(all_sequences))
            weighted_sum += pitch * weight
            total_weight += weight
            
        prediction = weighted_sum / total_weight
        confidence = 0.1  # Low confidence for fallback prediction
        sample_size = len(all_sequences)
    else:
        # Calculate weighted average
        prediction = sum(pitch * (weight/total_weight) 
                       for pitch, weight in weights.items())
        
        # Calculate confidence based on:
        # 1. Sample size
        # 2. Pattern strength (how concentrated the weights are)
        # 3. Consistency of predictions
        sample_size = len(pitch_sequences) + len(diff_sequences)
        pattern_strength = max(weights.values()) / total_weight
        
        # Calculate variance of top predictions
        top_predictions = sorted(weights.items(), key=lambda x: x[1], reverse=True)[:3]
        if len(top_predictions) >= 2:
            variance = statistics.variance(p[0] for p in top_predictions)
            consistency = 1 / (1 + (variance / 1000))  # Normalize variance
        else:
            consistency = 0.5
        
        confidence = min(0.95, 
                       (sample_size/100) *  # More samples = higher confidence
                       pattern_strength *    # Stronger pattern = higher confidence
                       consistency)         # More consistent predictions = higher confidence
    
    # Round prediction to nearest 10 to avoid overly specific predictions
    prediction = round(prediction / 10) * 10
    
    return prediction, confidence, sample_size

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