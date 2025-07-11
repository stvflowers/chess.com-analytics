# Chess.com Analytics - Azure AD Database Integration Guide

This guide covers the updated Chess.com analytics script that uses Azure AD authentication with App Registration for secure database access.

## Overview

The script now uses:
- **Azure AD App Registration** for authentication (no more username/password)
- **Configuration file** for storing connection details
- **Simplified command-line interface**

## Prerequisites

1. **Azure SQL Database** with your chess analytics schema
2. **Azure AD App Registration** with appropriate permissions
3. **Python packages**: `pip install pyodbc azure-identity`

## Azure Setup

### 1. Create App Registration

1. Go to Azure Portal → Azure Active Directory → App registrations
2. Click "New registration"
3. Name: `Chess Analytics App`
4. Click "Register"
5. Note down:
   - **Tenant ID** (Directory/tenant ID)
   - **Client ID** (Application/client ID)

### 2. Create Client Secret

1. In your App Registration, go to "Certificates & secrets"
2. Click "New client secret"
3. Description: `Chess Analytics Secret`
4. Expiration: Choose appropriate duration
5. Click "Add"
6. **Copy the secret value immediately** (it won't be shown again)

### 3. Grant Database Permissions

1. Go to your Azure SQL Database
2. Open Query Editor or connect via SQL Server Management Studio
3. Run these commands to create a user for your App Registration:

```sql
-- Create user for App Registration
CREATE USER [Chess Analytics App] FROM EXTERNAL PROVIDER;

-- Grant necessary permissions
ALTER ROLE db_datareader ADD MEMBER [Chess Analytics App];
ALTER ROLE db_datawriter ADD MEMBER [Chess Analytics App];
ALTER ROLE db_ddladmin ADD MEMBER [Chess Analytics App];

-- If using stored procedures, grant execute permissions
GRANT EXECUTE ON SCHEMA::dbo TO [Chess Analytics App];
```

## Configuration

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Create Database Configuration

Run the script once with `--use-database` to create the template:

```bash
python3 advanced_game_analysis.py --use-database
```

This creates `database_config.json`:

```json
{
    "server": "your-server.database.windows.net",
    "database": "your-database",
    "tenant_id": "your-azure-ad-tenant-id",
    "client_id": "your-app-registration-client-id",
    "client_secret": "your-app-registration-client-secret",
    "driver": "{ODBC Driver 17 for SQL Server}"
}
```

### 3. Edit Configuration File

Replace the placeholder values with your actual Azure details:

- **server**: Your Azure SQL server name (e.g., `myserver.database.windows.net`)
- **database**: Your database name (e.g., `chess_analytics`)
- **tenant_id**: Your Azure AD tenant ID
- **client_id**: Your App Registration client ID  
- **client_secret**: Your App Registration client secret

### 4. Secure the Configuration

The `database_config.json` file is automatically added to `.gitignore` to prevent accidental commits of sensitive data.

## Usage Examples

### Basic Analysis (No Database)
```bash
# Analyze without database storage
python3 advanced_game_analysis.py hikaru --num-games 50
```

### Database-Enabled Analysis
```bash
# Analyze with database storage (requires configured database_config.json)
python3 advanced_game_analysis.py your_username --use-database --num-games 100
```

### Command-Line Options

| Option | Description | Default |
|--------|-------------|---------|
| `username` | Chess.com username to analyze | goose_o7 |
| `--num-games` / `-n` | Number of games to analyze | 30 |
| `--use-database` | Enable database storage | False |

## Security Best Practices

### 1. Configuration File Security
```bash
# Ensure config file has restricted permissions
chmod 600 database_config.json

# Verify it's in .gitignore
grep database_config.json .gitignore
```

### 2. App Registration Security
- Use descriptive names for App Registrations
- Set appropriate secret expiration dates
- Rotate secrets regularly
- Use least-privilege permissions

### 3. Environment-Based Configuration (Alternative)

For production deployments, consider using environment variables:

```bash
# Set environment variables
export AZURE_TENANT_ID="your-tenant-id"
export AZURE_CLIENT_ID="your-client-id"  
export AZURE_CLIENT_SECRET="your-client-secret"
export SQL_SERVER="your-server.database.windows.net"
export SQL_DATABASE="chess_analytics"
```

Then modify `database_config.json` to use environment variables:
```json
{
    "server": "${SQL_SERVER}",
    "database": "${SQL_DATABASE}",
    "tenant_id": "${AZURE_TENANT_ID}",
    "client_id": "${AZURE_CLIENT_ID}",
    "client_secret": "${AZURE_CLIENT_SECRET}",
    "driver": "{ODBC Driver 17 for SQL Server}"
}
```

## Troubleshooting

### Common Issues

1. **"azure-identity not available"**
   ```bash
   pip install azure-identity
   ```

2. **"Failed to get access token"**
   - Verify tenant ID, client ID, and client secret
   - Check that App Registration is not expired
   - Ensure client secret is not expired

3. **"Login failed for user"**
   - Verify the App Registration user exists in SQL Database
   - Check database permissions for the App Registration
   - Ensure App Registration name matches exactly

4. **"database_config.json not found"**
   - Run with `--use-database` once to create template
   - Ensure file is in the same directory as the script

### Testing Connection

Test your database connection:

```bash
# Test with a small number of games first
python3 advanced_game_analysis.py test_user --use-database --num-games 5
```

## Migration from Old Version

If you were using the previous version with username/password authentication:

### Old Method (Deprecated)
```bash
python3 advanced_game_analysis.py user --use-database \
    --server server.database.windows.net \
    --database chess_db \
    --db-username sqluser \
    --password sqlpass
```

### New Method (Current)
```bash
# 1. Create and configure database_config.json
python3 advanced_game_analysis.py --use-database  # Creates template
# 2. Edit database_config.json with Azure AD details
# 3. Run analysis
python3 advanced_game_analysis.py user --use-database
```

## Automation

### Cron Job Example
```bash
# Daily analysis at 6 AM
0 6 * * * cd /path/to/chess-analytics && python3 advanced_game_analysis.py your_username --use-database --num-games 10
```

### Batch Processing Script
```bash
#!/bin/bash
# analyze_multiple_users.sh

USERS=("user1" "user2" "user3")

for user in "${USERS[@]}"
do
    echo "Analyzing $user..."
    python3 advanced_game_analysis.py "$user" --use-database --num-games 25
    sleep 10  # Respect API rate limits
done
```

## Benefits of Azure AD Authentication

- ✅ **No passwords in scripts** - Uses secure token-based authentication
- ✅ **Centralized access management** - Control access through Azure AD
- ✅ **Audit trails** - Azure AD logs all authentication attempts
- ✅ **Token rotation** - Access tokens automatically expire and refresh
- ✅ **Conditional access** - Can apply Azure AD conditional access policies
- ✅ **Multi-factor authentication** - Can require MFA for sensitive operations

This approach provides enterprise-grade security for your Chess.com analytics database!
