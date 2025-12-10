"""
Chess.com Analytics - Getting Started with Chess.com Public API

This script demonstrates how to use the Chess.com Public API Python client
to fetch and analyze chess data from Chess.com.

Install dependencies first:
    pip install -r requirements.txt

Chess.com API Documentation: https://www.chess.com/news/view/published-data-api
Python Client: https://pypi.org/project/chess.com/
"""

import json
from datetime import datetime, timedelta
from chessdotcom import get_player_profile, get_player_stats, get_player_games_by_month, get_player_clubs
from chessdotcom import get_leaderboards, get_country_details, get_club_details
from chessdotcom.client import Client

# Configure the client with a proper User-Agent header
Client.request_config['headers']['User-Agent'] = 'Chess.com Analytics Tool. Contact: your-email@example.com'


def display_player_info(username):
    """
    Fetch and display basic player information
    
    Args:
        username (str): Chess.com username
    """
    try:
        print(f"\n=== Player Profile: {username} ===")
        
        # Get player profile
        profile = get_player_profile(username)
        player_data = profile.json['player']
        
        print(f"Name: {player_data.get('name', 'N/A')}")
        print(f"Title: {player_data.get('title', 'None')}")
        print(f"Followers: {player_data.get('followers', 0)}")
        print(f"Country: {player_data.get('country', 'N/A').split('/')[-1] if player_data.get('country') else 'N/A'}")
        print(f"Location: {player_data.get('location', 'N/A')}")
        print(f"Joined: {datetime.fromtimestamp(player_data.get('joined', 0)).strftime('%Y-%m-%d') if player_data.get('joined') else 'N/A'}")
        print(f"Last Online: {datetime.fromtimestamp(player_data.get('last_online', 0)).strftime('%Y-%m-%d %H:%M') if player_data.get('last_online') else 'N/A'}")
        
        return True
        
    except Exception as e:
        print(f"Error fetching player profile: {e}")
        return False


def display_player_stats(username):
    """
    Fetch and display player statistics across different game modes
    
    Args:
        username (str): Chess.com username
    """
    try:
        print(f"\n=== Player Stats: {username} ===")
        
        # Get player stats
        stats = get_player_stats(username)
        stats_data = stats.json
        
        # Display different game mode stats
        game_modes = ['chess_rapid', 'chess_blitz', 'chess_bullet', 'chess_daily']
        
        for mode in game_modes:
            if mode in stats_data:
                mode_data = stats_data[mode]
                last_rating = mode_data.get('last', {})
                best_rating = mode_data.get('best', {})
                
                print(f"\n{mode.replace('chess_', '').title()}:")
                print(f"  Current Rating: {last_rating.get('rating', 'N/A')}")
                print(f"  Games Played: {last_rating.get('rd', 'N/A')}")
                print(f"  Best Rating: {best_rating.get('rating', 'N/A')} on {datetime.fromtimestamp(best_rating.get('date', 0)).strftime('%Y-%m-%d') if best_rating.get('date') else 'N/A'}")
        
        # Display puzzle stats if available
        if 'puzzle_rush' in stats_data:
            puzzle_data = stats_data['puzzle_rush']
            best_puzzle = puzzle_data.get('best', {})
            print(f"\nPuzzle Rush:")
            print(f"  Best Score: {best_puzzle.get('score', 'N/A')}")
            print(f"  Total Attempts: {best_puzzle.get('total_attempts', 'N/A')}")
        
        return True
        
    except Exception as e:
        print(f"Error fetching player stats: {e}")
        return False


def get_recent_games(username, year=None, month=None):
    """
    Fetch recent games for a player
    
    Args:
        username (str): Chess.com username
        year (int): Year (defaults to current year)
        month (int): Month (defaults to current month)
    """
    try:
        if not year:
            year = datetime.now().year
        if not month:
            month = datetime.now().month
            
        print(f"\n=== Recent Games: {username} ({year}-{month:02d}) ===")
        
        # Get games for the specified month
        games = get_player_games_by_month(username, year, month)
        games_data = games.json.get('games', [])
        
        print(f"Total games in {year}-{month:02d}: {len(games_data)}")
        
        if games_data:
            # Show last 5 games
            recent_games = games_data[-5:]
            print("\nLast 5 games:")
            
            for i, game in enumerate(recent_games, 1):
                white_player = game['white']['username']
                black_player = game['black']['username']
                white_rating = game['white'].get('rating', 'N/A')
                black_rating = game['black'].get('rating', 'N/A')
                result = game.get('white', {}).get('result', 'unknown')
                time_control = game.get('time_control', 'N/A')
                
                print(f"  {i}. {white_player} ({white_rating}) vs {black_player} ({black_rating})")
                print(f"     Result: {result}, Time Control: {time_control}")
                print(f"     URL: {game.get('url', 'N/A')}")
        
        return games_data
        
    except Exception as e:
        print(f"Error fetching recent games: {e}")
        return []


def analyze_game_performance(games_data, username):
    """
    Analyze game performance from games data
    
    Args:
        games_data (list): List of games from Chess.com API
        username (str): Username to analyze
    """
    if not games_data:
        print("No games data to analyze")
        return
        
    print(f"\n=== Game Analysis: {username} ===")
    
    wins = 0
    losses = 0
    draws = 0
    
    for game in games_data:
        white_player = game['white']['username'].lower()
        black_player = game['black']['username'].lower()
        
        if username.lower() == white_player:
            result = game['white'].get('result', '')
        elif username.lower() == black_player:
            result = game['black'].get('result', '')
        else:
            continue
            
        if result == 'win':
            wins += 1
        elif result in ['checkmated', 'resigned', 'timeout', 'abandoned']:
            losses += 1
        else:
            draws += 1
    
    total_games = wins + losses + draws
    if total_games > 0:
        win_rate = (wins / total_games) * 100
        print(f"Wins: {wins}")
        print(f"Losses: {losses}")
        print(f"Draws: {draws}")
        print(f"Win Rate: {win_rate:.1f}%")


def explore_leaderboards():
    """
    Explore Chess.com leaderboards
    """
    try:
        print("\n=== Chess.com Leaderboards ===")
        
        leaderboards = get_leaderboards()
        lb_data = leaderboards.json
        
        categories = ['daily', 'rapid', 'blitz', 'bullet']
        
        for category in categories:
            if category in lb_data:
                players = lb_data[category][:5]  # Top 5 players
                print(f"\nTop 5 {category.title()} Players:")
                for i, player in enumerate(players, 1):
                    username = player.get('username', 'N/A')
                    rating = player.get('score', 'N/A')
                    print(f"  {i}. {username}: {rating}")
        
    except Exception as e:
        print(f"Error fetching leaderboards: {e}")


def main():
    """
    Main function demonstrating Chess.com API usage
    """
    print("Chess.com Analytics - API Demo")
    print("=" * 40)
    
    # Example username - replace with any valid Chess.com username
    username = "hikaru"  # You can change this to any Chess.com username
    
    # Demonstrate various API functions
    print("Fetching player information...")
    if display_player_info(username):
        display_player_stats(username)
        games = get_recent_games(username)
        analyze_game_performance(games, username)
    
    # Explore leaderboards
    explore_leaderboards()
    
    print("\n" + "=" * 40)
    print("Demo completed! Try changing the username variable to explore other players.")
    print("You can also call individual functions with different usernames.")


if __name__ == "__main__":
    main()
