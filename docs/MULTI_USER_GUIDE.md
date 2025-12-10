# Chess.com Analytics - Multi-User Support Examples

The updated Chess.com analytics script now supports analyzing multiple users in a single command, making it perfect for batch processing and comparative analysis.

## New Features

### 1. Multiple Username Support
- Accept single username or list of usernames
- Automatic batch processing with progress indicators
- Configurable delay between users to respect API rate limits

### 2. Enhanced Error Handling
- If one user fails, processing continues with remaining users
- Clear error messages and progress tracking
- Final summary of processed users

### 3. API Rate Limit Management
- Built-in delay between user processing
- Customizable delay timing
- Helps prevent Chess.com API rate limiting

## Usage Examples

### Single User (Same as Before)
```bash
# Basic single user analysis
python3 advanced_game_analysis.py hikaru --num-games 50

# Single user with database
python3 advanced_game_analysis.py your_username --use-database --num-games 100
```

### Multiple Users
```bash
# Analyze multiple top players
python3 advanced_game_analysis.py hikaru magnuscarlsen gothamchess --num-games 30

# Batch analysis with custom settings
python3 advanced_game_analysis.py user1 user2 user3 user4 \
    --num-games 50 \
    --delay 3.0 \
    --use-database

# Quick batch analysis with minimal games
python3 advanced_game_analysis.py hikaru magnuscarlsen fabianocaruana \
    --num-games 10 \
    --delay 1.0
```

### Database Batch Processing
```bash
# Store analysis for multiple users in database
python3 advanced_game_analysis.py \
    hikaru magnuscarlsen gothamchess fabianocaruana \
    --use-database \
    --num-games 100 \
    --delay 5.0
```

## Command-Line Arguments

| Argument | Type | Default | Description |
|----------|------|---------|-------------|
| `usernames` | positional | goose_o7 | One or more Chess.com usernames |
| `--num-games` / `-n` | int | 30 | Games to analyze per user |
| `--use-database` | flag | False | Enable database storage |
| `--delay` | float | 2.0 | Seconds to wait between users |

## Output Format

### Single User
```
🔥 Chess.com Advanced Game Analysis with Database Integration
============================================================

🚀 Starting analysis for hikaru (30 games)...
📊 Database storage: Disabled

📊 Advanced Chess.com Game Analysis for: hikaru
[... analysis output ...]
```

### Multiple Users
```
🔥 Chess.com Advanced Game Analysis with Database Integration
============================================================

🚀 Starting batch analysis for 3 users (30 games each)...
👥 Users: hikaru, magnuscarlsen, gothamchess
⏱️  Delay between users: 2.0 seconds
📊 Database storage: Enabled

============================================================
🎯 Processing user 1/3: hikaru
============================================================
[... analysis for hikaru ...]

⏳ Waiting 2.0 seconds before processing next user...

============================================================
🎯 Processing user 2/3: magnuscarlsen
============================================================
[... analysis for magnuscarlsen ...]

⏳ Waiting 2.0 seconds before processing next user...

============================================================
🎯 Processing user 3/3: gothamchess
============================================================
[... analysis for gothamchess ...]

🏁 Batch analysis complete! Processed 3 users.
```

## Best Practices

### 1. API Rate Limiting
```bash
# For many users, use longer delays
python3 advanced_game_analysis.py user1 user2 user3 user4 user5 \
    --delay 5.0 \
    --num-games 25

# For quick testing, use minimal games
python3 advanced_game_analysis.py hikaru magnuscarlsen \
    --num-games 5 \
    --delay 1.0
```

### 2. Database Storage
```bash
# Enable database for historical tracking
python3 advanced_game_analysis.py \
    your_username friend1 friend2 \
    --use-database \
    --num-games 50 \
    --delay 3.0
```

### 3. Error Recovery
The script automatically handles errors for individual users:
```bash
# If one user fails, others continue processing
python3 advanced_game_analysis.py valid_user invalid_user another_valid_user
```

## Automation Examples

### Cron Job for Multiple Users
```bash
# Daily analysis for multiple users at 6 AM
0 6 * * * cd /path/to/chess-analytics && python3 advanced_game_analysis.py user1 user2 user3 --use-database --num-games 10 --delay 5.0
```

### Shell Script for Team Analysis
```bash
#!/bin/bash
# analyze_team.sh

# Define team members
TEAM_MEMBERS=("player1" "player2" "player3" "player4")

# Convert array to space-separated string
USERS="${TEAM_MEMBERS[*]}"

echo "Analyzing team: $USERS"

python3 advanced_game_analysis.py $USERS \
    --use-database \
    --num-games 30 \
    --delay 4.0

echo "Team analysis complete!"
```

### Python Script for Dynamic User Lists
```python
#!/usr/bin/env python3
import subprocess
import sys

# Dynamic user list from file or API
users = ["hikaru", "magnuscarlsen", "gothamchess"]

# Build command
cmd = [
    "python3", "advanced_game_analysis.py",
    *users,
    "--use-database",
    "--num-games", "25",
    "--delay", "3.0"
]

# Execute
result = subprocess.run(cmd, capture_output=True, text=True)
print(result.stdout)
if result.stderr:
    print("Errors:", result.stderr)
```

## Performance Considerations

### 1. Batch Size
- **Small batches (2-5 users)**: Use shorter delays (1-2 seconds)
- **Medium batches (5-10 users)**: Use moderate delays (3-5 seconds)  
- **Large batches (10+ users)**: Use longer delays (5-10 seconds)

### 2. Game Count per User
- **Quick overview**: 10-20 games per user
- **Standard analysis**: 30-50 games per user
- **Comprehensive analysis**: 100+ games per user

### 3. Database Performance
- Database operations are optimized for batch processing
- Each user's data is committed separately
- Failed user analysis doesn't affect other users' data

## Error Handling

The script provides robust error handling:

1. **Invalid usernames**: Continues with remaining users
2. **API errors**: Retries and continues processing
3. **Database errors**: Analysis continues without database for that user
4. **Network issues**: Graceful degradation

Example error output:
```
❌ Error analyzing invalid_user: ChessDotComClientError(status_code=404, text={"code":0,"message":"User \"invalid_user\" not found."}, url=https://api.chess.com/pub/player/invalid_user)
   Continuing with next user...
```

This makes the script reliable for automated batch processing scenarios!
