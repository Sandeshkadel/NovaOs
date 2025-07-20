import os
import json
from datetime import datetime
from werkzeug.utils import secure_filename

# Base directory for user files
BASE_DIR = "user_files"

def ensure_user_dir(username):
    """Create user directory if it doesn't exist"""
    user_dir = os.path.join(BASE_DIR, username)
    if not os.path.exists(user_dir):
        os.makedirs(user_dir)
    return user_dir

def save_file(username, filename, content):
    """Save file for user"""
    user_dir = ensure_user_dir(username)
    filename = secure_filename(filename)
    filepath = os.path.join(user_dir, filename)
    
    try:
        with open(filepath, 'w') as f:
            if filename.endswith('.json'):
                json.dump(content, f)
            else:
                f.write(content)
        return True
    except Exception as e:
        print(f"Error saving file: {e}")
        raise

def get_file(username, filename):
    """Get file content for user"""
    user_dir = ensure_user_dir(username)
    filename = secure_filename(filename)
    filepath = os.path.join(user_dir, filename)
    
    try:
        with open(filepath, 'r') as f:
            if filename.endswith('.json'):
                return json.load(f)
            else:
                return f.read()
    except FileNotFoundError:
        raise FileNotFoundError(f"File {filename} not found")
    except Exception as e:
        print(f"Error reading file: {e}")
        raise

def list_files(username):
    """List all files for user"""
    user_dir = ensure_user_dir(username)
    
    try:
        files = []
        for filename in os.listdir(user_dir):
            filepath = os.path.join(user_dir, filename)
            if os.path.isfile(filepath):
                stat = os.stat(filepath)
                files.append({
                    "name": filename,
                    "size": stat.st_size,
                    "modified": datetime.fromtimestamp(stat.st_mtime).isoformat()
                })
        return files
    except Exception as e:
        print(f"Error listing files: {e}")
        raise

def delete_file(username, filename):
    """Delete a user file"""
    user_dir = ensure_user_dir(username)
    filename = secure_filename(filename)
    filepath = os.path.join(user_dir, filename)
    
    try:
        if os.path.exists(filepath):
            os.remove(filepath)
            return True
        return False
    except Exception as e:
        print(f"Error deleting file: {e}")
        raise

def allowed_file(filename):
    """Check if file extension is allowed"""
    ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif', 'json', 'mp3'}
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS