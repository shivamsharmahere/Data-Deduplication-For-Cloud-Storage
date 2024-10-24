import os
import hashlib
from flask import Flask, request, jsonify, render_template
import mysql.connector
from werkzeug.utils import secure_filename
import shutil

app = Flask(__name__)
UPLOAD_FOLDER = os.path.join(os.getcwd(), 'uploads')
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def connect_to_database():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="Shivam@123",
        database="cloud_storage"
    )

def compute_sha256(file_path):
    sha256_hash = hashlib.sha256()
    with open(file_path, "rb") as f:
        for byte_block in iter(lambda: f.read(4096), b""):
            sha256_hash.update(byte_block)
    return sha256_hash.hexdigest()

def format_size(size):
    if size == 0:
        return "0 Bytes"
    elif size < 1024:
        return f"{size} Bytes"
    elif size < 1024**2:
        return f"{size / 1024:.2f} KB"
    elif size < 1024**3:
        return f"{size / (1024**2):.2f} MB"
    else:
        return f"{size / (1024**3):.2f} GB"

@app.route('/')
def index():
    return render_template('index.html')
@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({"status": "error", "message": "No file part"})
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({"status": "error", "message": "No selected file"})

    filename = secure_filename(file.filename)
    temp_path = os.path.join(UPLOAD_FOLDER, 'temp_' + filename)
    
    file.save(temp_path)
    file_hash = compute_sha256(temp_path)
    file_size = os.path.getsize(temp_path)

    db = connect_to_database()
    cursor = db.cursor(dictionary=True)

    try:
        cursor.execute("SELECT * FROM file_metadata WHERE file_hash = %s AND is_duplicate = 0", (file_hash,))
        original_file = cursor.fetchone()

        if original_file:
            cursor.execute(
                "SELECT COUNT(*) as count FROM file_metadata WHERE file_hash = %s",
                (file_hash,)
            )
            duplicate_count = cursor.fetchone()['count']
            
            name, ext = os.path.splitext(filename)
            new_filename = f"{name}_duplicate_{duplicate_count}{ext}"
            display_name = filename + f" (Duplicate {duplicate_count})"
            final_path = os.path.join(UPLOAD_FOLDER, new_filename)
            
            with open(final_path, 'wb') as f:
                pass
            
            cursor.execute(""" 
                INSERT INTO file_metadata 
                (file_name, display_name, file_path, file_hash, file_size, original_file_id, is_duplicate) 
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """, (new_filename, display_name, final_path, file_hash, 0, original_file['id'], True))
            
            db.commit()
            os.remove(temp_path)
            
            return jsonify({
                "status": "success",
                "message": f"Duplicate file saved as {display_name}"
            })
        else:
            final_path = os.path.join(UPLOAD_FOLDER, filename)
            shutil.move(temp_path, final_path)
            
            cursor.execute(""" 
                INSERT INTO file_metadata 
                (file_name, display_name, file_path, file_hash, file_size, is_duplicate) 
                VALUES (%s, %s, %s, %s, %s, %s)
            """, (filename, filename, final_path, file_hash, file_size, False))
            
            db.commit()
            return jsonify({
                "status": "success",
                "message": "File uploaded successfully!"
            })

    except Exception as e:
        if os.path.exists(temp_path):
            os.remove(temp_path)
        return jsonify({"status": "error", "message": str(e)})
    finally:
        cursor.close()
        db.close()
@app.route('/files', methods=['GET'])
def get_files():
    db = connect_to_database()
    cursor = db.cursor(dictionary=True)
    
    try:
        cursor.execute("""
            SELECT 
                m1.id,
                m1.display_name as file_name,
                m1.file_size,
                m1.file_hash,
                m1.is_duplicate,
                m1.original_file_id,
                CASE 
                    WHEN m1.is_duplicate = 0 THEN (
                        SELECT COUNT(*) 
                        FROM file_metadata m2 
                        WHERE m2.file_hash = m1.file_hash AND m2.is_duplicate = 1
                    )
                    ELSE (
                        SELECT COUNT(*) 
                        FROM file_metadata m2 
                        WHERE m2.file_hash = m1.file_hash AND m2.id != m1.id
                    )
                END as duplicate_count
            FROM file_metadata m1
            ORDER BY m1.is_duplicate, m1.display_name
        """)
        files = cursor.fetchall()
        
        return jsonify({
            "status": "success",
            "files": files
        })
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})
    finally:
        cursor.close()
        db.close()
@app.route('/duplicates/<int:file_id>', methods=['GET'])
def get_duplicates(file_id):
    db = connect_to_database()
    cursor = db.cursor(dictionary=True)
    
    try:
        # First, get the file hash of the original file
        cursor.execute("SELECT file_hash FROM file_metadata WHERE id = %s", (file_id,))
        original = cursor.fetchone()
        
        if not original:
            return jsonify({"status": "error", "message": "Original file not found"})
            
        # Get all duplicates
        cursor.execute("""
            SELECT id, display_name, file_size
            FROM file_metadata 
            WHERE file_hash = %s AND is_duplicate = 1
        """, (original['file_hash'],))
        
        duplicates = cursor.fetchall()
        return jsonify({
            "status": "success",
            "duplicates": duplicates
        })
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})
    finally:
        cursor.close()
        db.close()
@app.route('/delete/<int:file_id>', methods=['DELETE'])
def delete_file(file_id):
    db = connect_to_database()
    cursor = db.cursor(dictionary=True)

    try:
        # Check if the file is original or duplicate
        cursor.execute("""
            SELECT file_path, is_duplicate, file_hash 
            FROM file_metadata 
            WHERE id = %s
        """, (file_id,))
        file_record = cursor.fetchone()

        if not file_record:
            return jsonify({"status": "error", "message": "File not found"})

        if file_record['is_duplicate']:
            # Delete single duplicate file
            cursor.execute("DELETE FROM file_metadata WHERE id = %s", (file_id,))
            if os.path.exists(file_record['file_path']):
                os.remove(file_record['file_path'])
        else:
            # For original file, handle different delete types
            delete_type = request.args.get('delete_type', 'original')
            
            if delete_type == 'all':
                # Delete original and all duplicates
                cursor.execute("""
                    SELECT file_path 
                    FROM file_metadata 
                    WHERE file_hash = %s
                """, (file_record['file_hash'],))
                all_files = cursor.fetchall()
                
                for file in all_files:
                    if os.path.exists(file['file_path']):
                        os.remove(file['file_path'])
                
                cursor.execute("DELETE FROM file_metadata WHERE file_hash = %s", 
                             (file_record['file_hash'],))
            
            elif delete_type == 'duplicates_only':
                # Delete only duplicate files, keep the original
                cursor.execute("""
                    SELECT file_path 
                    FROM file_metadata 
                    WHERE file_hash = %s AND is_duplicate = 1
                """, (file_record['file_hash'],))
                duplicate_files = cursor.fetchall()
                
                for file in duplicate_files:
                    if os.path.exists(file['file_path']):
                        os.remove(file['file_path'])
                
                cursor.execute("""
                    DELETE FROM file_metadata 
                    WHERE file_hash = %s AND is_duplicate = 1
                """, (file_record['file_hash'],))
            
            else:  # 'original'
                # Delete only original file
                if os.path.exists(file_record['file_path']):
                    os.remove(file_record['file_path'])
                cursor.execute("DELETE FROM file_metadata WHERE id = %s", (file_id,))

        db.commit()
        return jsonify({"status": "success", "message": "File(s) deleted successfully!"})

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})
    finally:
        cursor.close()
        db.close()      
if __name__ == '__main__':
    app.run(debug=True)