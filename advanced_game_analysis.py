"""
Chess.com Game Analysis - Advanced Version

This script provides detailed analysis of recent Chess.com games including:
- Win/Loss records with detailed breakdown
- Player and opponent ratings during games
- First 3 moves (opening analysis)
- Game accuracy when available
- Time control distribution
- Rating progression
"""

import json
from datetime import datetime, timedelta
from chessdotcom import get_player_profile, get_player_games_by_month
from chessdotcom.client import Client
import re

# IMPORTANT: Set a proper User-Agent header (required by Chess.com API)
Client.request_config['headers']['User-Agent'] = 'Chess.com Advanced Game Analysis. Contact: your-email@example.com'


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
            if in_moves and line.strip():
                moves_lines.append(line.strip())
        
        moves_section = ' '.join(moves_lines)
        
        # Extract first 3 moves using regex
        move_pattern = r'(\d+)\.\s*([^\s\{]+)(?:\s+([^\s\{]+))?'
        moves = re.findall(move_pattern, moves_section)
        
        if moves:
            first_moves = []
            move_sequence = []
            
            for i in range(min(3, len(moves))):
                move_num, white_move, black_move = moves[i]
                
                # Clean up moves (remove annotations)
                white_clean = re.sub(r'[+#?!]', '', white_move)
                black_clean = re.sub(r'[+#?!]', '', black_move) if black_move else ""
                
                move_sequence.extend([white_clean, black_clean] if black_clean else [white_clean])
                first_moves.append(f"{move_num}.{white_clean}" + (f" {black_clean}" if black_clean else ""))
            
            first_moves_str = " ".join(first_moves)
            opening_name = classify_opening(move_sequence)
            
            return first_moves_str, opening_name
        
        return "N/A", "Unknown"
            
    except Exception as e:
        return "N/A", "Unknown"


def classify_opening(moves):
    """
    Basic opening classification based on first few moves.
    
    Args:
        moves (list): List of moves in algebraic notation
        
    Returns:
        str: Opening name or category
    """
    if not moves or len(moves) < 2:
        return "Unknown"
    
    first_move = moves[0].lower()
    second_move = moves[1].lower() if len(moves) > 1 else ""
    
    # Basic opening classification
    openings = {
        "e4": {
            "e5": "King's Pawn Game",
            "c5": "Sicilian Defense",
            "e6": "French Defense",
            "c6": "Caro-Kann Defense",
            "d6": "Pirc Defense",
            "g6": "Modern Defense",
            "nc6": "Nimzowitsch Defense"
        },
        "d4": {
            "d5": "Queen's Pawn Game",
            "nf6": "Indian Defense",
            "f5": "Dutch Defense",
            "g6": "King's Indian Defense",
            "e6": "Queen's Pawn Game",
            "c5": "Benoni Defense"
        },
        "nf3": {
            "": "Reti Opening"
        },
        "c4": {
            "": "English Opening"
        },
        "g3": {
            "": "King's Indian Attack"
        },
        "b3": {
            "": "Nimzo-Larsen Attack"
        }
    }
    
    if first_move in openings:
        if second_move in openings[first_move]:
            return openings[first_move][second_move]
        elif "" in openings[first_move]:
            return openings[first_move][""]
        else:
            return f"{first_move.upper()} Opening"
    
    return "Other"


def analyze_game_details(game, username):
    """
    Extract detailed information from a single game.
    
    Args:
        game (dict): Game data from Chess.com API
        username (str): Username to analyze
        
    Returns:
        dict: Detailed game analysis
    """
    white_player = game['white']['username'].lower()
    black_player = game['black']['username'].lower()
    username_lower = username.lower()
    
    # Determine user's color and result
    if username_lower == white_player:
        user_color = "White"
        user_result = game['white'].get('result', 'unknown')
        user_rating = game['white'].get('rating', 'N/A')
        opponent_rating = game['black'].get('rating', 'N/A')
        opponent_name = game['black']['username']
        user_accuracy = game['white'].get('accuracy', None)
    elif username_lower == black_player:
        user_color = "Black"
        user_result = game['black'].get('result', 'unknown')
        user_rating = game['black'].get('rating', 'N/A')
        opponent_rating = game['white'].get('rating', 'N/A')
        opponent_name = game['white']['username']
        user_accuracy = game['black'].get('accuracy', None)
    else:
        return None
    
    # Convert result to standard format
    if user_result == "win":
        result = "Win"
    elif user_result in ["checkmated", "resigned", "timeout", "abandoned"]:
        result = "Loss"
    elif user_result in ["agreed", "repetition", "stalemate", "insufficient"]:
        result = "Draw"
    else:
        result = "Unknown"
    
    # Extract game details
    time_control = game.get('time_control', 'N/A')
    game_url = game.get('url', 'N/A')
    
    # Get game date
    game_date = "N/A"
    if 'end_time' in game:
        try:
            game_date = datetime.fromtimestamp(game['end_time']).strftime('%Y-%m-%d')
        except:
            pass
    
    # Extract opening information
    pgn = game.get('pgn', '')
    first_moves, opening_name = extract_opening_moves(pgn)
    
    return {
        'result': result,
        'color': user_color,
        'user_rating': user_rating,
        'opponent_rating': opponent_rating,
        'opponent_name': opponent_name,
        'accuracy': f"{user_accuracy:.1f}%" if user_accuracy else "N/A",
        'time_control': time_control,
        'date': game_date,
        'first_moves': first_moves,
        'opening': opening_name,
        'url': game_url
    }


def analyze_user_games(username, num_games=50):
    """
    Comprehensive analysis of a user's recent games.
    
    Args:
        username (str): Chess.com username
        num_games (int): Number of recent games to analyze
    """
    print(f"🔍 Analyzing last {num_games} games for {username}")
    print("=" * 80)
    
    # Get recent games
    print("📥 Fetching games...")
    games = get_recent_games(username, num_games)
    
    if not games:
        print(f"❌ No games found for {username}")
        return
    
    print(f"✅ Found {len(games)} games for analysis\n")
    
    # Analyze each game
    game_analyses = []
    for game in games:
        analysis = analyze_game_details(game, username)
        if analysis:
            game_analyses.append(analysis)
    
    if not game_analyses:
        print("❌ No valid games found for analysis")
        return
    
    # Display detailed results
    print("📊 GAME-BY-GAME BREAKDOWN")
    print("-" * 80)
    print(f"{'#':<3} {'Result':<6} {'Color':<6} {'Rating':<7} {'Opp Rating':<10} {'Accuracy':<9} {'Opening':<20} {'Date':<12}")
    print("-" * 80)
    
    for i, analysis in enumerate(game_analyses, 1):
        print(f"{i:<3} {analysis['result']:<6} {analysis['color']:<6} {analysis['user_rating']:<7} "
              f"{analysis['opponent_rating']:<10} {analysis['accuracy']:<9} {analysis['opening'][:20]:<20} {analysis['date']:<12}")
    
    # Calculate statistics
    wins = sum(1 for g in game_analyses if g['result'] == 'Win')
    losses = sum(1 for g in game_analyses if g['result'] == 'Loss')
    draws = sum(1 for g in game_analyses if g['result'] == 'Draw')
    total = len(game_analyses)
    
    # Accuracy statistics
    accuracies = [float(g['accuracy'].replace('%', '')) for g in game_analyses if g['accuracy'] != 'N/A']
    
    # Rating statistics
    ratings = [int(g['user_rating']) for g in game_analyses if g['user_rating'] != 'N/A']
    
    # Opening statistics
    openings = {}
    for analysis in game_analyses:
        opening = analysis['opening']
        openings[opening] = openings.get(opening, 0) + 1
    
    # Time control statistics
    time_controls = {}
    for analysis in game_analyses:
        tc = analysis['time_control']
        time_controls[tc] = time_controls.get(tc, 0) + 1
    
    # Display summary
    print("\n" + "=" * 80)
    print("📈 PERFORMANCE SUMMARY")
    print("=" * 80)
    
    if total > 0:
        win_rate = (wins / total) * 100
        print(f"🎯 Overall Performance:")
        print(f"   Total Games: {total}")
        print(f"   Wins: {wins} ({win_rate:.1f}%)")
        print(f"   Losses: {losses} ({(losses/total)*100:.1f}%)")
        print(f"   Draws: {draws} ({(draws/total)*100:.1f}%)")
        
        if accuracies:
            avg_accuracy = sum(accuracies) / len(accuracies)
            max_accuracy = max(accuracies)
            min_accuracy = min(accuracies)
            print(f"\n🎯 Accuracy Statistics:")
            print(f"   Average: {avg_accuracy:.1f}%")
            print(f"   Best: {max_accuracy:.1f}%")
            print(f"   Worst: {min_accuracy:.1f}%")
            print(f"   Games with accuracy data: {len(accuracies)}/{total}")
        else:
            print(f"\n⚠️  No accuracy data available")
        
        if ratings:
            current_rating = ratings[-1]
            highest_rating = max(ratings)
            lowest_rating = min(ratings)
            avg_rating = sum(ratings) / len(ratings)
            rating_change = ratings[-1] - ratings[0] if len(ratings) > 1 else 0
            
            print(f"\n📊 Rating Analysis:")
            print(f"   Current: {current_rating}")
            print(f"   Highest: {highest_rating}")
            print(f"   Lowest: {lowest_rating}")
            print(f"   Average: {avg_rating:.0f}")
            print(f"   Change: {rating_change:+d}")
        
        # Top openings
        print(f"\n🎲 Most Played Openings:")
        sorted_openings = sorted(openings.items(), key=lambda x: x[1], reverse=True)
        for opening, count in sorted_openings[:5]:
            percentage = (count / total) * 100
            print(f"   {opening}: {count} games ({percentage:.1f}%)")
        
        # Time controls
        print(f"\n⏱️  Time Control Distribution:")
        sorted_tcs = sorted(time_controls.items(), key=lambda x: x[1], reverse=True)
        for tc, count in sorted_tcs:
            percentage = (count / total) * 100
            print(f"   {tc}: {count} games ({percentage:.1f}%)")


def main():
    """Main function demonstrating the advanced game analysis."""
    print("♟️  Chess.com Advanced Game Analysis Tool")
    print("=" * 50)
    
    # Analyze a specific player
    username = "goose_o7"  # Change this to analyze different players
    analyze_user_games(username, 30)  # Analyze last 30 games


if __name__ == "__main__":
    main()
