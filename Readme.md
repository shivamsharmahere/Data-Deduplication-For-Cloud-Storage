# Data Deduplication System 🗃️

A web-based file storage system that implements data deduplication to efficiently manage storage space by detecting and handling duplicate files.

## 🌟 Features

- File upload with automatic duplicate detection
- SHA-256 hash-based deduplication
- Real-time file size display
- Intuitive web interface
- Multiple delete options for managing duplicates
- Support for viewing duplicate file listings
- Storage space optimization

## 🔧 Technology Stack

- **Backend:** Python (Flask)
- **Frontend:** HTML, CSS, JavaScript
- **Database:** MySQL
- **File Processing:** Python's hashlib for SHA-256 hashing

## 📋 Prerequisites

Before running this project, make sure you have the following installed:

- Python 3.x
- MySQL Server
- pip (Python package manager)

## 🚀 Installation & Setup

1. **Clone the repository**
   ```bash
   git clone [your-repository-url]
   cd data-deduplication-system
   ```

2. **Install Python dependencies**
   ```bash
   pip install flask mysql-connector-python werkzeug
   ```

3. **Set up the MySQL database**
   ```sql
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
   ```

4. **Configure database connection**
   - Open `app.py`
   - Update the database connection parameters:
     ```python
     def connect_to_database():
         return mysql.connector.connect(
             host="localhost",
             user="your_username",
             password="your_password",
             database="cloud_storage"
         )
     ```

5. **Create upload directory**
   - The system will automatically create an 'uploads' directory in the project root
   - Ensure the application has write permissions to this directory

## 🎯 Usage

1. **Start the Flask server**
   ```bash
   python app.py
   ```

2. **Access the application**
   - Open your web browser
   - Navigate to `http://localhost:5000`
   - You should see the file upload interface

3. **Upload files**
   - Click "Choose File" to select a file
   - Click "Upload File" to process the file
   - The system will automatically detect duplicates

4. **Manage files**
   - View all files in the table
   - See original files and their duplicates
   - Use different delete options:
     - Delete original only
     - Delete duplicates only
     - Delete all related files

## 💡 How It Works

1. **File Upload Process**
   - User selects and uploads a file
   - System calculates SHA-256 hash of the file
   - Checks database for existing hash
   - Either stores new file or creates reference to existing file

2. **Deduplication Method**
   - Uses content-based deduplication
   - SHA-256 hashing ensures reliable duplicate detection
   - Maintains file metadata while saving storage space

3. **Storage Management**
   - Original files stored with full content
   - Duplicates stored as references
   - Efficient storage utilization

## 🔒 Security Considerations

- Implements secure filename handling
- Uses prepared SQL statements to prevent SQL injection
- Validates file uploads
- Implements proper file path handling

## 🤝 Contributing

Contributions are welcome! Here's how you can help:

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 📧 Contact

Your Name - [shivampurohit9145@gmail.com]
Project Link: [https://github.com/shivamsharmahere/Data-Deduplication-For-Cloud-Storage]
