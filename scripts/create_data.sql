-- Create the soldiers table according to exam requirements
-- Database: enemy_soldiers, Collection: soldier_details
-- But using MySQL so we create equivalent table structure

CREATE TABLE IF NOT EXISTS soldier_details (
    ID INT PRIMARY KEY,
    first_name VARCHAR(50) NOT NULL,
    last_name VARCHAR(50) NOT NULL,
    phone_number BIGINT NOT NULL,
    rank VARCHAR(50) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

-- Create index on ID for better performance (even though it's primary key)
CREATE INDEX idx_soldier_id ON soldier_details(ID);

-- Legacy table for backward compatibility
CREATE TABLE IF NOT EXISTS data (
    ID INT AUTO_INCREMENT PRIMARY KEY,
    first_name VARCHAR(50) NOT NULL,
    last_name VARCHAR(50) NOT NULL
);