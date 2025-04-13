import json
import hashlib
import sqlite3
import secrets
from urllib.parse import parse_qs
from http.server import BaseHTTPRequestHandler, HTTPServer

# Setup database
conn = sqlite3.connect('users.db')
cursor = conn.cursor()
cursor.execute('''
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE,
    email TEXT UNIQUE,
    password TEXT
)
''')
conn.commit()
conn.close()

# In-memory session store
sessions = {}  # token -> user_id

class SignupHandler(BaseHTTPRequestHandler):
    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'POST, GET, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type, Authorization')
        self.end_headers()

    def do_POST(self):
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length).decode('utf-8')
        data = parse_qs(post_data)
        path = self.path

        if path == '/signup':
            username = data.get('username', [''])[0]
            email = data.get('email', [''])[0]
            password = data.get('password', [''])[0]
            hashed_password = hashlib.sha256(password.encode()).hexdigest()

            try:
                conn = sqlite3.connect('users.db')
                cursor = conn.cursor()
                cursor.execute('INSERT INTO users (username, email, password) VALUES (?, ?, ?)',
                               (username, email, hashed_password))
                conn.commit()
                response = {'status': 'success', 'message': 'User registered successfully'}
            except sqlite3.IntegrityError:
                response = {'status': 'error', 'message': 'Username or email already exists'}
            finally:
                conn.close()

        elif path == '/login':
            email = data.get('email', [''])[0]
            password = data.get('password', [''])[0]
            hashed_password = hashlib.sha256(password.encode()).hexdigest()

            conn = sqlite3.connect('users.db')
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM users WHERE email = ? AND password = ?', (email, hashed_password))
            user = cursor.fetchone()
            conn.close()

            if user:
                # Generate session token
                token = secrets.token_hex(16)
                sessions[token] = user[0]  # user[0] = user_id
                response = {
                    'status': 'success',
                    'message': 'Login successful',
                    'token': token,
                    'user': {
                        'id': user[0],
                        'username': user[1],
                        'email': user[2]
                    }
                }
            else:
                response = {'status': 'error', 'message': 'Invalid email or password'}

        else:
            self.send_error(404)
            return

        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(json.dumps(response).encode('utf-8'))

    # Example of protected route
    def do_GET(self):
        if self.path == '/profile':
            # Get token from headers
            token = self.headers.get('Authorization')
            user_id = sessions.get(token)

            if user_id:
                conn = sqlite3.connect('users.db')
                cursor = conn.cursor()
                cursor.execute('SELECT id, username, email FROM users WHERE id = ?', (user_id,))
                user = cursor.fetchone()
                conn.close()

                response = {
                    'status': 'success',
                    'user': {
                        'id': user[0],
                        'username': user[1],
                        'email': user[2]
                    }
                }
            else:
                response = {'status': 'error', 'message': 'Unauthorized'}
                self.send_response(401)
        else:
            response = {'status': 'error', 'message': 'Not found'}
            self.send_response(404)

        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(json.dumps(response).encode('utf-8'))

def run(server_class=HTTPServer, handler_class=SignupHandler, port=8000):
    server_address = ('', port)
    httpd = server_class(server_address, handler_class)
    print(f"Running server on port {port}... \nYou can now open app on browser.")
    print(f"Geek Code Advanced")
    httpd.serve_forever()

if __name__ == '__main__':
    run()
