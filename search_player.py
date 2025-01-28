import sqlite3
from tabulate import tabulate
from models import Player, PlateAppearance

def search_player():
    name = input("Enter player name to search: ").strip()
    
    # Connect to database and search for players
    conn = sqlite3.connect('baseball.db')
    c = conn.cursor()
    
    # Search for players with similar names using LIKE
    c.execute('''
        SELECT playerID, playerName, team 
        FROM players 
        WHERE playerName LIKE ? 
        LIMIT 5
    ''', (f'%{name}%',))
    
    players = c.fetchall()
    
    if not players:
        print("No players found with that name.")
        conn.close()
        return None
    
    # Display players with numbers for selection
    print("\nFound these players:")
    for idx, (pid, pname, team) in enumerate(players, 1):
        print(f"{idx}. {pname} ({team})")
    
    # Get user selection
    while True:
        try:
            selection = int(input("\nSelect player number (or 0 to cancel): "))
            if selection == 0:
                conn.close()
                return None
            if 1 <= selection <= len(players):
                break
            print("Invalid selection. Please try again.")
        except ValueError:
            print("Please enter a number.")
    
    selected_player_id = players[selection-1][0]
    conn.close()
    return selected_player_id

def get_player_by_id(player_id):
    conn = sqlite3.connect('baseball.db')
    c = conn.cursor()
    
    c.execute('''
        SELECT playerID, playerName, team, batType, pitchType, pitchBonus, 
               hand, priPos, secPos, tertPos, redditName, discordName, 
               discordID, status, posValue
        FROM players 
        WHERE playerID = ?
    ''', (player_id,))
    
    player_data = c.fetchone()
    conn.close()
    
    if not player_data:
        return None
    
    return Player(
        player_data[0],  # playerID
        player_data[1],  # playerName
        player_data[2],  # team
        player_data[3],  # batType
        player_data[4],  # pitchType
        player_data[5],  # pitchBonus
        player_data[6],  # hand
        player_data[7],  # priPos
        player_data[8],  # secPos
        player_data[9],  # tertPos
        player_data[10], # redditName
        player_data[11], # discordName
        player_data[12], # discordID
        player_data[13], # status
        player_data[14]  # posValue
    )

def get_player_batting_pas_by_id(player_id):
    conn = sqlite3.connect('baseball.db')
    c = conn.cursor()
    
    c.execute('''
        SELECT 
            pa.paID, pa.league, pa.season, pa.session, pa.gameID,
            pa.inning, pa.inningID, pa.playNumber, pa.outs, pa.obc,
            pa.awayScore, pa.homeScore, pa.pitcherTeam, pa.pitcherName,
            pa.pitcherID, pa.hitterTeam, pa.hitterName, pa.hitterID,
            pa.pitch, pa.swing, pa.diff, pa.exactResult, pa.oldResult,
            pa.resultAtNeutral, pa.resultAllNeutral, pa.rbi, pa.run,
            pa.batterWPA, pa.pitcherWPA, pa.pr3B, pa.pr2B, pa.pr1B, pa.prAB
        FROM plate_appearances pa
        WHERE pa.hitterID = ? AND (pa.pa_type = 'pitching' OR pa.pa_type = 'batting')
        ORDER BY pa.season DESC, pa.session DESC
    ''', (player_id,))
    
    pas_data = c.fetchall()
    conn.close()
    
    return [PlateAppearance(
        pa[0], pa[1], pa[2], pa[3], pa[4],    # paID, league, season, session, gameID
        pa[5], pa[6], pa[7], pa[8], pa[9],    # inning, inningID, playNumber, outs, obc
        pa[10], pa[11], pa[12], pa[13], pa[14], # awayScore, homeScore, pitcherTeam, pitcherName, pitcherID
        pa[15], pa[16], pa[17], pa[18], pa[19], # hitterTeam, hitterName, hitterID, pitch, swing
        pa[20], pa[21], pa[22], pa[23], pa[24], # diff, exactResult, oldResult, resultAtNeutral, resultAllNeutral
        pa[25], pa[26], pa[27], pa[28], pa[29], # rbi, run, batterWPA, pitcherWPA, pr3B
        pa[30], pa[31], pa[32]                  # pr2B, pr1B, prAB
    ) for pa in pas_data]

def get_player_pitching_pas_by_id(player_id):
    conn = sqlite3.connect('baseball.db')
    c = conn.cursor()
    
    c.execute('''
        SELECT 
            pa.paID, pa.league, pa.season, pa.session, pa.gameID,
            pa.inning, pa.inningID, pa.playNumber, pa.outs, pa.obc,
            pa.awayScore, pa.homeScore, pa.pitcherTeam, pa.pitcherName,
            pa.pitcherID, pa.hitterTeam, pa.hitterName, pa.hitterID,
            pa.pitch, pa.swing, pa.diff, pa.exactResult, pa.oldResult,
            pa.resultAtNeutral, pa.resultAllNeutral, pa.rbi, pa.run,
            pa.batterWPA, pa.pitcherWPA, pa.pr3B, pa.pr2B, pa.pr1B, pa.prAB
        FROM plate_appearances pa
        WHERE pa.pitcherID = ? AND (pa.pa_type = 'pitching' OR pa.pa_type = 'batting')
        ORDER BY pa.season DESC, pa.session DESC
    ''', (player_id,))
    
    pas_data = c.fetchall()
    conn.close()
    
    return [PlateAppearance(
        pa[0], pa[1], pa[2], pa[3], pa[4],    # paID, league, season, session, gameID
        pa[5], pa[6], pa[7], pa[8], pa[9],    # inning, inningID, playNumber, outs, obc
        pa[10], pa[11], pa[12], pa[13], pa[14], # awayScore, homeScore, pitcherTeam, pitcherName, pitcherID
        pa[15], pa[16], pa[17], pa[18], pa[19], # hitterTeam, hitterName, hitterID, pitch, swing
        pa[20], pa[21], pa[22], pa[23], pa[24], # diff, exactResult, oldResult, resultAtNeutral, resultAllNeutral
        pa[25], pa[26], pa[27], pa[28], pa[29], # rbi, run, batterWPA, pitcherWPA, pr3B
        pa[30], pa[31], pa[32]                  # pr2B, pr1B, prAB
    ) for pa in pas_data]

def get_player_stealing_pas_by_id(player_id):
    conn = sqlite3.connect('baseball.db')
    c = conn.cursor()
    
    c.execute('''
        SELECT 
            pa.paID, pa.league, pa.season, pa.session, pa.gameID,
            pa.inning, pa.inningID, pa.playNumber, pa.outs, pa.obc,
            pa.awayScore, pa.homeScore, pa.pitcherTeam, pa.pitcherName,
            pa.pitcherID, pa.hitterTeam, pa.hitterName, pa.hitterID,
            pa.pitch, pa.swing, pa.diff, pa.exactResult, pa.oldResult,
            pa.resultAtNeutral, pa.resultAllNeutral, pa.rbi, pa.run,
            pa.batterWPA, pa.pitcherWPA, pa.pr3B, pa.pr2B, pa.pr1B, pa.prAB
        FROM plate_appearances pa
        WHERE (
            (pa.pr3B = ? AND pa.resultAtNeutral LIKE '%steal%') OR
            (pa.pr2B = ? AND pa.resultAtNeutral LIKE '%steal%') OR
            (pa.pr1B = ? AND pa.resultAtNeutral LIKE '%steal%')
        )
        ORDER BY pa.season DESC, pa.session DESC
    ''', (player_id, player_id, player_id))
    
    pas_data = c.fetchall()
    conn.close()
    
    return [PlateAppearance(
        pa[0], pa[1], pa[2], pa[3], pa[4],    # paID, league, season, session, gameID
        pa[5], pa[6], pa[7], pa[8], pa[9],    # inning, inningID, playNumber, outs, obc
        pa[10], pa[11], pa[12], pa[13], pa[14], # awayScore, homeScore, pitcherTeam, pitcherName, pitcherID
        pa[15], pa[16], pa[17], pa[18], pa[19], # hitterTeam, hitterName, hitterID, pitch, swing
        pa[20], pa[21], pa[22], pa[23], pa[24], # diff, exactResult, oldResult, resultAtNeutral, resultAllNeutral
        pa[25], pa[26], pa[27], pa[28], pa[29], # rbi, run, batterWPA, pitcherWPA, pr3B
        pa[30], pa[31], pa[32]                  # pr2B, pr1B, prAB
    ) for pa in pas_data]

def search_player_by_name(name):
    """Search for a player by name and return their ID"""
    conn = sqlite3.connect('baseball.db')
    c = conn.cursor()
    
    # Search for players with similar names using LIKE
    c.execute('''
        SELECT playerID, playerName, team 
        FROM players 
        WHERE playerName LIKE ? 
        LIMIT 1
    ''', (f'%{name}%',))
    
    player = c.fetchone()
    conn.close()
    
    if not player:
        return None
    
    return player[0]

if __name__ == '__main__':
    player_id = search_player()
    if player_id:
        print(get_player_by_id(player_id))