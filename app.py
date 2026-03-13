from flask import Flask, render_template, send_from_directory, request, redirect, url_for, session, flash
from werkzeug.utils import secure_filename
from flask_socketio import SocketIO, emit, join_room
import os

import sys
import os

if getattr(sys, 'frozen', False):
    # Running as compiled EXE
    base_dir = os.path.dirname(sys.executable)
    template_folder = os.path.join(sys._MEIPASS, 'templates')
    static_folder = os.path.join(sys._MEIPASS, 'static')
    app = Flask(__name__, template_folder=template_folder, static_folder=static_folder)
else:
    # Running from source
    base_dir = os.path.dirname(os.path.abspath(__file__))
    app = Flask(__name__)

socketio = SocketIO(app, cors_allowed_origins="*", async_mode='threading')



app.secret_key = 'your_secret_key_here' # Replace with a secure key in production
SHARING_ENABLED = True # Global state for file sharing
SHARING_ENABLED = True # Global state for file sharing
SHARED_TEXT_CONTENT = "" # Global state for shared text
BANNED_IPS = set() # Set of banned IP addresses
SHARED_FOLDER = os.path.join(base_dir, "shared")
os.makedirs(SHARED_FOLDER, exist_ok=True)
AVATAR_FOLDER = os.path.join(base_dir, "avatars")
os.makedirs(AVATAR_FOLDER, exist_ok=True)

# 🌐 Configuration
PORT = int(os.environ.get("PORT", 8000))

import mysql.connector
from mysql.connector import Error
from werkzeug.security import generate_password_hash, check_password_hash

import datetime

# 🗄️ Database Configuration
DB_HOST = os.environ.get("DB_HOST", "localhost")
DB_USER = os.environ.get("DB_USER", "root")
DB_PASSWORD = os.environ.get("DB_PASSWORD", "")
DB_NAME = os.environ.get("DB_NAME", "localsend_db")

def get_db_connection():
    try:
        connection = mysql.connector.connect(
            host=DB_HOST,
            user=DB_USER,
            password=DB_PASSWORD,
            database=DB_NAME
        )
        return connection
    except Error as e:
        print(f"Error connecting to MySQL: {e}")
        return None

def init_db():
    """Initialize the database and users table."""
    try:
        # Connect to MySQL server to create DB if not exists
        conn = mysql.connector.connect(
            host=DB_HOST,
            user=DB_USER,
            password=DB_PASSWORD
        )
        cursor = conn.cursor()
        cursor.execute(f"CREATE DATABASE IF NOT EXISTS {DB_NAME}")
        conn.close()

        # Connect to the specific database to create table
        conn = get_db_connection()
        if conn:
            cursor = conn.cursor()
            # Users Table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    username VARCHAR(50) NOT NULL UNIQUE,
                    email VARCHAR(100) NOT NULL UNIQUE,
                    password_hash VARCHAR(255) NOT NULL,
                    avatar VARCHAR(255)
                )
            """)
            
            # Activity Logs Table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS activity_logs (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    user_id INT,
                    username VARCHAR(50),
                    action VARCHAR(100),
                    details TEXT,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            conn.commit()
            conn.close()
            print("Database initialized successfully.")
    except Error as e:
        print(f"Database initialization failed: {e}")

# Initialize DB on startup
init_db()

# 🔍 Helper: Determine file type based on extension
def get_file_type(filename):
    ext = filename.lower().split('.')[-1]
    type_map = {
        'jpg': 'image', 'jpeg': 'image', 'png': 'image', 'gif': 'image', 'webp': 'image',
        'pdf': 'pdf',
        'mp4': 'video', 'webm': 'video', 'mkv': 'video',
        'mp3': 'audio', 'wav': 'audio', 'ogg': 'audio',
        'apk': 'app', 'exe': 'app', 'msi': 'app'
    }
    return type_map.get(ext, 'other')



def is_local_request():

    """Check if the request is from localhost."""
    return request.remote_addr in ['127.0.0.1', 'localhost']

# 🏠 Homepage Route (Landing Page)
@app.route("/")
def index():
    # Auto-login for network clients
    is_network_client = request.remote_addr != '127.0.0.1' and request.remote_addr != 'localhost'
    if is_network_client:
        session['username'] = 'Guest'
        return redirect(url_for('dashboard'))

    if 'username' in session:
        return redirect(url_for('dashboard'))
    return render_template("landing.html", server_url=get_server_url())

# 🔑 Sign In Route
@app.route("/signin", methods=['GET', 'POST'])
def signin():
    # Auto-login check (redundant but safe)
    is_network_client = request.remote_addr != '127.0.0.1' and request.remote_addr != 'localhost'
    if is_network_client:
        session['username'] = 'Guest'
        return redirect(url_for('dashboard'))

    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        conn = get_db_connection()
        if conn:
            cursor = conn.cursor(dictionary=True)
            cursor.execute("SELECT * FROM users WHERE username = %s", (username,))
            user = cursor.fetchone()
            conn.close()
            
            if user and check_password_hash(user['password_hash'], password):
                session['user_id'] = user['id']
                session['username'] = user['username']
                session['email'] = user['email']
                session['avatar'] = user['avatar']
                return redirect(url_for('dashboard'))
            else:
                flash('Invalid username or password')
        else:
            flash('Database connection error')
            
    return render_template("signin.html")

# 📝 Sign Up Route
@app.route("/signup", methods=['GET', 'POST'])
def signup():
     # Auto-login check
    is_network_client = request.remote_addr != '127.0.0.1' and request.remote_addr != 'localhost'
    if is_network_client:
        session['username'] = 'Guest'
        return redirect(url_for('dashboard'))

    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        
        conn = get_db_connection()
        if conn:
            cursor = conn.cursor()
            
            # Check if user exists
            cursor.execute("SELECT id FROM users WHERE username = %s OR email = %s", (username, email))
            if cursor.fetchone():
                flash('Username or Email already exists')
                conn.close()
                return redirect(url_for('signup'))
            
            hashed_password = generate_password_hash(password)
            try:
                cursor.execute("INSERT INTO users (username, email, password_hash) VALUES (%s, %s, %s)", 
                               (username, email, hashed_password))
                conn.commit()
                conn.close()
                flash('Account created successfully! Please sign in.')
                return redirect(url_for('signin'))
            except Error as e:
                flash(f"Error creating account: {e}")
                conn.close()
        else:
            flash('Database connection error')

    return render_template("signup.html")

# 🚪 Logout Route
@app.route("/logout")
def logout():
    session.clear()
    
    # If network client logs out, re-login as Guest immediately or show landing?
    is_network_client = request.remote_addr != '127.0.0.1' and request.remote_addr != 'localhost'
    
    if is_network_client:
        # Effectively they can't really "logout" to a login screen, they just refresh session
         return redirect(url_for('dashboard'))

    # If Host logs out, SHUTDOWN the server
    if is_local_request():
        print("Host logged out. Shutting down server...")
        
        def shutdown_server():
            import time
            time.sleep(1)
            print("Exiting...")
            os._exit(0)
            
        threading.Thread(target=shutdown_server).start()
        return "Server is shutting down. You can close this window."

    return redirect(url_for('index'))

# ⚙️ Update Profile Route
@app.route("/update_profile", methods=['POST'])
def update_profile():
    print("DEBUG: /update_profile called") # DEBUG
    if 'username' not in session:
        print("DEBUG: No username in session") # DEBUG
        return redirect(url_for('signin'))

    user_id = session.get('user_id')
    new_username = request.form.get('username')
    new_email = request.form.get('email')
    new_password = request.form.get('password')
    
    conn = get_db_connection()
    if conn and user_id:
        cursor = conn.cursor()
        
        if new_username:
            cursor.execute("UPDATE users SET username = %s WHERE id = %s", (new_username, user_id))
            session['username'] = new_username
            
        if new_email:
            cursor.execute("UPDATE users SET email = %s WHERE id = %s", (new_email, user_id))
            session['email'] = new_email
            
        if new_password:
            hashed_password = generate_password_hash(new_password)
            cursor.execute("UPDATE users SET password_hash = %s WHERE id = %s", (hashed_password, user_id))
            
        if 'avatar' in request.files:
            file = request.files['avatar']
            if file and file.filename != '':
                filename = secure_filename(f"avatar_{session['username']}_{file.filename}")
                save_path = os.path.join(AVATAR_FOLDER, filename)
                file.save(save_path)
                
                cursor.execute("UPDATE users SET avatar = %s WHERE id = %s", (filename, user_id))
                session['avatar'] = filename
        
        conn.commit()
        conn.close()

    return redirect(url_for('dashboard'))

# 📂 Dashboard Route (File Gallery)
@app.route("/dashboard")
def dashboard():
    # Auto-login for network clients
    is_network_client = request.remote_addr != '127.0.0.1' and request.remote_addr != 'localhost'
    
    if 'username' not in session:
        if is_network_client:
             session['username'] = 'Guest'
        else:
            return redirect(url_for('signin'))
    
    files = os.listdir(SHARED_FOLDER)
    files_data = []
    for f in files:
        if os.path.isfile(os.path.join(SHARED_FOLDER, f)):
            files_data.append({
                "name": f,
                "type": get_file_type(f),
                "extension": f.split('.')[-1].lower() if '.' in f else ''
            })

    
    server_url = get_server_url()

    is_network_client = not is_local_request()
    avatar_filename = session.get('avatar')
    avatar_url = url_for('get_avatar', filename=avatar_filename) if avatar_filename else None
    email = session.get('email', 'user@example.com')

    return render_template("dashboard.html", files=files_data, username=session['username'], server_url=server_url, local_ip=get_local_ip(), is_network_client=is_network_client, avatar_url=avatar_url, email=email, sharing_enabled=SHARING_ENABLED, shared_text=SHARED_TEXT_CONTENT)

# 🔍 Helper: Get Local IP
def get_local_ip():
    import socket
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        local_ip = s.getsockname()[0]
        s.close()
    except:
        local_ip = "127.0.0.1"
    return local_ip

# 🌍 Internet Sharing Removed
PUBLIC_URL = None

def get_server_url():
    """Returns the formatted server URL."""
    local_ip = get_local_ip()
    return f"http://{local_ip}:{PORT}"

# 👤 Get Avatar Route
@app.route("/avatars/<filename>")
def get_avatar(filename):
    if request.remote_addr in BANNED_IPS:
        return "Access Forbidden", 403
    return send_from_directory(AVATAR_FOLDER, filename)

# 🔄 Toggle Sharing API
@app.route("/api/toggle_share", methods=['POST'])
def toggle_share():
    global SHARING_ENABLED
    if not is_local_request():
        return {"error": "Unauthorized"}, 403
    
    SHARING_ENABLED = not SHARING_ENABLED
    print(f"DEBUG: Sharing Toggled -> {SHARING_ENABLED}")
    return {"sharing_enabled": SHARING_ENABLED}

# 🚫 Block User API
@app.route("/api/toggle_block", methods=['POST'])
def toggle_block():
    if not is_local_request():
        return {"error": "Unauthorized"}, 403
    
    data = request.get_json()
    target_ip = data.get('ip')
    
    if not target_ip:
         return {"error": "No IP provided"}, 400
         
    if target_ip in BANNED_IPS:
        BANNED_IPS.remove(target_ip)
        action = "unblocked"
    else:
        BANNED_IPS.add(target_ip)
        action = "blocked"
        
    print(f"DEBUG: User {target_ip} {action}")
    log_activity(session.get('username', 'Host'), f"User {action}", f"IP: {target_ip}")
    
    # Broadcast update to refresh lists (and kick user if needed)
    socketio.emit('update_users', get_connected_users_list(), broadcast=True)
    return {"status": "success", "action": action, "ip": target_ip}

# 📡 Peer Discovery System
import socket
import threading
import time
import json
import random

UDP_PORT = 8001
MY_ID = None # Will be set by frontend on load

class PeerDiscovery:
    def __init__(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        try:
            self.sock.bind(('0.0.0.0', UDP_PORT))
        except OSError as e:
            print(f" Warning: Peer Discovery Port {UDP_PORT} is busy. Discovery disabled.")
            self.running = False
            return
        self.running = True

    def listen(self):
        print(f" Discovery Listener Active on Port {UDP_PORT}")
        while self.running:
            try:
                data, addr = self.sock.recvfrom(1024)
                message = data.decode('utf-8')
                command, target_id = message.split(' ', 1)
                
                if command == "WHOIS" and target_id == MY_ID:
                    # It's for me! Reply with my URL
                    server_url = get_server_url()
                    response = f"HERE {MY_ID} {server_url}"
                    self.sock.sendto(response.encode('utf-8'), addr)
                    print(f" Responded to discovery from {addr}")
            except Exception as e:
                # print(f"Discovery Error: {e}")
                pass

    def search(self, target_id, timeout=2):
        print(f" Searching for {target_id}...")
        search_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        search_sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        search_sock.settimeout(timeout)
        
        try:
            msg = f"WHOIS {target_id}"
            search_sock.sendto(msg.encode('utf-8'), ('255.255.255.255', UDP_PORT))
            
            while True:
                try:
                    data, addr = search_sock.recvfrom(1024)
                    message = data.decode('utf-8')
                    parts = message.split(' ', 2)
                    if len(parts) == 3 and parts[0] == "HERE" and parts[1] == target_id:
                        return parts[2] # The URL
                except socket.timeout:
                    return None
        finally:
            search_sock.close()

# Start Listener in Background
discovery_service = PeerDiscovery()
threading.Thread(target=discovery_service.listen, daemon=True).start()

@app.route("/api/set_id", methods=['POST'])
def set_id():
    global MY_ID
    data = request.get_json()
    MY_ID = data.get('id')
    print(f" My Connection ID set to: {MY_ID}")
    return {"status": "ok"}

# 📡 WebRTC Remote Sharing Signaling
CONNECTED_USERS = {}

def log_activity(username, action, details="", user_id=None):
    """Log an activity to the database."""
    try:
        conn = get_db_connection()
        if conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO activity_logs (user_id, username, action, details, timestamp) VALUES (%s, %s, %s, %s, NOW())",
                (user_id, username, action, details)
            )
            conn.commit()
            conn.close()
            
            # Broadcast the new log to all clients
            socketio.emit('new_log', {
                'username': username,
                'action': action,
                'details': details,
                'timestamp': datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            })
    except Error as e:
        print(f"Failed to log activity: {e}")

@socketio.on('connect')
def handle_connect():
    username = session.get('username', 'Guest')
    user_id = session.get('user_id')
    print(f"User Connected: {username}")
    
    CONNECTED_USERS[request.sid] = {
        'username': username,
        'user_id': user_id,
        'avatar': session.get('avatar', 'default.png'),
        'ip': request.remote_addr
    }
    
    log_activity(username, "Joined", "User joined the network", user_id)
    log_activity(username, "Joined", "User joined the network", user_id)
    emit('update_users', get_connected_users_list(), broadcast=True)

@socketio.on('disconnect')
def handle_disconnect():
    user = CONNECTED_USERS.pop(request.sid, None)
    if user:
        print(f"User Disconnected: {user['username']}")
        log_activity(user['username'], "Left", "User left the network", user['user_id'])
        emit('update_users', get_connected_users_list(), broadcast=True)

@socketio.on('join')
def on_join(data):
    room = data['room']
    join_room(room)
    # Notify others in the room that a peer is ready
    emit('ready', {'msg': 'Peer joined'}, to=room, include_self=False)

@socketio.on('signal')
def handle_signal(data):
    # This relays Offer, Answer, or ICE Candidates to the other peer
    room = data['room']
    emit('signal', data, to=room, include_self=False)

# 📝 Text Sharing API
@app.route("/api/share_text", methods=['POST'])
def share_text():
    global SHARED_TEXT_CONTENT
    if not is_local_request():
        return {"error": "Unauthorized"}, 403
    
    data = request.get_json()
    SHARED_TEXT_CONTENT = data.get('text', '')
    
    username = session.get('username', 'Host')
    log_activity(username, "Shared Text", f"Updated shared text: {SHARED_TEXT_CONTENT[:20]}...")
    
    print(f"DEBUG: Shared Text Updated -> {SHARED_TEXT_CONTENT[:20]}...")
    return {"status": "success", "text": SHARED_TEXT_CONTENT}

@app.route("/api/get_text")
def get_text():
    if request.remote_addr in BANNED_IPS:
        return {"error": "Access Forbidden"}, 403
    if not is_local_request() and not SHARING_ENABLED:
        return {"error": "Sharing disabled"}, 403
    return {"text": SHARED_TEXT_CONTENT}

@app.route("/api/get_logs")
def get_logs():
    """Fetch recent logs involved with the network."""
    try:
        conn = get_db_connection()
        logs = []
        if conn:
            cursor = conn.cursor(dictionary=True)
            cursor.execute("SELECT * FROM activity_logs ORDER BY timestamp DESC LIMIT 50")
            logs = cursor.fetchall()
            conn.close()
            # Convert datetime to string
            for log in logs:
                if 'timestamp' in log and log['timestamp']:
                    log['timestamp'] = log['timestamp'].strftime("%Y-%m-%d %H:%M:%S")
        return {"logs": logs}
    except Error as e:
        return {"error": str(e)}, 500

@app.route("/api/connected_users")
def get_connected_users_api():
    """Return list of connected users."""
    """Return list of connected users."""
    return {"users": get_connected_users_list()}

def get_connected_users_list():
    users_list = []
    for sid, user in CONNECTED_USERS.items():
        user_copy = user.copy()
        user_copy['is_blocked'] = user['ip'] in BANNED_IPS
        # Hide IP from public, only show to host? 
        # For now, let's keep it simple. The host needs it to toggle.
        # But maybe we shouldn't send IP to everyone.
        # However, the toggle endpoint requires IP.
        # We can mask it for non-local if needed, but for local network tool it's fine.
        users_list.append(user_copy)
    return users_list

@app.route("/api/files")
def get_files():
    if request.remote_addr in BANNED_IPS:
        return {"error": "Access Forbidden"}, 403
        
    if not is_local_request() and not SHARING_ENABLED:
        return {"error": "Sharing disabled"}, 403
        
    files = os.listdir(SHARED_FOLDER)
    files_data = []
    for f in files:
        if os.path.isfile(os.path.join(SHARED_FOLDER, f)):
            files_data.append({
                "name": f,
                "type": get_file_type(f),
                "extension": f.split('.')[-1].lower() if '.' in f else ''
            })
    return {"files": files_data}

# 📤 Upload Route
@app.route("/upload", methods=['POST'])
def upload_file():
    if 'username' not in session:
        return redirect(url_for('signin'))
    
    if 'file' not in request.files:
        flash('No file part')
        return redirect(url_for('dashboard'))
        
    files = request.files.getlist('file')
    
    # Check if empty upload (one empty file)
    if len(files) == 1 and files[0].filename == '':
        flash('No selected file')
        return redirect(url_for('dashboard'))

    for file in files:
        if file and file.filename != '':
            filename = secure_filename(file.filename)
            file.save(os.path.join(SHARED_FOLDER, filename))
            
            username = session.get('username', 'Unknown')
            log_activity(username, "Uploaded File", f"Uploaded {filename}", session.get('user_id'))
            
    return redirect(url_for('dashboard'))

# 📤 API Upload Route (For Remote Peers)
@app.route("/api/upload", methods=['POST'])
def api_upload_file():
    if request.remote_addr in BANNED_IPS:
        return {"error": "Access Forbidden"}, 403
        
    if not is_local_request() and not SHARING_ENABLED:
        return {"error": "Sharing disabled"}, 403
        
    if 'file' not in request.files:
        return {"error": "No file part"}, 400
        
    files = request.files.getlist('file')
    saved_count = 0
    
    for file in files:
        if file and file.filename != '':
            filename = secure_filename(file.filename)
            file.save(os.path.join(SHARED_FOLDER, filename))
            saved_count += 1
            
            # Since this is API, we might not have session, but we can try
            username = "Remote Peer" # Ideally we'd pass username in headers/form
            # Try to resolve username from IP if possible, or just log IP
            # For now "Remote Peer" is okay, or we can look up in CONNECTED_USERS values if we had a way to map IP -> Username easily
            # But CONNECTED FILES use SID.
            # Let's just log "Remote Peer (IP)"
            log_activity(f"Peer ({request.remote_addr})", "Uploaded File", f"Uploaded {filename}")
            
    return {"status": "success", "count": saved_count}


# 🗑️ Delete Route
@app.route("/delete/<filename>", methods=['POST'])
def delete_file(filename):
    if not is_local_request():
        return "Unauthorized", 403
    
    file_path = os.path.join(SHARED_FOLDER, filename)
    if os.path.exists(file_path):
        os.remove(file_path)
        flash(f'Deleted {filename}')
        
        username = session.get('username', 'Host')
        log_activity(username, "Deleted File", f"Deleted {filename}")
    else:
        flash('File not found')
        
    return redirect(url_for('dashboard'))

# 👓 View Route (stream media file inline)
@app.route("/view/<filename>")
def view_file(filename):
    if request.remote_addr in BANNED_IPS:
        return "Access Forbidden", 403
        
    if not is_local_request() and not SHARING_ENABLED:
        return "Sharing is currently disabled by the host.", 403
        
    username = session.get('username', 'Peer') # improved username logic could go here
    log_activity(username, "Viewed File", f"Viewed {filename}", session.get('user_id') if is_local_request() else None)
    
    return send_from_directory(SHARED_FOLDER, filename)

# 📥 Download Route
@app.route("/download/<filename>")
def download_file(filename):
    if request.remote_addr in BANNED_IPS:
        return "Access Forbidden", 403

    if not is_local_request() and not SHARING_ENABLED:
        return "Sharing is currently disabled by the host.", 403
    
    username = session.get('username', 'Peer')
    if is_local_request():
         username = session.get('username', 'Host')
         
    # Only log downloads if significant? Maybe spammy. Let's log.
    # Only log downloads if significant? Maybe spammy. Let's log.
    log_activity(username, "Downloaded File", f"Downloaded {filename}", session.get('user_id') if is_local_request() else None)
    
    return send_from_directory(SHARED_FOLDER, filename, as_attachment=True)



# 📱 QR Code Route
@app.route("/qrcode")
def get_qrcode():
    import qrcode
    import io
    from flask import send_file
    
    url = get_server_url()
    
    # Generate QR Code
    img = qrcode.make(url)
    buf = io.BytesIO()
    img.save(buf)
    buf.seek(0)
    
    return send_file(buf, mimetype='image/png')

# 🌍 WAN / WebRTC Signaling removed (Moved to Client-Side MQTT)

# 🛠 Run the app

if __name__ == "__main__":
    local_ip = get_local_ip()
    server_url = get_server_url()
    
    print(f"\n\n{'='*40}")
    print(f" SERVER RUNNING!")
    print(f" - Local:   http://127.0.0.1:{PORT}")
    print(f" - Network: {server_url}")
    print(f" - Other Possible IPs:")
    
    import socket
    try:
        hostname = socket.gethostname()
        for ip in socket.gethostbyname_ex(hostname)[2]:
            print(f"   - http://{ip}:{PORT}")
    except:
        pass
        
    print(f"{'='*40}\n\n")

    import webbrowser
    from threading import Timer

    def open_browser():
        webbrowser.open_new(f"http://127.0.0.1:{PORT}")

    Timer(1, open_browser).start()
    
    # Use SocketIO for real-time communication
    print(f" STARTING SOCKETIO SERVER ON PORT {PORT}...")
    # Allow all origins for CORS to ensure mobile devices can connect
    socketio.run(app, host='0.0.0.0', port=PORT, debug=True, allow_unsafe_werkzeug=True)
