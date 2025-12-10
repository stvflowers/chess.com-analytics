# Date and Time Filtering Guide

The Chess.com Analytics tool now supports filtering games by specific dates and times. This allows you to analyze performance during particular periods, such as tournaments, training sessions, or specific time ranges.

## Date Filtering Options

### Basic Date Range
Filter games between two dates:
```bash
python3 advanced_game_analysis.py hikaru --start-date 2024-01-01 --end-date 2024-12-31
```

### Date with Time Range
Filter games with specific start and end times:
```bash
python3 advanced_game_analysis.py hikaru --start-date 2024-06-15 --start-time 14:00 --end-date 2024-06-15 --end-time 18:00
```

### From a Specific Date Onwards
Analyze all games from a certain date to present:
```bash
python3 advanced_game_analysis.py hikaru --start-date 2024-06-01 --num-games 100
```

### Up to a Specific Date
Analyze games up to a certain date:
```bash
python3 advanced_game_analysis.py hikaru --end-date 2024-05-31 --num-games 50
```

## Date and Time Formats

- **Date Format**: `YYYY-MM-DD` (e.g., `2024-01-01`)
- **Time Format**: `HH:MM` (24-hour format, e.g., `14:30` for 2:30 PM)

## Time Zone Behavior

- All times are interpreted in UTC (Chess.com's standard)
- If no time is specified with a date:
  - `start-date` defaults to `00:00` (beginning of day)
  - `end-date` defaults to `23:59:59` (end of day)

## Practical Examples

### Tournament Analysis
Analyze performance during a specific tournament:
```bash
python3 advanced_game_analysis.py your_username --start-date 2024-03-15 --end-date 2024-03-22 --use-database
```

### Evening Session Analysis
Analyze games played in the evening:
```bash
python3 advanced_game_analysis.py your_username --start-date 2024-01-01 --start-time 18:00 --end-date 2024-12-31 --end-time 23:59
```

### Weekend Games
Analyze weekend performance (you'll need to run separate commands for different dates):
```bash
# Saturday games
python3 advanced_game_analysis.py your_username --start-date 2024-06-01 --end-date 2024-06-01

# Sunday games  
python3 advanced_game_analysis.py your_username --start-date 2024-06-02 --end-date 2024-06-02
```

### Monthly Performance
Analyze performance for a specific month:
```bash
python3 advanced_game_analysis.py your_username --start-date 2024-06-01 --end-date 2024-06-30
```

### Recent Week Analysis
Analyze last week's games:
```bash
python3 advanced_game_analysis.py your_username --start-date 2024-12-25 --end-date 2024-12-31
```

## Multi-User Date Filtering

Date filtering works with batch processing too:
```bash
python3 advanced_game_analysis.py hikaru magnuscarlsen --start-date 2024-01-01 --end-date 2024-06-30 --delay 3.0
```

## Database Integration

Date filtering works seamlessly with database storage:
```bash
python3 advanced_game_analysis.py your_username --start-date 2024-01-01 --end-date 2024-12-31 --use-database
```

## Tips

1. **Large Date Ranges**: For very large date ranges, consider using `--num-games` to limit the number of games analyzed
2. **API Rate Limits**: When filtering large periods, the tool automatically searches multiple months - this is normal
3. **No Games Found**: If no games are found in the specified range, check your date format and ensure games exist in that period
4. **Time Precision**: The filtering uses the game's end time from Chess.com's API

## Error Handling

The tool will show helpful error messages for:
- Invalid date formats
- Start date after end date
- Invalid time formats

Example error handling:
```bash
python3 advanced_game_analysis.py hikaru --start-date 2024-13-01  # Invalid month
# ❌ Error parsing date/time: time data '2024-13-01' does not match format '%Y-%m-%d'
```
