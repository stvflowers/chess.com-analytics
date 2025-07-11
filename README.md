# Chess.com Analytics

A Python project for interacting with the Chess.com Public API to analyze chess data and player statistics.

## Getting Started

### Prerequisites

- Python 3.7+
- pip

### Installation

1. Install the required dependencies:
```bash
pip install -r requirements.txt
```

### Quick Start

The simplest way to get started is with the `simple_example.py` file:

```python
from chessdotcom import get_player_profile, get_player_stats
from chessdotcom.client import Client

# IMPORTANT: Set User-Agent header (required by Chess.com API)
Client.request_config['headers']['User-Agent'] = 'Your App Name. Contact: your-email@example.com'

# Get player information
profile = get_player_profile("hikaru")
player_data = profile.json['player']
print(f"Player: {player_data.get('name')}")
```

## Files Overview

### `requirements.txt`
Contains all necessary Python dependencies:
- `chess.com` - Official Chess.com API client
- `requests` - HTTP library (dependency)
- `python-dateutil` - Date parsing utilities

### `simple_example.py`
A basic example showing how to:
- Get player profiles
- Extract basic player information
- Display rapid chess ratings

### `chess_analytics.py`
A comprehensive script demonstrating:
- Player profiles and statistics
- Recent games analysis
- Game performance metrics
- Chess.com leaderboards
- Win/loss/draw analysis

## Available API Functions

The Chess.com API client provides access to:

- `get_player_profile(username)` - Player profile information
- `get_player_stats(username)` - Player ratings and statistics
- `get_player_games_by_month(username, year, month)` - Games for a specific month
- `get_player_clubs(username)` - Player's clubs
- `get_leaderboards()` - Current leaderboards
- `get_country_details(country_code)` - Country information
- `get_club_details(club_url_id)` - Club information

## Usage Examples

### Basic Player Information
```python
from chessdotcom import get_player_profile
from chessdotcom.client import Client

Client.request_config['headers']['User-Agent'] = 'Your App. Contact: email@example.com'

profile = get_player_profile("hikaru")
print(profile.json['player']['name'])  # "Hikaru Nakamura"
```

### Player Statistics
```python
from chessdotcom import get_player_stats

stats = get_player_stats("hikaru")
rapid_stats = stats.json['chess_rapid']
current_rating = rapid_stats['last']['rating']
print(f"Current rapid rating: {current_rating}")
```

### Recent Games
```python
from chessdotcom import get_player_games_by_month
from datetime import datetime

now = datetime.now()
games = get_player_games_by_month("hikaru", now.year, now.month)
print(f"Games this month: {len(games.json['games'])}")
```

## Important Notes

1. **User-Agent Header**: The Chess.com API requires a proper User-Agent header. Always set it before making requests:
   ```python
   Client.request_config['headers']['User-Agent'] = 'Your App Name. Contact: your-email@example.com'
   ```

2. **Rate Limiting**: Be respectful of the API rate limits. Don't make too many requests in quick succession.

3. **Error Handling**: Always wrap API calls in try-except blocks to handle potential errors gracefully.

## API Documentation

- [Chess.com Public API Documentation](https://www.chess.com/news/view/published-data-api)
- [Python Client on PyPI](https://pypi.org/project/chess.com/)

## Sample Output

When you run `chess_analytics.py`, you'll see output like:

```
=== Player Profile: hikaru ===
Name: Hikaru Nakamura
Title: GM
Followers: 1,298,169
Country: US
Location: Florida
Joined: 2014-01-06

=== Player Stats: hikaru ===
Rapid:
  Current Rating: 3329
  Best Rating: 3336 on 2025-07-09

=== Recent Games: hikaru (2025-07) ===
Total games in 2025-07: 280
Win Rate: 87.5%
```

## Next Steps

1. Modify the `username` variable in the scripts to analyze different players
2. Experiment with different API functions
3. Create your own analysis functions
4. Build visualizations using matplotlib or plotly
5. Store data in a database for historical analysis

## Contributing

Feel free to add new analysis functions, visualizations, or improvements to the existing code!