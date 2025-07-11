"""
Chess.com Game Analysis Tool

This script analyzes the last 50 games from a Chess.com user profile,
focusing on win/loss records, opening moves, ratings, and game accuracy.
"""

import json
from datetime import datetime, timedelta
from chessdotcom import get_player_profile, get_player_games_by_month
from chessdotcom.client import Client
import re

# IMPORTANT: Set a proper User-Agent header (required by Chess.com API)
Client.request_config['headers']['User-Agent'] = 'Chess.com Game Analysis Tool. Contact: your-email@example.com'


def get_last_50_games(username):
    """
    Fetch the last 50 games for a given username by searching recent months.
    
    Args:
        username (str): Chess.com username
        
    Returns:
        list: List of game dictionaries
    """
    games = []
    current_date = datetime.now()
    
    # Search through the last 6 months to get 50 games
    for month_offset in range(6):
        target_date = current_date - timedelta(days=30 * month_offset)
        year = target_date.year
        month = target_date.month
        
        try:
            monthly_games = get_player_games_by_month(username, year, month)
            monthly_data = monthly_games.json.get('games', [])
            games.extend(monthly_data)
            
            print(f"Found {len(monthly_data)} games in {year}-{month:02d}")
            
            # Stop if we have enough games
            if len(games) >= 50:
                break
                
        except Exception as e:
            print(f"Error fetching games for {year}-{month:02d}: {e}")
            continue
    
    # Return the most recent 50 games
    return games[-50:] if len(games) >= 50 else games


def extract_first_three_moves(pgn):
    """
    Extract the first 3 moves from a PGN string.
    
    Args:
        pgn (str): PGN notation of the game
        
    Returns:
        str: First 3 moves in algebraic notation
    """
    if not pgn:
        return "N/A"
    
    try:
        # Find the moves section (after headers)
        moves_section = pgn
        if '[White ' in pgn:
            # Split by newlines and find where moves start
            lines = pgn.split('\n')
            moves_lines = []
            in_moves = False
            for line in lines:
                if line.strip() and not line.startswith('['):
                    in_moves = True
                if in_moves and line.strip():
                    moves_lines.append(line.strip())
            moves_section = ' '.join(moves_lines)
        
        # Extract moves using regex pattern for standard notation
        # Pattern matches: 1. e4 e5 2. Nf3 Nc6 etc.
        move_pattern = r'(\d+)\.\s*([^\s]+)(?:\s+([^\s]+))?'
        moves = re.findall(move_pattern, moves_section)
        
        if moves:
            first_three = []
            for i in range(min(3, len(moves))):
                move_num, white_move, black_move = moves[i]
                if white_move:
                    move_str = f"{move_num}.{white_move}"
                    if black_move and not black_move.startswith('{'):
                        move_str += f" {black_move}"
                    first_three.append(move_str)
            return " ".join(first_three)
        
        # Fallback: try to extract any chess moves
        chess_moves = re.findall(r'\b[NBRQK]?[a-h]?[1-8]?x?[a-h][1-8](?:=[NBRQ])?[+#]?|\bO-O(?:-O)?[+#]?', moves_section)
        if chess_moves:
            return " ".join(chess_moves[:6])  # First 6 half-moves = 3 full moves
        
        return "N/A"
            
    except Exception as e:
        return "N/A"


def analyze_game_result(game, username):
    """
    Determine if the user won, lost, or drew the game.
    
    Args:
        game (dict): Game data from Chess.com API
        username (str): Username to analyze
        
    Returns:
        tuple: (result, user_color, user_rating, opponent_rating, opponent_name)
    """
    white_player = game['white']['username'].lower()
    black_player = game['black']['username'].lower()
    username_lower = username.lower()
    
    if username_lower == white_player:
        user_color = "white"
        user_result = game['white'].get('result', 'unknown')
        user_rating = game['white'].get('rating', 'N/A')
        opponent_rating = game['black'].get('rating', 'N/A')
        opponent_name = game['black']['username']
    elif username_lower == black_player:
        user_color = "black"
        user_result = game['black'].get('result', 'unknown')
        user_rating = game['black'].get('rating', 'N/A')
        opponent_rating = game['white'].get('rating', 'N/A')
        opponent_name = game['white']['username']
    else:
        return "unknown", "unknown", "N/A", "N/A", "N/A"
    
    # Convert result to win/loss/draw
    if user_result == "win":
        result = "Win"
    elif user_result in ["checkmated", "resigned", "timeout", "abandoned"]:
        result = "Loss"
    elif user_result in ["agreed", "repetition", "stalemate", "insufficient"]:
        result = "Draw"
    else:
        result = "Unknown"
    
    return result, user_color, user_rating, opponent_rating, opponent_name


def extract_accuracy(game, username):
    """
    Extract game accuracy if available.
    
    Args:
        game (dict): Game data from Chess.com API
        username (str): Username to analyze
        
    Returns:
        str: Accuracy percentage or "N/A"
    """
    white_player = game['white']['username'].lower()
    username_lower = username.lower()
    
    try:
        if username_lower == white_player:
            accuracy = game['white'].get('accuracy', 'N/A')
        else:
            accuracy = game['black'].get('accuracy', 'N/A')
        
        if accuracy and accuracy != 'N/A':
            return f"{accuracy}%"
        return "N/A"
    except:
        return "N/A"


def analyze_games(username):
    """
    Analyze the last 50 games for a user with detailed statistics.
    
    Args:
        username (str): Chess.com username
    """
    print(f"Analyzing last 50 games for {username}...")
    print("=" * 60)
    
    # Get the games
    games = get_last_50_games(username)
    
    if not games:
        print(f"No games found for {username}")
        return
    
    print(f"\nAnalyzing {len(games)} games...")
    print("-" * 60)
    
    # Initialize counters
    wins = 0
    losses = 0
    draws = 0
    total_accuracy = 0
    accuracy_count = 0
    time_controls = {}
    opening_moves = {}
    
    # Detailed game analysis
    print(f"\n{'Game':<4} {'Result':<6} {'Color':<6} {'User Rating':<12} {'Opp Rating':<11} {'Accuracy':<9} {'Opening':<20} {'Time Control'}")
    print("-" * 100)
    
    for i, game in enumerate(games[-50:], 1):  # Last 50 games
        result, color, user_rating, opp_rating, opponent = analyze_game_result(game, username)
        accuracy = extract_accuracy(game, username)
        first_moves = extract_first_three_moves(game.get('pgn', ''))
        time_control = game.get('time_control', 'N/A')
        
        # Count results
        if result == "Win":
            wins += 1
        elif result == "Loss":
            losses += 1
        elif result == "Draw":
            draws += 1
        
        # Track accuracy
        if accuracy != "N/A":
            try:
                acc_value = float(accuracy.replace('%', ''))
                total_accuracy += acc_value
                accuracy_count += 1
            except:
                pass
        
        # Track time controls
        time_controls[time_control] = time_controls.get(time_control, 0) + 1
        
        # Track opening moves
        if first_moves != "N/A":
            opening_moves[first_moves] = opening_moves.get(first_moves, 0) + 1
        
        # Display game info
        print(f"{i:<4} {result:<6} {color:<6} {user_rating:<12} {opp_rating:<11} {accuracy:<9} {first_moves[:20]:<20} {time_control}")
    
    # Summary statistics
    total_games = wins + losses + draws
    print("\n" + "=" * 60)
    print("SUMMARY STATISTICS")
    print("=" * 60)
    
    if total_games > 0:
        win_rate = (wins / total_games) * 100
        loss_rate = (losses / total_games) * 100
        draw_rate = (draws / total_games) * 100
        
        print(f"Total Games Analyzed: {total_games}")
        print(f"Wins: {wins} ({win_rate:.1f}%)")
        print(f"Losses: {losses} ({loss_rate:.1f}%)")
        print(f"Draws: {draws} ({draw_rate:.1f}%)")
        
        if accuracy_count > 0:
            avg_accuracy = total_accuracy / accuracy_count
            print(f"Average Accuracy: {avg_accuracy:.1f}% (from {accuracy_count} games with accuracy data)")
    
    # Most common time controls
    print(f"\nMost Common Time Controls:")
    sorted_time_controls = sorted(time_controls.items(), key=lambda x: x[1], reverse=True)
    for tc, count in sorted_time_controls[:5]:
        print(f"  {tc}: {count} games")
    
    # Most common openings
    print(f"\nMost Common Opening Sequences:")
    sorted_openings = sorted(opening_moves.items(), key=lambda x: x[1], reverse=True)
    for opening, count in sorted_openings[:5]:
        print(f"  {opening}: {count} times")


def compare_players(usernames):
    """
    Compare multiple players' recent performance.
    
    Args:
        usernames (list): List of Chess.com usernames
    """
    print("PLAYER COMPARISON")
    print("=" * 80)
    
    for username in usernames:
        print(f"\n{username.upper()}:")
        games = get_last_50_games(username)
        
        if not games:
            print(f"  No games found")
            continue
        
        wins = losses = draws = 0
        total_accuracy = accuracy_count = 0
        
        for game in games[-50:]:
            result, _, _, _, _ = analyze_game_result(game, username)
            accuracy = extract_accuracy(game, username)
            
            if result == "Win":
                wins += 1
            elif result == "Loss":
                losses += 1
            elif result == "Draw":
                draws += 1
            
            if accuracy != "N/A":
                try:
                    acc_value = float(accuracy.replace('%', ''))
                    total_accuracy += acc_value
                    accuracy_count += 1
                except:
                    pass
        
        total_games = wins + losses + draws
        if total_games > 0:
            win_rate = (wins / total_games) * 100
            avg_accuracy = total_accuracy / accuracy_count if accuracy_count > 0 else 0
            
            print(f"  Games: {total_games} | Win Rate: {win_rate:.1f}% | Avg Accuracy: {avg_accuracy:.1f}%")
            print(f"  W: {wins} | L: {losses} | D: {draws}")


def debug_pgn_sample(username, num_games=3):
    """
    Debug function to examine PGN format from Chess.com API.
    
    Args:
        username (str): Chess.com username
        num_games (int): Number of games to examine
    """
    print(f"Debugging PGN format for {username}...")
    games = get_last_50_games(username)
    
    for i, game in enumerate(games[-num_games:], 1):
        print(f"\nGame {i} PGN sample:")
        pgn = game.get('pgn', 'No PGN available')
        print(f"First 200 characters: {pgn[:200]}...")
        print(f"Game URL: {game.get('url', 'N/A')}")
        
        # Try to extract moves
        moves = extract_first_three_moves(pgn)
        print(f"Extracted moves: {moves}")


def analyze_games_simplified(username, num_games=50):
    """
    Simplified game analysis focusing on core metrics without problematic PGN parsing.
    
    Args:
        username (str): Chess.com username
        num_games (int): Number of recent games to analyze
    """
    print(f"Analyzing last {num_games} games for {username}...")
    print("=" * 80)
    
    # Get the games
    games = get_last_50_games(username)
    
    if not games:
        print(f"No games found for {username}")
        return
    
    # Limit to requested number of games
    recent_games = games[-num_games:] if len(games) >= num_games else games
    
    print(f"\nAnalyzing {len(recent_games)} games...")
    print("-" * 80)
    
    # Initialize counters
    wins = losses = draws = 0
    total_accuracy = accuracy_count = 0
    time_controls = {}
    rating_history = []
    
    # Detailed game analysis
    print(f"{'#':<3} {'Result':<6} {'Color':<6} {'User Rating':<11} {'Opp Rating':<11} {'Accuracy':<9} {'Time Control':<12} {'Date':<10}")
    print("-" * 90)
    
    for i, game in enumerate(recent_games, 1):
        result, color, user_rating, opp_rating, opponent = analyze_game_result(game, username)
        accuracy = extract_accuracy(game, username)
        time_control = game.get('time_control', 'N/A')
        
        # Extract date from game URL or end_time
        game_date = "N/A"
        if 'end_time' in game:
            try:
                game_date = datetime.fromtimestamp(game['end_time']).strftime('%Y-%m-%d')
            except:
                pass
        
        # Count results
        if result == "Win":
            wins += 1
        elif result == "Loss":
            losses += 1
        elif result == "Draw":
            draws += 1
        
        # Track accuracy
        if accuracy != "N/A":
            try:
                acc_value = float(accuracy.replace('%', ''))
                total_accuracy += acc_value
                accuracy_count += 1
            except:
                pass
        
        # Track time controls
        time_controls[time_control] = time_controls.get(time_control, 0) + 1
        
        # Track rating history
        if user_rating != "N/A":
            try:
                rating_history.append(int(user_rating))
            except:
                pass
        
        # Display game info
        print(f"{i:<3} {result:<6} {color:<6} {user_rating:<11} {opp_rating:<11} {accuracy:<9} {time_control:<12} {game_date:<10}")
    
    # Summary statistics
    total_games = wins + losses + draws
    print("\n" + "=" * 80)
    print("SUMMARY STATISTICS")
    print("=" * 80)
    
    if total_games > 0:
        win_rate = (wins / total_games) * 100
        loss_rate = (losses / total_games) * 100
        draw_rate = (draws / total_games) * 100
        
        print(f"Total Games Analyzed: {total_games}")
        print(f"Wins: {wins} ({win_rate:.1f}%)")
        print(f"Losses: {losses} ({loss_rate:.1f}%)")
        print(f"Draws: {draws} ({draw_rate:.1f}%)")
        
        if accuracy_count > 0:
            avg_accuracy = total_accuracy / accuracy_count
            print(f"Average Accuracy: {avg_accuracy:.1f}% (from {accuracy_count} games with accuracy data)")
        else:
            print("No accuracy data available")
        
        # Rating statistics
        if rating_history:
            current_rating = rating_history[-1] if rating_history else "N/A"
            highest_rating = max(rating_history)
            lowest_rating = min(rating_history)
            avg_rating = sum(rating_history) / len(rating_history)
            
            print(f"Rating Statistics:")
            print(f"  Current: {current_rating}")
            print(f"  Highest: {highest_rating}")
            print(f"  Lowest: {lowest_rating}")
            print(f"  Average: {avg_rating:.0f}")
    
    # Most common time controls
    print(f"\nTime Control Distribution:")
    sorted_time_controls = sorted(time_controls.items(), key=lambda x: x[1], reverse=True)
    for tc, count in sorted_time_controls:
        percentage = (count / total_games) * 100
        print(f"  {tc}: {count} games ({percentage:.1f}%)")


def main():
    """Main function to demonstrate the game analysis functionality."""
    print("Chess.com Game Analysis Tool")
    print("=" * 40)
    
    # Analyze a specific player with simplified analysis
    username = "hikaru"  # Change this to any Chess.com username
    
    # First, let's debug the PGN format
    print("=== PGN Format Debug ===")
    debug_pgn_sample(username, 2)
    
    print("\n\n=== Simplified Game Analysis ===")
    analyze_games_simplified(username, 25)  # Analyze last 25 games
    
    # Compare multiple players
    print("\n\n=== Player Comparison ===")
    players_to_compare = ["hikaru", "fabianocaruana"]
    compare_players(players_to_compare)


if __name__ == "__main__":
    main()
