CREATE DATABASE cloud_storage;

USE cloud_storage;

CREATE TABLE file_metadata (
    id INT AUTO_INCREMENT PRIMARY KEY,
    file_name VARCHAR(255) NOT NULL,
    display_name VARCHAR(255) NOT NULL,
    file_path VARCHAR(255) NOT NULL,
    file_hash VARCHAR(64) NOT NULL,
    file_size BIGINT NOT NULL,
    original_file_id INT DEFAULT NULL,
    is_duplicate BOOLEAN DEFAULT FALSE,
    FOREIGN KEY (original_file_id) REFERENCES file_metadata(id)
);


select * from file_metadata;

drop table file_metadata;