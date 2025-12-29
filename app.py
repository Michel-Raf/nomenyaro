from flask import Flask, render_template, request, redirect, url_for, session, flash
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
import psycopg2
import psycopg2.extras
from datetime import datetime
import os
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = 'your-secret-key-change-in-production'

# --- DATABASE CONFIG ---
DATABASE_URL = os.getenv('DATABASE_URL')

# --- UPLOAD CONFIG ---
UPLOAD_FOLDER = 'static/image'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# --- HELPER FUNCTIONS ---
def get_db():
    """Return a new database connection."""
    conn = psycopg2.connect(DATABASE_URL, sslmode='require')
    return conn

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'admin_logged_in' not in session:
            return redirect(url_for('admin_login'))
        return f(*args, **kwargs)
    return decorated_function

# --- DATABASE INITIALIZATION ---
def init_db():
    """Create tables if they don't exist."""
    conn = get_db()
    cur = conn.cursor()
    cur.execute("""
    CREATE TABLE IF NOT EXISTS projects (
        id SERIAL PRIMARY KEY,
        title TEXT NOT NULL,
        description TEXT,
        image TEXT,
        link TEXT,
        tags TEXT
    );
    """)
    cur.execute("""
    CREATE TABLE IF NOT EXISTS education (
        id SERIAL PRIMARY KEY,
        school TEXT NOT NULL,
        degree TEXT,
        field TEXT,
        start_year INTEGER,
        end_year INTEGER,
        details TEXT
    );
    """)
    cur.execute("""
    CREATE TABLE IF NOT EXISTS certifications (
        id SERIAL PRIMARY KEY,
        title TEXT NOT NULL,
        issuer TEXT,
        year INTEGER,
        credential_url TEXT,
        description TEXT
    );
    """)
    cur.execute("""
    CREATE TABLE IF NOT EXISTS messages (
        id SERIAL PRIMARY KEY,
        name TEXT,
        email TEXT,
        message TEXT,
        timestamp TIMESTAMP
    );
    """)
    conn.commit()
    cur.close()
    conn.close()

# Initialize DB on app start
init_db()

# --- PUBLIC ROUTES ---
@app.route('/')
def home():
    return render_template('home.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/projects')
def projects():
    conn = get_db()
    cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    cur.execute('SELECT * FROM projects ORDER BY id DESC')
    projects = cur.fetchall()
    cur.close()
    conn.close()
    return render_template('projects.html', projects=projects)

@app.route('/education')
def education():
    conn = get_db()
    cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    cur.execute('SELECT * FROM education ORDER BY start_year DESC')
    education = cur.fetchall()
    cur.close()
    conn.close()
    return render_template('education.html', education=education)

@app.route('/certifications')
def certifications():
    conn = get_db()
    cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    cur.execute('SELECT * FROM certifications ORDER BY year DESC')
    certs = cur.fetchall()
    cur.close()
    conn.close()
    return render_template('certifications.html', certifications=certs)

@app.route('/contact', methods=['GET', 'POST'])
def contact():
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        message = request.form.get('message')
        conn = get_db()
        cur = conn.cursor()
        cur.execute(
            'INSERT INTO messages (name, email, message, timestamp) VALUES (%s, %s, %s, %s)',
            (name, email, message, datetime.now())
        )
        conn.commit()
        cur.close()
        conn.close()
        flash('Thank you for your message! I will get back to you soon.', 'success')
        return redirect(url_for('contact'))
    return render_template('contact.html')

# --- ADMIN LOGIN/LOGOUT ---
@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        if username == 'Michel-Raf' and password == '$Nomenyaro01':
            session['admin_logged_in'] = True
            flash('Successfully logged in!', 'success')
            return redirect(url_for('admin_dashboard'))
        else:
            flash('Invalid credentials!', 'danger')
    return render_template('admin/login.html')

@app.route('/admin/logout')
def admin_logout():
    session.pop('admin_logged_in', None)
    flash('Successfully logged out!', 'success')
    return redirect(url_for('home'))

# --- ADMIN DASHBOARD ---
@app.route('/admin')
@login_required
def admin_dashboard():
    conn = get_db()
    cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    cur.execute('SELECT COUNT(*) AS count FROM projects')
    projects_count = cur.fetchone()['count']
    cur.execute('SELECT COUNT(*) AS count FROM education')
    education_count = cur.fetchone()['count']
    cur.execute('SELECT COUNT(*) AS count FROM certifications')
    certs_count = cur.fetchone()['count']
    cur.execute('SELECT COUNT(*) AS count FROM messages')
    messages_count = cur.fetchone()['count']
    cur.close()
    conn.close()
    return render_template(
        'admin/dashboard.html',
        projects_count=projects_count,
        education_count=education_count,
        certs_count=certs_count,
        messages_count=messages_count
    )

# --- All CRUD routes remain unchanged ---

if __name__ == '__main__':
    app.run(debug=True)
