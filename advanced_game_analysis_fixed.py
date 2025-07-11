"""
Chess.com Game Analysis - Advanced Version with SQL Database Integration

This script provides detailed analysis of recent Chess.com games including:
- Win/Loss records with detailed breakdown
- Player and opponent ratings during games
- First 3 moves (opening analysis)
- Game accuracy when available
- Time control distribution
- Rating progression
- SQL Database storage for historical analysis
"""

import json
from datetime import datetime, timedelta
from chessdotcom import get_player_profile, get_player_games_by_month
from chessdotcom.client import Client
import re

# Try to import pyodbc, gracefully handle if not available
try:
    import pyodbc
    PYODBC_AVAILABLE = True
except ImportError:
    PYODBC_AVAILABLE = False
    print("⚠️  pyodbc not available. Install with: pip install pyodbc")
    print("   Database features will be disabled.")

# IMPORTANT: Set a proper User-Agent header (required by Chess.com API)
Client.request_config['headers']['User-Agent'] = 'Chess.com Advanced Game Analysis. Contact: your-email@example.com'

# Database configuration
DATABASE_CONFIG = {
    'server': 'your-server.database.windows.net',
    'database': 'your-database',
    'username': 'your-username', 
    'password': 'your-password',
    'driver': '{ODBC Driver 17 for SQL Server}'
}


def configure_database(server=None, database=None, username=None, password=None):
    """
    Configure database connection parameters.
    
    Args:
        server (str): Azure SQL server name (e.g., 'your-server.database.windows.net')
        database (str): Database name
        username (str): Database username
        password (str): Database password
    """
    global DATABASE_CONFIG
    
    if server:
        DATABASE_CONFIG['server'] = server
    if database:
        DATABASE_CONFIG['database'] = database
    if username:
        DATABASE_CONFIG['username'] = username
    if password:
        DATABASE_CONFIG['password'] = password
    
    print("✅ Database configuration updated")
    print(f"   Server: {DATABASE_CONFIG['server']}")
    print(f"   Database: {DATABASE_CONFIG['database']}")
    print(f"   Username: {DATABASE_CONFIG['username']}")


def get_database_connection():
    """
    Create and return a database connection.
    
    Returns:
        pyodbc.Connection: Database connection object or None if failed
    """
    if not PYODBC_AVAILABLE:
        return None
        
    try:
        connection_string = (
            f"DRIVER={DATABASE_CONFIG['driver']};"
            f"SERVER={DATABASE_CONFIG['server']};"
            f"DATABASE={DATABASE_CONFIG['database']};"
            f"UID={DATABASE_CONFIG['username']};"
            f"PWD={DATABASE_CONFIG['password']}"
        )
        connection = pyodbc.connect(connection_string)
        return connection
    except Exception as e:
        print(f"❌ Error connecting to database: {e}")
        return None


def store_game_in_database(connection, username, game_analysis):
    """
    Store game analysis in the database.
    
    Args:
        connection: Database connection
        username (str): Chess.com username
        game_analysis (dict): Analyzed game data
        
    Returns:
        bool: True if successful, False otherwise
    """
    if not connection:
        return False
        
    try:
        cursor = connection.cursor()
        
        # Prepare data for insertion
        game_data = {
            'username': username,
            'game_id': game_analysis.get('game_id'),
            'game_date': game_analysis.get('date'),
            'time_control': game_analysis.get('time_control'),
            'rated': 1 if game_analysis.get('rated', False) else 0,
            'rules': game_analysis.get('rules', 'chess'),
            'result': game_analysis.get('result'),
            'termination': game_analysis.get('termination'),
            'player_color': game_analysis.get('player_color'),
            'player_rating': game_analysis.get('player_rating'),
            'opponent_username': game_analysis.get('opponent_username'),
            'opponent_rating': game_analysis.get('opponent_rating'),
            'opening_moves': game_analysis.get('opening_moves'),
            'opening_name': game_analysis.get('opening_name'),
            'accuracy_white': game_analysis.get('accuracy_white'),
            'accuracy_black': game_analysis.get('accuracy_black'),
            'pgn': game_analysis.get('pgn')
        }
        
        # Use the stored procedure to insert the game
        cursor.execute("""
            EXEC InsertGame 
                @username = ?, @game_id = ?, @game_date = ?, @time_control = ?,
                @rated = ?, @rules = ?, @result = ?, @termination = ?,
                @player_color = ?, @player_rating = ?, @opponent_username = ?,
                @opponent_rating = ?, @opening_moves = ?, @opening_name = ?,
                @accuracy_white = ?, @accuracy_black = ?, @pgn = ?
        """, 
            game_data['username'], game_data['game_id'], game_data['game_date'],
            game_data['time_control'], game_data['rated'], game_data['rules'],
            game_data['result'], game_data['termination'], game_data['player_color'],
            game_data['player_rating'], game_data['opponent_username'],
            game_data['opponent_rating'], game_data['opening_moves'],
            game_data['opening_name'], game_data['accuracy_white'],
            game_data['accuracy_black'], game_data['pgn']
        )
        
        connection.commit()
        return True
        
    except Exception as e:
        print(f"❌ Error storing game in database: {e}")
        connection.rollback()
        return False


def update_user_statistics_in_database(connection, username):
    """
    Update user statistics in the database using stored procedure.
    
    Args:
        connection: Database connection
        username (str): Chess.com username
        
    Returns:
        bool: True if successful, False otherwise
    """
    if not connection:
        return False
        
    try:
        cursor = connection.cursor()
        cursor.execute("EXEC UpdateUserStatistics @username = ?", username)
        connection.commit()
        return True
        
    except Exception as e:
        print(f"❌ Error updating user statistics: {e}")
        connection.rollback()
        return False


def get_user_statistics_from_database(connection, username):
    """
    Retrieve user statistics from the database.
    
    Args:
        connection: Database connection
        username (str): Chess.com username
        
    Returns:
        dict: User statistics or None if failed
    """
    if not connection:
        return None
        
    try:
        cursor = connection.cursor()
        cursor.execute("""
            SELECT total_games, wins, losses, draws, avg_accuracy_white, 
                   avg_accuracy_black, highest_rating, current_rating, last_updated
            FROM user_statistics 
            WHERE username = ?
        """, username)
        
        row = cursor.fetchone()
        if row:
            return {
                'total_games': row[0],
                'wins': row[1],
                'losses': row[2],
                'draws': row[3],
                'avg_accuracy_white': row[4],
                'avg_accuracy_black': row[5],
                'highest_rating': row[6],
                'current_rating': row[7],
                'last_updated': row[8]
            }
        return None
        
    except Exception as e:
        print(f"❌ Error retrieving user statistics: {e}")
        return None


def get_recent_games(username, num_games=50):
    """
    Fetch recent games for a user, searching back through multiple months if needed.
    
    Args:
        username (str): Chess.com username
        num_games (int): Number of recent games to fetch
        
    Returns:
        list: List of game dictionaries
    """
    games = []
    current_date = datetime.now()
    
    # Search through the last 12 months to get enough games
    for month_offset in range(12):
        target_date = current_date - timedelta(days=30 * month_offset)
        year = target_date.year
        month = target_date.month
        
        try:
            monthly_games = get_player_games_by_month(username, year, month)
            monthly_data = monthly_games.json.get('games', [])
            
            if monthly_data:
                games.extend(monthly_data)
                print(f"  Found {len(monthly_data)} games in {year}-{month:02d}")
            
            # Stop if we have enough games
            if len(games) >= num_games:
                break
                
        except Exception as e:
            continue
    
    # Return the most recent games
    return games[-num_games:] if len(games) >= num_games else games


def extract_opening_moves(pgn):
    """
    Extract the first few moves from PGN and identify common openings.
    
    Args:
        pgn (str): PGN notation of the game
        
    Returns:
        tuple: (first_moves_string, opening_name)
    """
    if not pgn:
        return "N/A", "Unknown"
    
    try:
        # Find the moves section
        lines = pgn.split('\n')
        moves_lines = []
        in_moves = False
        
        for line in lines:
            if line.strip() and not line.startswith('['):
                in_moves = True
            if in_moves:
                moves_lines.append(line)
        
        moves_text = ' '.join(moves_lines)
        
        # Clean up the moves - remove annotations, timestamps, etc.
        moves_text = re.sub(r'\{[^}]*\}', '', moves_text)  # Remove comments
        moves_text = re.sub(r'%clk \d+:\d+:\d+', '', moves_text)  # Remove clock times
        moves_text = re.sub(r'\s+', ' ', moves_text)  # Normalize whitespace
        
        # Extract first 6 moves (3 for each side)
        move_pattern = r'(\d+\.)\s*(\S+)\s*(\S+)?'
        matches = re.findall(move_pattern, moves_text)
        
        if not matches:
            return "N/A", "Unknown"
        
        # Format the first 3 moves
        first_moves = []
        for i, (move_num, white_move, black_move) in enumerate(matches[:3]):
            if white_move:
                first_moves.append(f"{move_num} {white_move}")
                if black_move:
                    first_moves.append(black_move)
        
        first_moves_str = ' '.join(first_moves)
        
        # Simple opening classification
        opening_name = classify_opening(first_moves_str)
        
        return first_moves_str, opening_name
        
    except Exception as e:
        return "Error parsing", "Unknown"


def classify_opening(moves_str):
    """
    Classify chess opening based on first moves.
    
    Args:
        moves_str (str): String of first moves
        
    Returns:
        str: Opening name
    """
    moves_lower = moves_str.lower()
    
    # Common opening patterns
    if 'e4 e5' in moves_lower:
        if 'nf3 nc6' in moves_lower:
            return "Italian Game / Spanish Opening"
        elif 'bc4' in moves_lower:
            return "Italian Game"
        elif 'bb5' in moves_lower:
            return "Spanish Opening (Ruy Lopez)"
        else:
            return "King's Pawn Game"
    elif 'e4 c5' in moves_lower:
        return "Sicilian Defense"
    elif 'e4 e6' in moves_lower:
        return "French Defense"
    elif 'e4 c6' in moves_lower:
        return "Caro-Kann Defense"
    elif 'd4 d5' in moves_lower:
        return "Queen's Pawn Game"
    elif 'd4 nf6' in moves_lower:
        if 'c4' in moves_lower:
            return "English Opening / Queen's Indian"
        else:
            return "Indian Defense"
    elif 'nf3' in moves_lower and moves_lower.startswith('1. nf3'):
        return "Reti Opening"
    elif 'c4' in moves_lower and moves_lower.startswith('1. c4'):
        return "English Opening"
    elif 'f4' in moves_lower and moves_lower.startswith('1. f4'):
        return "Bird's Opening"
    else:
        return "Other Opening"


def analyze_game(game, username):
    """
    Analyze a single game and extract relevant information.
    
    Args:
        game (dict): Game data from Chess.com API
        username (str): The username we're analyzing for
        
    Returns:
        dict: Analyzed game data
    """
    # Determine player's color and role
    white_player = game.get('white', {}).get('username', '').lower()
    black_player = game.get('black', {}).get('username', '').lower()
    
    if username.lower() == white_player:
        player_color = 'white'
        player_rating = game.get('white', {}).get('rating')
        opponent_username = black_player
        opponent_rating = game.get('black', {}).get('rating')
    else:
        player_color = 'black'
        player_rating = game.get('black', {}).get('rating')
        opponent_username = white_player
        opponent_rating = game.get('white', {}).get('rating')
    
    # Determine result from player's perspective
    result = game.get('white', {}).get('result', 'unknown')
    if player_color == 'white':
        if result == 'win':
            player_result = 'win'
        elif result in ['checkmated', 'timeout', 'resigned', 'abandoned']:
            player_result = 'loss'
        else:
            player_result = 'draw'
    else:
        if result == 'win':
            player_result = 'loss'
        elif result in ['checkmated', 'timeout', 'resigned', 'abandoned']:
            player_result = 'win'
        else:
            player_result = 'draw'
    
    # Extract PGN and opening moves
    pgn = game.get('pgn', '')
    opening_moves, opening_name = extract_opening_moves(pgn)
    
    # Extract accuracies if available
    accuracy_white = None
    accuracy_black = None
    
    # Look for accuracy in PGN headers
    if pgn:
        white_accuracy_match = re.search(r'\[WhiteAccuracy "([^"]+)"\]', pgn)
        black_accuracy_match = re.search(r'\[BlackAccuracy "([^"]+)"\]', pgn)
        
        if white_accuracy_match:
            try:
                accuracy_white = float(white_accuracy_match.group(1))
            except:
                pass
                
        if black_accuracy_match:
            try:
                accuracy_black = float(black_accuracy_match.group(1))
            except:
                pass
    
    # Format date
    end_time = game.get('end_time')
    if end_time:
        game_date = datetime.fromtimestamp(end_time).strftime('%Y-%m-%d %H:%M:%S')
    else:
        game_date = 'Unknown'
    
    return {
        'game_id': game.get('uuid', 'unknown'),
        'date': game_date,
        'end_time': end_time,
        'player_color': player_color,
        'player_rating': player_rating,
        'opponent_username': opponent_username,
        'opponent_rating': opponent_rating,
        'result': player_result,
        'termination': game.get('white', {}).get('result', 'unknown'),
        'time_control': game.get('time_control', 'unknown'),
        'rated': game.get('rated', False),
        'rules': game.get('rules', 'chess'),
        'opening_moves': opening_moves,
        'opening_name': opening_name,
        'accuracy_white': accuracy_white,
        'accuracy_black': accuracy_black,
        'pgn': pgn,
        'url': game.get('url', '')
    }


def analyze_user_games(username, num_games=50, save_to_database=False):
    """
    Analyze recent games for a user with comprehensive statistics and optional database storage.
    
    Args:
        username (str): Chess.com username
        num_games (int): Number of recent games to analyze
        save_to_database (bool): Whether to save results to database
    """
    print(f"\n📊 Advanced Chess.com Game Analysis for: {username}")
    print(f"🔍 Analyzing last {num_games} games...")
    
    # Database connection
    db_connection = None
    if save_to_database and PYODBC_AVAILABLE:
        db_connection = get_database_connection()
        if db_connection:
            print("✅ Connected to database")
        else:
            print("❌ Database connection failed, proceeding without database")
    
    try:
        # Get player profile
        profile = get_player_profile(username)
        profile_data = profile.json
        
        print(f"👤 Player: {profile_data.get('name', username)}")
        print(f"🏆 Title: {profile_data.get('title', 'No title')}")
        print(f"📅 Joined: {datetime.fromtimestamp(profile_data.get('joined', 0)).strftime('%Y-%m-%d')}")
        
    except Exception as e:
        print(f"⚠️  Could not fetch profile: {e}")
    
    # Fetch recent games
    print(f"\n🔄 Fetching recent games...")
    games = get_recent_games(username, num_games)
    
    if not games:
        print("❌ No games found!")
        return
    
    print(f"✅ Found {len(games)} games")
    
    # Analyze games
    analyzed_games = []
    for game in games:
        analysis = analyze_game(game, username)
        analyzed_games.append(analysis)
        
        # Store in database if enabled
        if db_connection:
            if store_game_in_database(db_connection, username, analysis):
                print(f"  ✅ Stored game {analysis['game_id'][:8]}... in database")
            else:
                print(f"  ❌ Failed to store game {analysis['game_id'][:8]}...")
    
    # Update user statistics in database
    if db_connection:
        if update_user_statistics_in_database(db_connection, username):
            print("✅ Updated user statistics in database")
        else:
            print("❌ Failed to update user statistics")
    
    # Get historical statistics from database
    historical_stats = None
    if db_connection:
        historical_stats = get_user_statistics_from_database(db_connection, username)
    
    # Calculate statistics
    total_games = len(analyzed_games)
    wins = sum(1 for game in analyzed_games if game['result'] == 'win')
    losses = sum(1 for game in analyzed_games if game['result'] == 'loss')
    draws = sum(1 for game in analyzed_games if game['result'] == 'draw')
    
    win_rate = (wins / total_games * 100) if total_games > 0 else 0
    
    # Rating analysis
    ratings = [game['player_rating'] for game in analyzed_games if game['player_rating']]
    if ratings:
        current_rating = ratings[-1]  # Most recent game
        highest_rating = max(ratings)
        lowest_rating = min(ratings)
        avg_rating = sum(ratings) / len(ratings)
    else:
        current_rating = highest_rating = lowest_rating = avg_rating = "N/A"
    
    # Time control analysis
    time_controls = {}
    for game in analyzed_games:
        tc = game['time_control']
        time_controls[tc] = time_controls.get(tc, 0) + 1
    
    # Opening analysis
    openings = {}
    for game in analyzed_games:
        opening = game['opening_name']
        if opening not in openings:
            openings[opening] = {'count': 0, 'wins': 0, 'losses': 0, 'draws': 0}
        openings[opening]['count'] += 1
        openings[opening][game['result'] + 's'] += 1
    
    # Accuracy analysis
    white_accuracies = [game['accuracy_white'] for game in analyzed_games if game['accuracy_white'] is not None]
    black_accuracies = [game['accuracy_black'] for game in analyzed_games if game['accuracy_black'] is not None]
    
    # Print comprehensive analysis
    print(f"\n" + "="*60)
    print(f"📊 COMPREHENSIVE GAME ANALYSIS")
    print(f"="*60)
    
    print(f"\n🎯 OVERALL PERFORMANCE:")
    print(f"   Total Games: {total_games}")
    print(f"   Wins: {wins} ({win_rate:.1f}%)")
    print(f"   Losses: {losses} ({losses/total_games*100:.1f}%)")
    print(f"   Draws: {draws} ({draws/total_games*100:.1f}%)")
    
    if isinstance(current_rating, (int, float)):
        print(f"\n📈 RATING STATISTICS:")
        print(f"   Current Rating: {current_rating}")
        print(f"   Highest Rating: {highest_rating}")
        print(f"   Lowest Rating: {lowest_rating}")
        print(f"   Average Rating: {avg_rating:.1f}")
    
    print(f"\n⏱️  TIME CONTROL DISTRIBUTION:")
    for tc, count in sorted(time_controls.items(), key=lambda x: x[1], reverse=True):
        print(f"   {tc}: {count} games ({count/total_games*100:.1f}%)")
    
    print(f"\n🎪 OPENING ANALYSIS:")
    for opening, stats in sorted(openings.items(), key=lambda x: x[1]['count'], reverse=True)[:10]:
        wr = (stats['wins'] / stats['count'] * 100) if stats['count'] > 0 else 0
        print(f"   {opening}: {stats['count']} games (Win rate: {wr:.1f}%)")
    
    if white_accuracies or black_accuracies:
        print(f"\n🎯 ACCURACY STATISTICS:")
        if white_accuracies:
            print(f"   Average as White: {sum(white_accuracies)/len(white_accuracies):.1f}%")
        if black_accuracies:
            print(f"   Average as Black: {sum(black_accuracies)/len(black_accuracies):.1f}%")
    
    # Show historical comparison if available
    if historical_stats:
        print(f"\n📚 HISTORICAL DATABASE STATISTICS:")
        print(f"   Total Games in DB: {historical_stats['total_games']}")
        print(f"   All-time Wins: {historical_stats['wins']}")
        print(f"   All-time Losses: {historical_stats['losses']}")
        print(f"   All-time Draws: {historical_stats['draws']}")
        if historical_stats['avg_accuracy_white']:
            print(f"   Historical Avg Accuracy (White): {historical_stats['avg_accuracy_white']:.1f}%")
        if historical_stats['avg_accuracy_black']:
            print(f"   Historical Avg Accuracy (Black): {historical_stats['avg_accuracy_black']:.1f}%")
        print(f"   Highest Rating Ever: {historical_stats['highest_rating']}")
    
    # Recent games details
    print(f"\n📋 RECENT GAMES DETAILS:")
    print(f"{'Date':<12} {'Opponent':<15} {'Color':<6} {'Result':<6} {'Rating':<6} {'Opening':<20}")
    print("-" * 80)
    
    for game in analyzed_games[-10:]:  # Show last 10 games
        date_str = game['date'][:10] if len(game['date']) >= 10 else game['date']
        opponent = game['opponent_username'][:14] if game['opponent_username'] else 'Unknown'
        color = game['player_color'][:5]
        result = game['result']
        rating = str(game['player_rating']) if game['player_rating'] else 'N/A'
        opening = game['opening_name'][:19] if game['opening_name'] else 'Unknown'
        
        print(f"{date_str:<12} {opponent:<15} {color:<6} {result:<6} {rating:<6} {opening:<20}")
    
    # Close database connection
    if db_connection:
        db_connection.close()
        print(f"\n✅ Database connection closed")
    
    print(f"\n✅ Analysis complete!")


def main():
    """Main function to run the advanced analysis."""
    print("🔥 Chess.com Advanced Game Analysis with Database Integration")
    print("="*60)
    
    # Database configuration
    save_to_db = False
    if PYODBC_AVAILABLE:
        use_db = input("\nDo you want to use database storage? (y/n): ").strip().lower()
        if use_db == 'y':
            print("\n📊 Database Configuration:")
            server = input("Azure SQL Server (e.g., your-server.database.windows.net): ").strip()
            database = input("Database name: ").strip()
            db_username = input("Username: ").strip()
            password = input("Password: ").strip()
            
            if all([server, database, db_username, password]):
                configure_database(server, database, db_username, password)
                save_to_db = True
            else:
                print("⚠️  Incomplete database configuration, proceeding without database")
                save_to_db = False
    else:
        save_to_db = False
    
    # Get username to analyze
    chess_username = input("\nChess.com username to analyze: ").strip() or "hikaru"
    num_games = input("Number of games to analyze (default 30): ").strip()
    
    try:
        num_games = int(num_games) if num_games else 30
    except:
        num_games = 30
    
    print(f"\n🚀 Starting analysis...")
    analyze_user_games(chess_username, num_games=num_games, save_to_database=save_to_db)


if __name__ == "__main__":
    main()
