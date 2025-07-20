from flask import Flask, request, jsonify, session
from flask_cors import CORS
import os
from datetime import timedelta
from ai_assistant import ask_gemini
from file_manager import save_file, get_file, list_files, delete_file

app = Flask(__name__)
app.secret_key = os.urandom(24)
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(days=7)
CORS(app, supports_credentials=True)

# Mock user database
users = {
    "admin": {"password": "admin123", "theme": "dark", "wallpaper": "default"},
    "guest": {"password": "guest123", "theme": "light", "wallpaper": "default"}
}

@app.route('/api/login', methods=['POST'])
def login():
    data = request.json
    username = data.get('username')
    password = data.get('password')
    
    if username in users and users[username]['password'] == password:
        session['username'] = username
        session.permanent = True
        return jsonify({
            "success": True,
            "username": username,
            "theme": users[username]['theme'],
            "wallpaper": users[username]['wallpaper']
        })
    return jsonify({"success": False, "message": "Invalid credentials"}), 401

@app.route('/api/logout', methods=['POST'])
def logout():
    session.pop('username', None)
    return jsonify({"success": True})

@app.route('/api/check_auth', methods=['GET'])
def check_auth():
    if 'username' in session:
        username = session['username']
        return jsonify({
            "authenticated": True,
            "username": username,
            "theme": users[username]['theme'],
            "wallpaper": users[username]['wallpaper']
        })
    return jsonify({"authenticated": False})

@app.route('/api/ask', methods=['POST'])
def ask():
    if 'username' not in session:
        return jsonify({"error": "Unauthorized"}), 401
        
    data = request.json
    prompt = data.get('prompt')
    
    if not prompt:
        return jsonify({"error": "Prompt is required"}), 400
        
    try:
        response = ask_gemini(prompt)
        return jsonify({"response": response})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/files', methods=['GET', 'POST'])
def files():
    if 'username' not in session:
        return jsonify({"error": "Unauthorized"}), 401
        
    username = session['username']
    
    if request.method == 'POST':
        # Save file
        data = request.json
        filename = data.get('filename')
        content = data.get('content')
        
        if not filename or not content:
            return jsonify({"error": "Filename and content are required"}), 400
            
        try:
            save_file(username, filename, content)
            return jsonify({"success": True})
        except Exception as e:
            return jsonify({"error": str(e)}), 500
            
    else:
        # List files
        try:
            files = list_files(username)
            return jsonify({"files": files})
        except Exception as e:
            return jsonify({"error": str(e)}), 500

@app.route('/api/files/<path:filename>', methods=['GET', 'DELETE'])
def file_operations(filename):
    if 'username' not in session:
        return jsonify({"error": "Unauthorized"}), 401
        
    username = session['username']
    
    if request.method == 'GET':
        try:
            content = get_file(username, filename)
            return jsonify({"content": content})
        except FileNotFoundError:
            return jsonify({"error": "File not found"}), 404
        except Exception as e:
            return jsonify({"error": str(e)}), 500
            
    elif request.method == 'DELETE':
        try:
            delete_file(username, filename)
            return jsonify({"success": True})
        except FileNotFoundError:
            return jsonify({"error": "File not found"}), 404
        except Exception as e:
            return jsonify({"error": str(e)}), 500

@app.route('/api/settings', methods=['GET', 'POST'])
def settings():
    if 'username' not in session:
        return jsonify({"error": "Unauthorized"}), 401
        
    username = session['username']
    
    if request.method == 'POST':
        data = request.json
        theme = data.get('theme')
        wallpaper = data.get('wallpaper')
        
        if theme and theme in ['light', 'dark', 'aurora', 'glass', 'neon']:
            users[username]['theme'] = theme
            return jsonify({"success": True, "theme": theme})
        elif wallpaper:
            users[username]['wallpaper'] = wallpaper
            return jsonify({"success": True, "wallpaper": wallpaper})
        return jsonify({"error": "Invalid settings"}), 400
        
    else:
        return jsonify({
            "theme": users[username]['theme'],
            "wallpaper": users[username]['wallpaper'],
            "username": username
        })

@app.route('/api/wallpapers', methods=['GET'])
def get_wallpapers():
    return jsonify({
        "wallpapers": [
            {"id": "default", "name": "Default", "url": "https://source.unsplash.com/random/1920x1080/?nature,night"},
            {"id": "mountains", "name": "Mountains", "url": "https://source.unsplash.com/random/1920x1080/?mountains"},
            {"id": "beach", "name": "Beach", "url": "https://source.unsplash.com/random/1920x1080/?beach"},
            {"id": "city", "name": "City", "url": "https://source.unsplash.com/random/1920x1080/?city,night"},
            {"id": "space", "name": "Space", "url": "https://source.unsplash.com/random/1920x1080/?space"}
        ]
    })

if __name__ == '__main__':
    app.run(debug=True, port=5000)