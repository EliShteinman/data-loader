-- This script creates the 'data' table required by the application.
CREATE TABLE IF NOT EXISTS data (
    ID INT AUTO_INCREMENT PRIMARY KEY,
    first_name VARCHAR(50) NOT NULL,
    last_name VARCHAR(50) NOT NULL
);