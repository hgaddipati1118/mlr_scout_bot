import sqlite3

def calculate_delta(first_num, second_num):
    value = second_num - first_num
    if value > 500:
        value = value - 1000
    elif value <= -500:
        value = value + 1000
    return value

def get_result_color(result):
    """Returns color code for different batting results"""
    if not result or result == 'N/A':
        return 'gray'
        
    result = result.lower()
    
    # Home Runs
    if 'hr' in result:
        return 'darkred'
    
    # Triples
    elif '3b' in result or 'triple' in result:
        return 'red'
    
    # Doubles
    elif '2b' in result or 'double' in result:
        return 'orange'
    
    # Singles and Bunts for Hit
    elif '1b' in result or 'single' in result:
        return 'yellow'
    
    # Walks
    elif any(x in result for x in ['bb', 'walk', 'ibb', 'auto bb']):
        return 'lightgreen'
    
    # Strikeouts
    elif any(x in result for x in ['k', 'auto k']):
        return 'blue'
    
    # Ground Outs
    elif 'go' in result or 'groundout' in result:
        return 'lightblue'
    
    # Fly Outs
    elif 'fo' in result or 'flyout' in result or 'sac fly' in result:
        return 'lightgray'
    
    # Pop Outs
    elif 'po' in result or 'popout' in result:
        return 'gray'
    
    # Line Outs
    elif 'lo' in result or 'lineout' in result:
        return 'darkgray'
    
    # Double/Triple Plays
    elif 'dp' in result or 'tp' in result:
        return 'purple'
    
    # Steals/Caught Stealing
    elif any(x in result for x in ['steal', 'sb', 'cs']):
        return 'green'
    
    # Sacrifices
    elif 'sac' in result or 'bunt' in result:
        return 'tan'
    
    # Default for any unhandled cases
    else:
        return 'black'

def get_all_possible_results():
    """Returns a list of all unique results found in the database"""
    conn = sqlite3.connect('baseball.db')
    c = conn.cursor()
    
    # Get all unique results from both exactResult and oldResult columns
    c.execute('''
        SELECT DISTINCT exactResult FROM plate_appearances 
        WHERE exactResult IS NOT NULL
        UNION
        SELECT DISTINCT oldResult FROM plate_appearances 
        WHERE oldResult IS NOT NULL
    ''')
    
    results = sorted([row[0] for row in c.fetchall()])
    conn.close()
    
    return results

def print_all_results():
    """Prints all unique results found in the database"""
    results = get_all_possible_results()
    print("\nAll possible results found in database:")
    for i, result in enumerate(results, 1):
        print(f"{i}. {result}")

# We'll implement get_result_color after we see all possible results
def get_result_color(result):
    """Placeholder until we see all possible results"""
    return 'gray'

