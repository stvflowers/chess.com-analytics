# Chess.com Game Analysis Tools - Usage Guide

This repository contains several Python scripts for analyzing Chess.com games and player data using the official Chess.com Public API.

## Files Overview

### 1. `simple_example.py`
**Purpose**: Basic introduction to the Chess.com API
**Features**:
- Get player profile information
- Display basic stats (name, title, rating, followers)
- Simple error handling
- Good starting point for beginners

**Usage**:
```bash
python simple_example.py
```

### 2. `chess_analytics.py`
**Purpose**: Comprehensive Chess.com data analysis
**Features**:
- Detailed player profiles and statistics
- Recent games analysis with performance metrics
- Win/loss/draw analysis
- Chess.com leaderboards access
- Multiple game modes (rapid, blitz, bullet, daily)

**Usage**:
```bash
python chess_analytics.py
```

### 3. `game_analysis.py`
**Purpose**: Advanced game analysis with debugging capabilities
**Features**:
- Last 50 games analysis
- PGN format debugging
- Rating progression tracking
- Time control distribution
- Player comparison functionality
- Simplified and detailed analysis modes

**Usage**:
```bash
python game_analysis.py
```

### 4. `advanced_game_analysis.py` ⭐ **RECOMMENDED**
**Purpose**: Most comprehensive game analysis tool
**Features**:
- ✅ **Win/Loss Analysis**: Detailed breakdown of game results
- ✅ **Rating Tracking**: User and opponent ratings for each game
- ✅ **Opening Classification**: Identifies common chess openings
- ✅ **First 3 Moves**: Extracts and displays opening moves
- ✅ **Game Accuracy**: Shows accuracy percentages when available
- ✅ **Time Control Analysis**: Distribution of different time controls
- ✅ **Performance Statistics**: Win rates, rating changes, trends
- ✅ **Beautiful Output**: Formatted with emojis and clear sections

**Key Metrics Analyzed**:
1. **Win/Loss Records** - Complete breakdown with percentages
2. **Player Ratings** - Current, highest, lowest, average, and change
3. **Opponent Ratings** - Rating of opponents faced
4. **First 3 Moves** - Opening moves in algebraic notation
5. **Game Accuracy** - Accuracy percentages when provided by Chess.com
6. **Opening Classification** - Identifies popular openings like Sicilian, French, etc.
7. **Time Controls** - Distribution of rapid, blitz, bullet games
8. **Game Dates** - Chronological analysis of recent performance

**Usage**:
```bash
python advanced_game_analysis.py
```

**Sample Output**:
```
🔍 Analyzing last 30 games for hikaru
================================================================================
📊 GAME-BY-GAME BREAKDOWN
#   Result Color  Rating  Opp Rating Accuracy  Opening              Date        
1   Win    Black  3309    3008       N/A       Reti Opening         2025-07-11  
2   Win    White  3311    3006       N/A       Nimzo-Larsen Attack  2025-07-11  
...

📈 PERFORMANCE SUMMARY
🎯 Overall Performance:
   Total Games: 30
   Wins: 28 (93.3%)
   Losses: 2 (6.7%)
   Draws: 0 (0.0%)

📊 Rating Analysis:
   Current: 3335
   Change: +26

🎲 Most Played Openings:
   Nimzo-Larsen Attack: 14 games (46.7%)
   Reti Opening: 11 games (36.7%)
```

## Quick Start

1. **Install dependencies**:
```bash
pip install -r requirements.txt
```

2. **Run the advanced analysis** (recommended):
```bash
python advanced_game_analysis.py
```

3. **Customize the username** by editing the script:
```python
username = "your_chess_username_here"  # Change this line
```

## Customization Options

### Change the player to analyze:
```python
username = "gmmagnus"  # Or any Chess.com username
```

### Adjust number of games to analyze:
```python
analyze_user_games(username, 50)  # Analyze last 50 games instead of 30
```

### Focus on specific metrics:
- Edit the `analyze_user_games()` function to add custom analysis
- Modify the `classify_opening()` function to add more opening classifications
- Extend the statistics section to include additional metrics

## API Rate Limits

- Be respectful of Chess.com's API rate limits
- The scripts include proper User-Agent headers as required
- Add delays between requests if analyzing multiple players

## Troubleshooting

1. **No games found**: Some players may have private profiles or no recent games
2. **Missing accuracy data**: Chess.com doesn't provide accuracy for all game types
3. **API errors**: Check your internet connection and try again

## Next Steps

- **Add visualizations**: Use matplotlib or plotly to create charts
- **Database storage**: Store historical data for trend analysis
- **Compare multiple players**: Analyze head-to-head records
- **Opening repertoire analysis**: Deep dive into opening preferences
- **Performance by time control**: Separate analysis for different time formats

The `advanced_game_analysis.py` script provides the most comprehensive analysis and is the best starting point for serious chess data analysis.
