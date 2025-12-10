-- Chess.com Analytics Database Schema - Azure SQL Basic Syntax
-- This file uses the most basic SQL syntax to avoid any token parsing issues

-- =============================================================================
-- MAIN TABLES (Basic syntax only)
-- =============================================================================

-- Table to store individual chess games and their analysis
CREATE TABLE chess_games (
    id INT IDENTITY(1,1) PRIMARY KEY,
    username NVARCHAR(50) NOT NULL,
    game_url NVARCHAR(255) UNIQUE,
    game_date DATE,
    created_at DATETIME2 DEFAULT GETDATE(),
    updated_at DATETIME2 DEFAULT GETDATE(),
    
    -- Game outcome and player information
    result NVARCHAR(10) NOT NULL,
    user_color NVARCHAR(5) NOT NULL,
    
    -- Rating information
    user_rating INT,
    opponent_rating INT,
    opponent_name NVARCHAR(50),
    rating_difference AS (user_rating - opponent_rating),
    
    -- Game analysis metrics
    accuracy DECIMAL(4,1),
    time_control NVARCHAR(20),
    
    -- Opening analysis
    first_moves NVARCHAR(MAX),
    opening_name NVARCHAR(100),
    opening_category NVARCHAR(50),
    
    -- Additional metadata
    pgn_data NVARCHAR(MAX),
    analysis_version NVARCHAR(10) DEFAULT '1.0'
);

-- Table to store aggregated user statistics
CREATE TABLE user_statistics (
    id INT IDENTITY(1,1) PRIMARY KEY,
    username NVARCHAR(50) UNIQUE NOT NULL,
    last_updated DATETIME2 DEFAULT GETDATE(),
    
    -- Performance statistics
    total_games INT DEFAULT 0,
    wins INT DEFAULT 0,
    losses INT DEFAULT 0,
    draws INT DEFAULT 0,
    win_rate DECIMAL(5,2),
    
    -- Rating statistics
    current_rating INT,
    highest_rating INT,
    lowest_rating INT,
    avg_rating DECIMAL(7,2),
    rating_change INT,
    
    -- Accuracy statistics
    avg_accuracy DECIMAL(4,1),
    best_accuracy DECIMAL(4,1),
    worst_accuracy DECIMAL(4,1),
    games_with_accuracy INT DEFAULT 0,
    
    -- Time period for this analysis
    analysis_start_date DATE,
    analysis_end_date DATE,
    games_analyzed INT DEFAULT 0
);

-- Table to track opening performance
CREATE TABLE opening_statistics (
    id INT IDENTITY(1,1) PRIMARY KEY,
    username NVARCHAR(50) NOT NULL,
    opening_name NVARCHAR(100) NOT NULL,
    
    -- Performance with this opening
    games_played INT DEFAULT 0,
    wins INT DEFAULT 0,
    losses INT DEFAULT 0,
    draws INT DEFAULT 0,
    win_rate DECIMAL(5,2),
    
    -- Rating performance
    avg_rating DECIMAL(7,2),
    avg_opponent_rating DECIMAL(7,2),
    avg_accuracy DECIMAL(4,1),
    
    -- Timestamps
    first_played DATE,
    last_played DATE,
    last_updated DATETIME2 DEFAULT GETDATE()
);

-- Table to track time control performance
CREATE TABLE time_control_statistics (
    id INT IDENTITY(1,1) PRIMARY KEY,
    username NVARCHAR(50) NOT NULL,
    time_control NVARCHAR(20) NOT NULL,
    
    -- Performance stats
    games_played INT DEFAULT 0,
    wins INT DEFAULT 0,
    losses INT DEFAULT 0,
    draws INT DEFAULT 0,
    win_rate DECIMAL(5,2),
    
    -- Rating and accuracy
    avg_rating DECIMAL(7,2),
    avg_accuracy DECIMAL(4,1),
    
    last_updated DATETIME2 DEFAULT GETDATE()
);

-- =============================================================================
-- ADD UNIQUE CONSTRAINTS SEPARATELY
-- =============================================================================

ALTER TABLE opening_statistics 
ADD CONSTRAINT UQ_opening_stats UNIQUE(username, opening_name);

ALTER TABLE time_control_statistics 
ADD CONSTRAINT UQ_time_control_stats UNIQUE(username, time_control);

-- =============================================================================
-- INDEXES FOR PERFORMANCE
-- =============================================================================

CREATE NONCLUSTERED INDEX IX_chess_games_username_date 
ON chess_games(username, game_date DESC);

CREATE NONCLUSTERED INDEX IX_chess_games_opening 
ON chess_games(opening_name);

CREATE NONCLUSTERED INDEX IX_chess_games_result 
ON chess_games(result);

CREATE NONCLUSTERED INDEX IX_chess_games_rating 
ON chess_games(user_rating);

CREATE NONCLUSTERED INDEX IX_chess_games_time_control 
ON chess_games(time_control);

CREATE NONCLUSTERED INDEX IX_chess_games_accuracy 
ON chess_games(accuracy);

CREATE NONCLUSTERED INDEX IX_chess_games_user_result_date 
ON chess_games(username, result, game_date);

CREATE NONCLUSTERED INDEX IX_chess_games_user_opening_result 
ON chess_games(username, opening_name, result);

-- =============================================================================
-- STORED PROCEDURES FOR DATA MANAGEMENT
-- =============================================================================

CREATE PROCEDURE sp_upsert_game_analysis
    @username NVARCHAR(50),
    @game_url NVARCHAR(255),
    @game_date DATE,
    @result NVARCHAR(10),
    @user_color NVARCHAR(5),
    @user_rating INT,
    @opponent_rating INT,
    @opponent_name NVARCHAR(50),
    @accuracy DECIMAL(4,1),
    @time_control NVARCHAR(20),
    @first_moves NVARCHAR(MAX),
    @opening_name NVARCHAR(100)
AS
BEGIN
    SET NOCOUNT ON;
    
    DECLARE @existing_count INT;
    
    SELECT @existing_count = COUNT(*) 
    FROM chess_games 
    WHERE game_url = @game_url;
    
    IF @existing_count > 0
    BEGIN
        UPDATE chess_games 
        SET username = @username,
            game_date = @game_date,
            result = @result,
            user_color = @user_color,
            user_rating = @user_rating,
            opponent_rating = @opponent_rating,
            opponent_name = @opponent_name,
            accuracy = @accuracy,
            time_control = @time_control,
            first_moves = @first_moves,
            opening_name = @opening_name,
            updated_at = GETDATE()
        WHERE game_url = @game_url;
    END
    ELSE
    BEGIN
        INSERT INTO chess_games (
            username, game_url, game_date, result, user_color, user_rating, 
            opponent_rating, opponent_name, accuracy, time_control, first_moves, opening_name
        )
        VALUES (
            @username, @game_url, @game_date, @result, @user_color, @user_rating,
            @opponent_rating, @opponent_name, @accuracy, @time_control, @first_moves, @opening_name
        );
    END
END;

CREATE PROCEDURE sp_update_user_statistics
    @username NVARCHAR(50)
AS
BEGIN
    SET NOCOUNT ON;
    
    DECLARE @total_games INT;
    DECLARE @wins INT;
    DECLARE @losses INT;
    DECLARE @draws INT;
    DECLARE @win_rate DECIMAL(5,2);
    DECLARE @highest_rating INT;
    DECLARE @lowest_rating INT;
    DECLARE @avg_rating DECIMAL(7,2);
    DECLARE @avg_accuracy DECIMAL(4,1);
    DECLARE @best_accuracy DECIMAL(4,1);
    DECLARE @worst_accuracy DECIMAL(4,1);
    DECLARE @games_with_accuracy INT;
    DECLARE @analysis_start_date DATE;
    DECLARE @analysis_end_date DATE;
    DECLARE @current_rating INT;
    DECLARE @first_rating INT;
    DECLARE @rating_change INT;
    DECLARE @existing_count INT;
    
    -- Calculate statistics
    SELECT 
        @total_games = COUNT(*),
        @wins = SUM(CASE WHEN result = 'Win' THEN 1 ELSE 0 END),
        @losses = SUM(CASE WHEN result = 'Loss' THEN 1 ELSE 0 END),
        @draws = SUM(CASE WHEN result = 'Draw' THEN 1 ELSE 0 END),
        @highest_rating = MAX(user_rating),
        @lowest_rating = MIN(user_rating),
        @avg_rating = AVG(CAST(user_rating AS FLOAT)),
        @avg_accuracy = AVG(accuracy),
        @best_accuracy = MAX(accuracy),
        @worst_accuracy = MIN(accuracy),
        @games_with_accuracy = COUNT(CASE WHEN accuracy IS NOT NULL THEN 1 END),
        @analysis_start_date = MIN(game_date),
        @analysis_end_date = MAX(game_date)
    FROM chess_games 
    WHERE username = @username;
    
    -- Calculate win rate
    SET @win_rate = 0;
    IF @total_games > 0
        SET @win_rate = (@wins * 100.0) / @total_games;
    
    -- Get current rating
    SELECT TOP 1 @current_rating = user_rating 
    FROM chess_games 
    WHERE username = @username AND user_rating IS NOT NULL 
    ORDER BY game_date DESC, id DESC;
    
    -- Get first rating
    SELECT TOP 1 @first_rating = user_rating 
    FROM chess_games 
    WHERE username = @username AND user_rating IS NOT NULL 
    ORDER BY game_date ASC, id ASC;
    
    -- Calculate rating change
    SET @rating_change = ISNULL(@current_rating, 0) - ISNULL(@first_rating, 0);
    
    -- Check if user exists
    SELECT @existing_count = COUNT(*) 
    FROM user_statistics 
    WHERE username = @username;
    
    IF @existing_count > 0
    BEGIN
        UPDATE user_statistics 
        SET total_games = @total_games,
            wins = @wins,
            losses = @losses,
            draws = @draws,
            win_rate = @win_rate,
            current_rating = @current_rating,
            highest_rating = @highest_rating,
            lowest_rating = @lowest_rating,
            avg_rating = @avg_rating,
            avg_accuracy = @avg_accuracy,
            best_accuracy = @best_accuracy,
            worst_accuracy = @worst_accuracy,
            games_with_accuracy = @games_with_accuracy,
            analysis_start_date = @analysis_start_date,
            analysis_end_date = @analysis_end_date,
            games_analyzed = @total_games,
            rating_change = @rating_change,
            last_updated = GETDATE()
        WHERE username = @username;
    END
    ELSE
    BEGIN
        INSERT INTO user_statistics (
            username, total_games, wins, losses, draws, win_rate,
            current_rating, highest_rating, lowest_rating, avg_rating,
            avg_accuracy, best_accuracy, worst_accuracy, games_with_accuracy,
            analysis_start_date, analysis_end_date, games_analyzed, rating_change
        )
        VALUES (
            @username, @total_games, @wins, @losses, @draws, @win_rate,
            @current_rating, @highest_rating, @lowest_rating, @avg_rating,
            @avg_accuracy, @best_accuracy, @worst_accuracy, @games_with_accuracy,
            @analysis_start_date, @analysis_end_date, @total_games, @rating_change
        );
    END
END;

-- =============================================================================
-- VALIDATION FUNCTIONS (Optional - can be skipped if causing issues)
-- =============================================================================

CREATE FUNCTION fn_validate_result(@result NVARCHAR(10))
RETURNS BIT
AS
BEGIN
    DECLARE @is_valid BIT = 0;
    
    IF @result = 'Win' SET @is_valid = 1;
    IF @result = 'Loss' SET @is_valid = 1;
    IF @result = 'Draw' SET @is_valid = 1;
    IF @result = 'Unknown' SET @is_valid = 1;
    
    RETURN @is_valid;
END;

CREATE FUNCTION fn_validate_color(@color NVARCHAR(5))
RETURNS BIT
AS
BEGIN
    DECLARE @is_valid BIT = 0;
    
    IF @color = 'White' SET @is_valid = 1;
    IF @color = 'Black' SET @is_valid = 1;
    
    RETURN @is_valid;
END;