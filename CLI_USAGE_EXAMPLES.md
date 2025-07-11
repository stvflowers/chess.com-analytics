# Chess.com Advanced Game Analysis - Usage Examples

The updated `advanced_game_analysis.py` now supports command-line arguments for better automation and scripting capabilities.

## Command-Line Usage

### Basic Usage (No Database)

```bash
# Analyze default user (goose_o7) with default settings
python3 advanced_game_analysis.py

# Analyze specific user with 50 games
python3 advanced_game_analysis.py hikaru --num-games 50

# Analyze with short form argument
python3 advanced_game_analysis.py magnuscarlsen -n 25
```

### Database Integration

```bash
# Enable database storage with all required parameters
python3 advanced_game_analysis.py your_username \
    --use-database \
    --server your-server.database.windows.net \
    --database chess_analytics \
    --db-username your_db_user \
    --password your_password \
    --num-games 100
```

### Interactive Mode

```bash
# Use interactive mode (prompts for database configuration)
python3 advanced_game_analysis.py --interactive
```

## Available Arguments

| Argument | Short | Type | Default | Description |
|----------|-------|------|---------|-------------|
| `username` | - | str | goose_o7 | Chess.com username to analyze |
| `--num-games` | `-n` | int | 30 | Number of games to analyze |
| `--use-database` | - | flag | False | Enable database storage |
| `--server` | - | str | - | Azure SQL Server name |
| `--database` | - | str | - | Database name |
| `--db-username` | - | str | - | Database username |
| `--password` | - | str | - | Database password |
| `--interactive` | - | flag | False | Use interactive mode |
| `--help` | `-h` | - | - | Show help message |

## Examples for Different Scenarios

### 1. Quick Analysis
```bash
# Just analyze a player quickly
python3 advanced_game_analysis.py hikaru -n 10
```

### 2. Comprehensive Analysis
```bash
# Detailed analysis with many games
python3 advanced_game_analysis.py gothamchess --num-games 200
```

### 3. Automated Database Storage
```bash
# Perfect for cron jobs or automated scripts
python3 advanced_game_analysis.py your_username \
    --use-database \
    --server your-server.database.windows.net \
    --database chess_analytics \
    --db-username chess_user \
    --password your_secure_password \
    --num-games 50
```

### 4. Development/Testing
```bash
# Interactive mode for testing database connections
python3 advanced_game_analysis.py --interactive
```

## Programmatic Usage

You can also use the functions directly in Python:

```python
from advanced_game_analysis import analyze_user_games, configure_database

# Configure database
configure_database(
    server="your-server.database.windows.net",
    database="chess_analytics", 
    username="your_user",
    password="your_password"
)

# Run analysis with database
analyze_user_games("hikaru", num_games=50, save_to_database=True)

# Run analysis without database
analyze_user_games("magnuscarlsen", num_games=30, save_to_database=False)
```

## Error Handling

The script gracefully handles various error conditions:

- **Missing pyodbc**: Database features are disabled with a warning
- **Incomplete database config**: Analysis continues without database
- **Invalid username**: Clear error message displayed
- **API rate limits**: Continues processing what it can

## Security Best Practices

When using database features:

1. **Environment Variables**: Store credentials in environment variables
```bash
export DB_SERVER="your-server.database.windows.net"
export DB_NAME="chess_analytics"  
export DB_USER="your_username"
export DB_PASS="your_password"

python3 advanced_game_analysis.py hikaru --use-database \
    --server "$DB_SERVER" \
    --database "$DB_NAME" \
    --db-username "$DB_USER" \
    --password "$DB_PASS"
```

2. **Configuration Files**: Use a config file (add to .gitignore)
```bash
# Create config.json (don't commit to git!)
echo '{"server":"your-server","database":"chess_db","username":"user","password":"pass"}' > config.json
```

3. **Interactive Mode**: For development and testing
```bash
python3 advanced_game_analysis.py --interactive
```

## Migration from Old Version

If you were using the old interactive version:

**Old way:**
```bash
python3 advanced_game_analysis.py
# Then type inputs when prompted
```

**New way:**
```bash
# Option 1: Command-line arguments
python3 advanced_game_analysis.py hikaru --num-games 50

# Option 2: Still use interactive mode
python3 advanced_game_analysis.py --interactive
```

## Automation Examples

### Cron Job for Daily Analysis
```bash
# Add to crontab for daily analysis at 6 AM
0 6 * * * cd /path/to/chess-analytics && python3 advanced_game_analysis.py your_username --use-database --server your-server.database.windows.net --database chess_analytics --db-username your_user --password your_pass --num-games 10
```

### Batch Processing Multiple Users
```bash
#!/bin/bash
# analyze_multiple_users.sh

USERS=("hikaru" "magnuscarlsen" "gothamchess" "your_username")

for user in "${USERS[@]}"
do
    echo "Analyzing $user..."
    python3 advanced_game_analysis.py "$user" \
        --use-database \
        --server your-server.database.windows.net \
        --database chess_analytics \
        --db-username your_user \
        --password your_password \
        --num-games 25
done
```

This updated version provides much more flexibility while maintaining backward compatibility through the `--interactive` flag!
