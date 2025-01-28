from models import Player, PlateAppearance
import requests
import sqlite3
import os

def init_db():
    # Create database if it doesn't exist
    conn = sqlite3.connect('baseball.db')
    c = conn.cursor()
    
    # Create tables
    c.execute('''
        CREATE TABLE IF NOT EXISTS players (
            playerID INTEGER PRIMARY KEY,
            playerName TEXT,
            team TEXT,
            batType TEXT,
            pitchType TEXT,
            pitchBonus INTEGER,
            hand TEXT,
            priPos TEXT,
            secPos TEXT,
            tertPos TEXT,
            redditName TEXT,
            discordName TEXT,
            discordID TEXT,
            status TEXT,
            posValue INTEGER
        )
    ''')
    
    c.execute('''
        CREATE TABLE IF NOT EXISTS plate_appearances (
            paID INTEGER PRIMARY KEY,
            league TEXT,
            season INTEGER,
            session INTEGER,
            gameID TEXT,
            inning INTEGER,
            inningID TEXT,
            playNumber INTEGER,
            outs INTEGER,
            obc TEXT,
            awayScore INTEGER,
            homeScore INTEGER,
            pitcherTeam TEXT,
            pitcherName TEXT,
            pitcherID INTEGER,
            hitterTeam TEXT,
            hitterName TEXT,
            hitterID INTEGER,
            pitch INTEGER,
            swing INTEGER,
            diff INTEGER,
            exactResult TEXT,
            oldResult TEXT,
            resultAtNeutral TEXT,
            resultAllNeutral TEXT,
            rbi INTEGER,
            run INTEGER,
            batterWPA REAL,
            pitcherWPA REAL,
            pr3B TEXT,
            pr2B TEXT,
            pr1B TEXT,
            prAB TEXT,
            pa_type TEXT
        )
    ''')
    
    conn.commit()
    conn.close()

def check_player_exists(player_id, conn):
    """Check if player's data already exists in database"""
    c = conn.cursor()
    c.execute('SELECT 1 FROM plate_appearances WHERE (hitterID = ? OR pitcherID = ?) LIMIT 1', 
              (player_id, player_id))
    return c.fetchone() is not None

def refresh_player_data(player_id, conn):
    """Remove existing data for player before fetching new data"""
    c = conn.cursor()
    # Instead of deleting, let's just count the records
    c.execute('SELECT COUNT(*) FROM plate_appearances WHERE (hitterID = ? OR pitcherID = ?)', 
              (player_id, player_id))
    count = c.fetchone()[0]
    return count > 0

def getPlayerBattingPlateAppearances(playerID, conn):
    """Returns batting plate appearances, refreshing existing data"""
    plateAppearances = []
    response = requests.get(f'https://www.rslashfakebaseball.com/api/plateappearances/batting/mlr/{playerID}')
    if response.status_code == 200:
        pa_data = response.json()
        for pa in pa_data:
            try:
                pa_obj = PlateAppearance(    
                    pa['paID'], pa['league'], pa['season'], pa['session'],
                    pa['gameID'], pa['inning'], pa['inningID'], pa['playNumber'],
                    pa['outs'], pa['obc'], pa['awayScore'], pa['homeScore'],
                    pa['pitcherTeam'], pa['pitcherName'], pa['pitcherID'],
                    pa['hitterTeam'], pa['hitterName'], pa['hitterID'],
                    pa['pitch'], pa['swing'], pa['diff'], pa['exactResult'],
                    pa['oldResult'], pa['resultAtNeutral'], pa['resultAllNeutral'],
                    pa['rbi'], pa['run'], pa['batterWPA'], pa['pitcherWPA'],
                    pa['pr3B'], pa['pr2B'], pa['pr1B'], pa['prAB']
                )
                plateAppearances.append(pa_obj)
                save_plate_appearance(pa_obj, 'batting', conn)
            except Exception as e:
                print(f"Error processing PA: {pa}")
                print(f"Error: {str(e)}")
    return plateAppearances

def getPlayerPitchingPlateAppearances(playerID, conn):
    """Returns pitching plate appearances, refreshing existing data"""
    plateAppearances = []
    response = requests.get(f'https://www.rslashfakebaseball.com/api/plateappearances/pitching/mlr/{playerID}')
    if response.status_code == 200:
        pa_data = response.json()
        for pa in pa_data:
            try:
                pa_obj = PlateAppearance(    
                    pa['paID'], pa['league'], pa['season'], pa['session'],
                    pa['gameID'], pa['inning'], pa['inningID'], pa['playNumber'],
                    pa['outs'], pa['obc'], pa['awayScore'], pa['homeScore'],
                    pa['pitcherTeam'], pa['pitcherName'], pa['pitcherID'],
                    pa['hitterTeam'], pa['hitterName'], pa['hitterID'],
                    pa['pitch'], pa['swing'], pa['diff'], pa['exactResult'],
                    pa['oldResult'], pa['resultAtNeutral'], pa['resultAllNeutral'],
                    pa['rbi'], pa['run'], pa['batterWPA'], pa['pitcherWPA'],
                    pa['pr3B'], pa['pr2B'], pa['pr1B'], pa['prAB']
                )
                plateAppearances.append(pa_obj)
                save_plate_appearance(pa_obj, 'pitching', conn)
            except Exception as e:
                print(f"Error processing PA: {pa}")
                print(f"Error: {str(e)}")
    return plateAppearances

def save_plate_appearance(pa_obj, pa_type, conn):
    """Save plate appearance to database using provided connection"""
    c = conn.cursor()
    
    try:
        c.execute('''
            INSERT OR REPLACE INTO plate_appearances VALUES 
            (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            pa_obj.paID, pa_obj.league, pa_obj.season, pa_obj.session, pa_obj.gameID,
            pa_obj.inning, pa_obj.inningID, pa_obj.playNumber, pa_obj.outs, pa_obj.obc,
            pa_obj.awayScore, pa_obj.homeScore, pa_obj.pitcherTeam, pa_obj.pitcherName,
            pa_obj.pitcherID, pa_obj.hitterTeam, pa_obj.hitterName, pa_obj.hitterID,
            pa_obj.pitch, pa_obj.swing, pa_obj.diff, pa_obj.exactResult, pa_obj.oldResult,
            pa_obj.resultAtNeutral, pa_obj.resultAllNeutral, pa_obj.rbi, pa_obj.run,
            pa_obj.batterWPA, pa_obj.pitcherWPA, pa_obj.pr3B, pa_obj.pr2B, pa_obj.pr1B,
            pa_obj.prAB, pa_type
        ))
        conn.commit()  # Commit after each insert
    except Exception as e:
        print(f"Error saving PA: {str(e)}")
        print(f"PA data: {pa_obj.__dict__}")
        conn.rollback()

def getPlayers():
    """Get all players, updating database with any new ones"""
    init_db()
    players = []
    
    # Get existing players from database
    conn = sqlite3.connect('baseball.db')
    c = conn.cursor()
    c.execute('SELECT playerID FROM players')
    existing_ids = {row[0] for row in c.fetchall()}
    
    response = requests.get('https://www.rslashfakebaseball.com/api/players')
    if response.status_code == 200:
        player_data = response.json()
        
        for player in player_data:
            player_obj = Player(
                player['playerID'],
                player['playerName'], 
                player['Team'],
                player['batType'],
                player['pitchType'],
                player['pitchBonus'],
                player['hand'],
                player['priPos'],
                player['secPos'],
                player['tertPos'],
                player['redditName'],
                player['discordName'], 
                player['discordID'],
                player['status'],
                player['posValue']
            )
            players.append(player_obj)
            
            # Only insert if player is new or update if status might have changed
            c.execute('''
                INSERT OR REPLACE INTO players VALUES 
                (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                player['playerID'],
                player['playerName'],
                player['Team'],
                player['batType'],
                player['pitchType'],
                player['pitchBonus'],
                player['hand'],
                player['priPos'],
                player['secPos'],
                player['tertPos'],
                player['redditName'],
                player['discordName'],
                player['discordID'],
                player['status'],
                player['posValue']
            ))
            
            # Only fetch PAs for new players
            if player['playerID'] not in existing_ids:
                print(f"Fetching data for new player: {player['playerName']}")
                getPlayerBattingPlateAppearances(player['playerID'], conn)
                getPlayerPitchingPlateAppearances(player['playerID'], conn)
        
        conn.commit()
    
    conn.close()
    return players

def getTeams():
    teams = set()
    for player in getPlayers():
        teams.add(player.Team)
    return teams

def getPlateAppearances():
    plateAppearances = {}
    for player in getPlayers():
        plateAppearances[player.playerID] = player.playerID
    return plateAppearances

def main():
    init_db()
    print("Updating player database...")
    getPlayers()
    print("Database update complete!")

if __name__ == '__main__':
    main()

