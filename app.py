from flask import Flask, render_template, request, flash, redirect, url_for, session, abort
from flask_socketio import SocketIO, join_room, leave_room, emit
import pymysql
import re
from dotenv import load_dotenv
from werkzeug.security import generate_password_hash, check_password_hash
from config import Config
from datetime import datetime
import logging
from functools import wraps
import os
import redis
import json

load_dotenv()
app = Flask(__name__)
app.config.from_object(Config)

# Redis for messages
r = redis.from_url(app.config['REDIS_URL'])

# Set session redis
app.config['SESSION_REDIS'] = r

socketio = SocketIO(app, cors_allowed_origins="*", async_mode=Config.SOCKETIO_ASYNC_MODE, manage_session=False)

# Logging
logging.basicConfig(level=logging.INFO if app.config['DEBUG'] else logging.WARNING)
logger = logging.getLogger(__name__)

# Pre-compile regex
EMAIL_REGEX = re.compile(r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$')

def get_db_connection():
    """Context manager for DB connections."""
    return pymysql.connect(
        host=app.config['DB_HOST'],
        port=int(app.config['DB_PORT']),
        user=app.config['DB_USER'],
        password=app.config['DB_PASSWORD'],
        database=app.config['DB_NAME'],
        charset='utf8mb4',
        cursorclass=pymysql.cursors.DictCursor,
        autocommit=True
    )

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('user_id'):
            flash('Please log in to access this page.', 'info')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

def validate_email(email):
    return email and EMAIL_REGEX.match(email)

def validate_password(password, confirm=None):
    if not password:
        return False, "Password is required."
    if len(password) < 8:
        return False, "Password must be at least 8 characters."
    if len(password) > 64:
        return False, "Password must not exceed 64 characters."
    if confirm and password != confirm:
        return False, "Passwords do not match."
    return True, None

@app.route('/')
def index():
    if session.get('user_id'):
        return redirect(url_for('chat'))
    return redirect(url_for('login'))

@app.route('/subscribe', methods=['GET', 'POST'])
def subscribe():
    if request.method == 'POST':
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '').strip()
        confirm_password = request.form.get('confirm_password', '').strip()

        if not validate_email(email):
            flash('Please provide a valid email address.', 'error')
            return render_template('subscribe.html')

        if not confirm_password:
            flash('Please confirm your password by filling both fields.', 'error')
            return render_template('subscribe.html')

        is_valid, error_msg = validate_password(password, confirm_password)
        if not is_valid:
            flash(error_msg, 'error')
            return render_template('subscribe.html')

        password_hash = generate_password_hash(password, method='pbkdf2:sha256')

        try:
            with get_db_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute(
                        "INSERT INTO subscribers (email, password_hash) VALUES (%s, %s)",
                        (email, password_hash)
                    )
            logger.info(f"New subscriber: {email}")
            flash('Subscription successful! Please log in.', 'success')
            return redirect(url_for('login'))
        except pymysql.err.IntegrityError:
            flash('Email already subscribed. Please log in.', 'info')
        except pymysql.err.OperationalError as db_error:
            logger.error(f"DB connection error: {db_error}")
            flash('Database connection failed. Check .env DB_USER/DB_PASSWORD.', 'error')
        except Exception as e:
            logger.error(f"Subscription error: {e}")
            flash('Subscription failed. Try again.', 'error')

    return render_template('subscribe.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '').strip()

        if not validate_email(email):
            flash('Invalid email.', 'error')
            return render_template('login.html')

        is_valid, _ = validate_password(password)
        if not is_valid:
            flash('Invalid password.', 'error')
            return render_template('login.html')

        try:
            with get_db_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute(
                        "SELECT id, email, password_hash FROM subscribers WHERE email = %s",
                        (email,)
                    )
                    user = cursor.fetchone()

                    if user and check_password_hash(user['password_hash'], password):
                        session['user_id'] = user['id']
                        session['user_email'] = user['email']
                        # Mark online
                        cursor.execute(
                            "UPDATE subscribers SET online_status = 'online' WHERE id = %s",
                            (user['id'],)
                        )
                        logger.info(f"User logged in: {email}")
                        flash('Login successful! Welcome to chat.', 'success')
                        return redirect(url_for('chat'))
                    else:
                        flash('Invalid credentials.', 'error')
        except pymysql.err.OperationalError as db_error:
            logger.error(f"DB connection error: {db_error}")
            flash('Database connection failed. Check .env DB_USER/DB_PASSWORD.', 'error')
        except Exception as e:
            logger.error(f"Login error: {e}")
            flash('Login failed.', 'error')

    return render_template('login.html')

@app.route('/chat')
@login_required
def chat():
    # Get current user info
    try:
        with get_db_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute(
                    "SELECT id, email FROM subscribers WHERE id = %s",
                    (session['user_id'],)
                )
                user = cursor.fetchone()
    except:
        user = {'id': session['user_id'], 'email': session['user_email']}
    
    # Load recent messages from Redis (last 100)
    messages = r.lrange('chat_messages', -100, -1)
    messages = [json.loads(msg) for msg in messages[::-1]]  # Reverse to newest first
    return render_template('chat.html', user=user, messages=messages)

@app.route('/logout')
def logout():
    user_id = session.get('user_id')
    if user_id:
        r.srem('online_users', str(user_id))
        try:
            with get_db_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute(
                        "UPDATE subscribers SET online_status = 'offline' WHERE id = %s",
                        (user_id,)
                    )
            logger.info(f"User logged out: {session.get('user_email', 'Unknown')}")
        except:
            pass
        session.clear()
    socketio.emit('user_status_change', {}, room='chat')  # Broadcast logout
    flash('Logged out successfully.', 'success')
    return redirect(url_for('login'))

# SocketIO Events
@socketio.on('connect')
def handle_connect(auth):
    emit('status', {'msg': 'Socket connected!'})
    if not session.get('user_id'):
        emit('error', {'msg': 'Auth required for chat'})
        return False
    user_id = session['user_id']
    join_room('chat')
    join_room(str(user_id))
    # Redis online set
    r.sadd('online_users', str(user_id))
    # Update DB too
    try:
        with get_db_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute("UPDATE subscribers SET online_status = 'online' WHERE id = %s", (user_id,))
    except Exception as e:
        logger.error(f"DB update error: {e}")
    logger.info(f"User {user_id} connected")
    emit('user_status_change', {}, room='chat')

@socketio.on('send_message')
def handle_message(data):
    if not session.get('user_id'):
        return
    user_id = session['user_id']
    email = session.get('user_email', 'Unknown')
    message = data.get('message', '').strip()
    if message:
        from flask import current_app
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")  # Date + time
        msg_data = {
            'user': email.split('@')[0],
            'message': message,
            'timestamp': timestamp,
            'user_id': user_id
        }
        # Store in Redis
        r.lpush('chat_messages', json.dumps(msg_data))
        r.ltrim('chat_messages', 0, 999)  # Keep last 1000
        
        emit('new_message', msg_data, room='chat')
        emit('user_status_change', {}) # Trigger list refresh

@socketio.on('get_online')
def handle_get_online():
    try:
        # Redis online set (updated on connect/disconnect)
        with get_db_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute("SELECT id, email FROM subscribers WHERE online_status = 'online'")
                online_users = cursor.fetchall()
        data = {'users': [{'id': u['id'], 'name': u['email'].split('@')[0]} for u in online_users]}
        emit('online_list', data)
        logger.info(f"Redis online list sent: {len(data['users'])} users")
    except Exception as e:
        logger.error(f"Redis online error: {e}")
        emit('error', {'msg': 'Failed to fetch online users'})

@socketio.on('disconnect')
def handle_disconnect():
    if session.get('user_id'):
        user_id = session['user_id']
        r.srem('online_users', str(user_id))
        try:
            with get_db_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("UPDATE subscribers SET online_status = 'offline' WHERE id = %s", (user_id,))
            conn.commit()
        except:
            pass
        emit('user_status_change', {}, room='chat')

if __name__ == '__main__':
    socketio.run(app, debug=app.config['DEBUG'], host='0.0.0.0', port=5000)

