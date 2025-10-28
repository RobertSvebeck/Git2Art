-- Git2Art Database Schema
-- MariaDB/MySQL compatible

-- Table for storing generated artwork metadata
CREATE TABLE IF NOT EXISTS artworks (
    id INT AUTO_INCREMENT PRIMARY KEY,
    repo_url VARCHAR(512) NOT NULL,
    repo_name VARCHAR(255) NOT NULL,
    commit_hash VARCHAR(40) NOT NULL,
    art_style VARCHAR(50) NOT NULL DEFAULT 'default',
    image_path VARCHAR(512) NOT NULL,
    image_filename VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    like_count INT DEFAULT 0,
    INDEX idx_repo_url (repo_url),
    INDEX idx_commit_hash (commit_hash),
    INDEX idx_art_style (art_style),
    INDEX idx_created_at (created_at),
    INDEX idx_like_count (like_count),
    UNIQUE KEY unique_repo_commit_style (repo_url, commit_hash, art_style)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Table for tracking artwork likes
CREATE TABLE IF NOT EXISTS artwork_likes (
    id INT AUTO_INCREMENT PRIMARY KEY,
    artwork_id INT NOT NULL,
    user_identifier VARCHAR(255) NOT NULL,
    liked_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_artwork_id (artwork_id),
    INDEX idx_user_identifier (user_identifier),
    UNIQUE KEY unique_user_artwork (artwork_id, user_identifier),
    FOREIGN KEY (artwork_id) REFERENCES artworks(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
