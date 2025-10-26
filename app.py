import os
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import sqlite3
import jwt
import datetime
from dotenv import load_dotenv
from chatbot import get_chatbot_response
from utils import init_db, query_db, execute_db

load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), '.env'))
SECRET = os.getenv('JWT_SECRET', 'replace-me')
DB_PATH = os.path.join(os.path.dirname(__file__), 'planpal.db')

app = Flask(__name__, static_folder='../frontend', static_url_path='/')
CORS(app)

init_db(DB_PATH)

def auth_required(f):
    from functools import wraps
    @wraps(f)
    def wrapper(*args, **kwargs):
        token = None
        if 'Authorization' in request.headers:
            parts = request.headers['Authorization'].split()
            if len(parts) == 2 and parts[0].lower() == 'bearer':
                token = parts[1]
        if not token:
            return jsonify({'error':'Missing token'}), 401
        try:
            payload = jwt.decode(token, SECRET, algorithms=['HS256'])
            request.user = payload.get('sub')
        except Exception as e:
            return jsonify({'error':'Invalid token', 'msg': str(e)}), 401
        return f(*args, **kwargs)
    return wrapper

@app.route('/')
def index():
    return send_from_directory(app.static_folder, 'index.html')

@app.route('/api/register', methods=['POST'])
def register():
    data = request.json or {}
    username = data.get('username')
    if not username:
        return jsonify({'error':'username required'}), 400
    execute_db(DB_PATH, "INSERT INTO users (username) VALUES (?)", (username,))
    user = query_db(DB_PATH, "SELECT * FROM users WHERE username=?", (username,), one=True)
    token = jwt.encode({'sub': user['id'], 'exp': datetime.datetime.utcnow() + datetime.timedelta(days=7)}, SECRET, algorithm='HS256')
    return jsonify({'token': token, 'user': {'id': user['id'], 'username': user['username']}})

@app.route('/api/groups', methods=['POST'])
@auth_required
def create_group():
    data = request.json or {}
    name = data.get('name') or 'New Group'
    execute_db(DB_PATH, "INSERT INTO groups (name, owner_id) VALUES (?,?)", (name, request.user))
    group = query_db(DB_PATH, "SELECT * FROM groups WHERE rowid = last_insert_rowid()", (), one=True)
    return jsonify({'group': group})

@app.route('/api/groups/<int:group_id>/polls', methods=['POST'])
@auth_required
def create_poll(group_id):
    data = request.json or {}
    title = data.get('title') or 'Poll'
    options = data.get('options') or []
    execute_db(DB_PATH, "INSERT INTO polls (group_id, title) VALUES (?,?)", (group_id, title))
    poll = query_db(DB_PATH, "SELECT rowid, * FROM polls WHERE rowid = last_insert_rowid()", (), one=True)
    for opt in options:
        execute_db(DB_PATH, "INSERT INTO poll_options (poll_id, option_text) VALUES (?,?)", (poll['rowid'], opt))
    return jsonify({'poll': poll})

@app.route('/api/polls/<int:poll_id>/vote', methods=['POST'])
@auth_required
def vote_poll(poll_id):
    data = request.json or {}
    option_id = data.get('option_id')
    execute_db(DB_PATH, "INSERT INTO votes (poll_id, option_id, user_id) VALUES (?,?,?)", (poll_id, option_id, request.user))
    return jsonify({'ok': True})

@app.route('/api/chat', methods=['POST'])
@auth_required
def chat():
    data = request.json or {}
    message = data.get('message','')
    mood = data.get('mood')
    resp = get_chatbot_response(message=message, mood=mood)
    return jsonify({'reply': resp})

@app.route('/api/ping')
def ping():
    return jsonify({'status':'ok'})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
