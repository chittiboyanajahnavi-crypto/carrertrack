-- ============================================================================
-- Student Placement & Internship Management System (CareerTrack)
-- Script 01: Database Initialization & Dedicated User Setup
-- ============================================================================
-- Execute this script as root (via MySQL Workbench or MySQL CLI):
--   mysql -u root -p < database/01_init_db_and_user.sql
-- ============================================================================

-- 1. Create the database with full UTF-8 Unicode support
CREATE DATABASE IF NOT EXISTS careertrack_db
    CHARACTER SET utf8mb4
    COLLATE utf8mb4_unicode_ci;

-- 2. Create the dedicated application user
-- NOTE: You may customize 'CareerTrack@2026' to your own secure password.
-- Match this password with DB_PASSWORD in backend/.env.
CREATE USER IF NOT EXISTS 'careertrack_user'@'localhost' 
    IDENTIFIED BY 'CareerTrack@2026';

-- 3. Grant privileges ONLY on the careertrack_db database (principle of least privilege)
GRANT ALL PRIVILEGES ON careertrack_db.* TO 'careertrack_user'@'localhost';

-- 4. Apply changes
FLUSH PRIVILEGES;

-- 5. Verification query
SELECT user, host FROM mysql.user WHERE user = 'careertrack_user';
SHOW GRANTS FOR 'careertrack_user'@'localhost';
