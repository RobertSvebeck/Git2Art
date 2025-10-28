-- Migration: Add art_style field to artworks table
-- Run this directly on your database server

USE bravoose_git2art;

-- Check if column already exists (safe to run multiple times)
SET @col_exists = 0;
SELECT COUNT(*) INTO @col_exists
FROM information_schema.COLUMNS
WHERE TABLE_SCHEMA = 'bravoose_git2art'
AND TABLE_NAME = 'artworks'
AND COLUMN_NAME = 'art_style';

-- Add art_style column if it doesn't exist
SET @sql = IF(@col_exists = 0,
    'ALTER TABLE artworks ADD COLUMN art_style VARCHAR(50) NOT NULL DEFAULT ''default'' AFTER commit_hash',
    'SELECT ''Column art_style already exists'' AS message');
PREPARE stmt FROM @sql;
EXECUTE stmt;
DEALLOCATE PREPARE stmt;

-- Add index on art_style if it doesn't exist
SET @idx_exists = 0;
SELECT COUNT(*) INTO @idx_exists
FROM information_schema.STATISTICS
WHERE TABLE_SCHEMA = 'bravoose_git2art'
AND TABLE_NAME = 'artworks'
AND INDEX_NAME = 'idx_art_style';

SET @sql = IF(@idx_exists = 0,
    'ALTER TABLE artworks ADD INDEX idx_art_style (art_style)',
    'SELECT ''Index idx_art_style already exists'' AS message');
PREPARE stmt FROM @sql;
EXECUTE stmt;
DEALLOCATE PREPARE stmt;

-- Update existing records to have 'default' style
UPDATE artworks
SET art_style = 'default'
WHERE art_style = '' OR art_style IS NULL;

SELECT CONCAT('Updated ', ROW_COUNT(), ' existing artworks to default style') AS message;

-- Drop old unique constraint if it exists
SET @constraint_exists = 0;
SELECT COUNT(*) INTO @constraint_exists
FROM information_schema.STATISTICS
WHERE TABLE_SCHEMA = 'bravoose_git2art'
AND TABLE_NAME = 'artworks'
AND INDEX_NAME = 'unique_repo_commit';

SET @sql = IF(@constraint_exists > 0,
    'ALTER TABLE artworks DROP INDEX unique_repo_commit',
    'SELECT ''Old constraint unique_repo_commit does not exist'' AS message');
PREPARE stmt FROM @sql;
EXECUTE stmt;
DEALLOCATE PREPARE stmt;

-- Add new unique constraint including art_style if it doesn't exist
SET @new_constraint_exists = 0;
SELECT COUNT(*) INTO @new_constraint_exists
FROM information_schema.STATISTICS
WHERE TABLE_SCHEMA = 'bravoose_git2art'
AND TABLE_NAME = 'artworks'
AND INDEX_NAME = 'unique_repo_commit_style';

SET @sql = IF(@new_constraint_exists = 0,
    'ALTER TABLE artworks ADD UNIQUE KEY unique_repo_commit_style (repo_url, commit_hash, art_style)',
    'SELECT ''Constraint unique_repo_commit_style already exists'' AS message');
PREPARE stmt FROM @sql;
EXECUTE stmt;
DEALLOCATE PREPARE stmt;

-- Verify the migration
SELECT
    'Migration complete!' AS status,
    COUNT(*) AS total_artworks,
    COUNT(DISTINCT art_style) AS unique_styles
FROM artworks;

-- Show sample of artworks with their styles
SELECT id, repo_name, commit_hash, art_style, created_at
FROM artworks
ORDER BY created_at DESC
LIMIT 5;
