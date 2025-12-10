# Chess.com Analytics Usage Guide

This workspace contains several Python scripts for analyzing Chess.com game data with optional SQL database integration.

## Files Overview

### 1. `simple_example.py`
Basic Chess.com API demonstration script.

**Features:**
- Fetches player profile information
- Shows player statistics and ratings
- Simple to understand and modify

**Usage:**
```bash
python3 simple_example.py
```

### 2. `chess_analytics.py`
Comprehensive Chess.com analytics tool.

**Features:**
- Player profile analysis
- Recent games overview
- Leaderboard information
- Multiple analysis functions

**Usage:**
```bash
python3 chess_analytics.py
```

### 3. `game_analysis.py`
Focused game analysis tool for recent games.

**Features:**
- Analyzes last 50 games by default
- Win/loss/draw statistics
- Rating progression tracking
- First 3 moves extraction
- Game accuracy when available

**Usage:**
```bash
python3 game_analysis.py
```

### 4. `advanced_game_analysis.py` ⭐ **RECOMMENDED**
Most comprehensive analysis tool with SQL database integration.

**Features:**
- Complete game analysis with database storage
- Advanced opening classification
- Historical statistics tracking
- Accuracy analysis for both colors
- Time control distribution
- Opponent analysis
- Optional Azure SQL Database integration

**Database Integration:**
- Stores game history in SQL database
- Tracks long-term statistics
- Uses stored procedures for data integrity
- Supports Azure SQL Database

**Usage:**
```bash
python3 advanced_game_analysis.py
```

**Interactive prompts:**
1. Choose whether to use database storage
2. If yes, provide database connection details:
   - Azure SQL Server (e.g., your-server.database.windows.net)
   - Database name
   - Username and password
3. Enter Chess.com username to analyze
4. Specify number of games to analyze

### 5. `sql_setup.sql`
Azure SQL Database schema and stored procedures.

**Features:**
- Complete database schema for chess analytics
- Tables: chess_games, user_statistics, opening_statistics
- Stored procedures for data management
- Optimized for Azure SQL Database

**Setup:**
1. Create an Azure SQL Database
2. Run this script to create tables and procedures
3. Use connection details in advanced_game_analysis.py

## Installation & Setup

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

**Required packages:**
- chess.com (Chess.com API client)
- requests (HTTP requests)
- python-dateutil (Date parsing)
- pyodbc (SQL database connectivity - optional)

### 2. Database Setup (Optional)
If you want to use database features:

1. **Create Azure SQL Database:**
   - Sign up for Azure if needed
   - Create a SQL Database instance
   - Note the server name, database name, username, and password

2. **Run Database Setup:**
   ```sql
   -- Run the contents of sql_setup.sql in your Azure SQL Database
   -- This creates tables and stored procedures
   ```

3. **Install pyodbc:**
   ```bash
   pip install pyodbc
   ```

## Usage Examples

### Basic Analysis (No Database)
```bash
python3 advanced_game_analysis.py
# Choose 'n' for database when prompted
# Enter username: hikaru
# Number of games: 50
```

### Full Analysis with Database
```bash
python3 advanced_game_analysis.py
# Choose 'y' for database
# Enter Azure SQL connection details
# Enter username: your-chess-username
# Number of games: 100
```

### API Integration Example
```python
from advanced_game_analysis import analyze_user_games

# Analyze without database
analyze_user_games("hikaru", num_games=30, save_to_database=False)

# Analyze with database (requires configuration)
from advanced_game_analysis import configure_database
configure_database(
    server="your-server.database.windows.net",
    database="chess_analytics",
    username="your-username",
    password="your-password"
)
analyze_user_games("your-username", num_games=50, save_to_database=True)
```

## Output Explanation

### Game Analysis Results

**Overall Performance:**
- Total games analyzed
- Win/loss/draw counts and percentages
- Win rate calculation

**Rating Statistics:**
- Current rating (from most recent game)
- Highest and lowest ratings in sample
- Average rating during analyzed period

**Time Control Distribution:**
- Breakdown of games by time control format
- Percentages for each format

**Opening Analysis:**
- Most frequently played openings
- Win rates for each opening
- Opening classification based on first moves

**Accuracy Statistics:**
- Average accuracy when playing as White
- Average accuracy when playing as Black
- Based on Chess.com's analysis when available

**Recent Games Details:**
- Last 10 games in tabular format
- Date, opponent, color, result, rating, opening

**Database Statistics (if enabled):**
- Historical all-time statistics
- Comparison with current analysis
- Long-term trends and patterns

## Database Schema

### Tables Created:
1. **chess_games** - Individual game records
2. **user_statistics** - Aggregated user statistics  
3. **opening_statistics** - Opening performance data

### Stored Procedures:
1. **InsertGame** - Add new game with validation
2. **UpdateUserStatistics** - Recalculate user stats
3. **GetUserStatistics** - Retrieve user statistics

## Troubleshooting

### Common Issues:

1. **"pyodbc not available"**
   - Install with: `pip install pyodbc`
   - Or run without database features

2. **"Rate limit exceeded"**
   - Chess.com API has rate limits
   - Wait a few minutes and try again
   - Reduce number of games analyzed

3. **"No games found"**
   - Check username spelling
   - User might have very few recent games
   - Try a different username

4. **Database connection errors**
   - Verify Azure SQL connection details
   - Check firewall settings
   - Ensure database exists and is accessible

5. **"Import errors"**
   - Run: `pip install -r requirements.txt`
   - Check Python version (3.6+ recommended)

### Performance Tips:

1. **For large analyses:**
   - Start with smaller game counts (30-50)
   - Use database storage for historical tracking
   - Be patient with API requests

2. **Database usage:**
   - Use database for long-term tracking
   - Run periodic updates to build history
   - Take advantage of stored procedures

## API Guidelines

- Always use appropriate User-Agent headers (automatically set)
- Respect Chess.com's rate limits
- Don't abuse the API with excessive requests
- Consider caching results for repeated analysis

## Advanced Usage

### Custom Analysis Functions
```python
from advanced_game_analysis import *

# Get raw games data
games = get_recent_games("username", 100)

# Analyze specific game
analysis = analyze_game(games[0], "username")

# Custom opening classification
opening = classify_opening("1. e4 e5 2. Nf3 Nc6")
```

### Database Operations
```python
# Direct database access
connection = get_database_connection()
stats = get_user_statistics_from_database(connection, "username")
print(f"Total games: {stats['total_games']}")
```

## Future Enhancements

Possible additions:
- Time-based analysis (performance by time of day)
- Opponent strength analysis
- Opening repertoire suggestions
- Tournament performance tracking
- Rating prediction models
- Export to CSV/Excel formats

---

**Need Help?** 
- Check the Chess.com API documentation
- Review the code comments for detailed explanations
- Test with known usernames first (e.g., "hikaru", "magnuscarlsen")
- Start with basic scripts before using advanced features
