"""
Simple Chess.com API Example

A quick start guide to using the Chess.com Public API with Python.
"""

from chessdotcom import get_player_profile, get_player_stats
from chessdotcom.client import Client

# IMPORTANT: Set a proper User-Agent header (required by Chess.com API)
Client.request_config['headers']['User-Agent'] = 'Chess.com Analytics Tool. Contact: your-email@example.com'


def get_player_info(username):
    """Get basic information about a Chess.com player."""
    try:
        # Get player profile
        profile = get_player_profile(username)
        player_data = profile.json['player']
        
        print(f"Player: {username}")
        print(f"Name: {player_data.get('name', 'N/A')}")
        print(f"Title: {player_data.get('title', 'None')}")
        print(f"Country: {player_data.get('country', 'N/A').split('/')[-1] if player_data.get('country') else 'N/A'}")
        print(f"Followers: {player_data.get('followers', 0)}")
        
        # Get player stats
        stats = get_player_stats(username)
        stats_data = stats.json
        
        # Show rapid chess rating if available
        if 'chess_rapid' in stats_data:
            rapid_rating = stats_data['chess_rapid'].get('last', {}).get('rating', 'N/A')
            print(f"Rapid Rating: {rapid_rating}")
        
        print("-" * 30)
        
    except Exception as e:
        print(f"Error getting info for {username}: {e}")


if __name__ == "__main__":
    # Example usage - try different usernames
    players = ["hikaru", "gmmagnus", "fabianocaruana", "anishgiri", "goose_o7"]
    
    print("Chess.com Player Information\n")
    
    for player in players:
        get_player_info(player)
