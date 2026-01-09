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
DATABASE_URL = "postgresql://neondb_owner:npg_0WjrBKgt5ZhF@ep-small-smoke-a4d61e4r-pooler.us-east-1.aws.neon.tech/neondb?sslmode=require&channel_binding=require"

def get_db():
    conn = psycopg2.connect(DATABASE_URL, sslmode='require')
    return conn

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
def init_database():
    conn = psycopg2.connect(DATABASE_URL, sslmode='require')
    cur = conn.cursor()

    # --- CREATE TABLES ---
    cur.execute('''
        CREATE TABLE IF NOT EXISTS projects (
            id SERIAL PRIMARY KEY,
            title TEXT NOT NULL,
            description TEXT NOT NULL,
            image TEXT,
            link TEXT,
            tags TEXT
        )
    ''')

    cur.execute('''
        CREATE TABLE IF NOT EXISTS education (
            id SERIAL PRIMARY KEY,
            school TEXT NOT NULL,
            degree TEXT NOT NULL,
            field TEXT,
            start_year INTEGER NOT NULL,
            end_year INTEGER,
            details TEXT
        )
    ''')

    cur.execute('''
        CREATE TABLE IF NOT EXISTS certifications (
            id SERIAL PRIMARY KEY,
            title TEXT NOT NULL,
            issuer TEXT NOT NULL,
            year INTEGER NOT NULL,
            credential_url TEXT,
            description TEXT
        )
    ''')

    cur.execute('''
        CREATE TABLE IF NOT EXISTS messages (
            id SERIAL PRIMARY KEY,
            name TEXT NOT NULL,
            email TEXT NOT NULL,
            message TEXT NOT NULL,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    # --- INSERT SAMPLE DATA ONLY IF EMPTY ---

    # Projects
    cur.execute('SELECT COUNT(*) FROM projects')
    if cur.fetchone()[0] == 0:
        projects = [
            ('E-Commerce Platform',
             'A full-stack e-commerce platform with payment integration, user authentication, and admin dashboard. Built with modern technologies and responsive design.',
             'https://images.pexels.com/photos/3183150/pexels-photo-3183150.jpeg?auto=compress&cs=tinysrgb&w=800',
             'https://github.com',
             'Python, Flask, PostgreSQL, Bootstrap'),

            ('Task Management App',
             'A collaborative task management application with real-time updates, team collaboration features, and project tracking capabilities.',
             'https://images.pexels.com/photos/3184291/pexels-photo-3184291.jpeg?auto=compress&cs=tinysrgb&w=800',
             'https://github.com',
             'React, Node.js, MongoDB, Socket.io'),

            ('Weather Dashboard',
             'A beautiful weather dashboard that displays current weather, forecasts, and historical data with interactive charts and maps.',
             'https://images.pexels.com/photos/1118873/pexels-photo-1118873.jpeg?auto=compress&cs=tinysrgb&w=800',
             'https://github.com',
             'JavaScript, API Integration, Chart.js'),

            ('Portfolio CMS',
             'A content management system specifically designed for portfolios, allowing easy updates and customization without coding knowledge.',
             'https://images.pexels.com/photos/196644/pexels-photo-196644.jpeg?auto=compress&cs=tinysrgb&w=800',
             'https://github.com',
             'Django, SQLite, Bootstrap, REST API')
        ]
        for p in projects:
            cur.execute(
                'INSERT INTO projects (title, description, image, link, tags) VALUES (%s, %s, %s, %s, %s)',
                p
            )

    # Education
    cur.execute('SELECT COUNT(*) FROM education')
    if cur.fetchone()[0] == 0:
        education = [
            ("Ecole Supérieure Polytechnique d'Antananarivo",
             'Master of Engineering',
             'Petroleum Engineering',
             2019,
             2021,
             'Specialized in Machine Learning and AI. Completed thesis on Deep Learning applications in Computer Vision.'),

            ]
        for e in education:
            cur.execute(
                'INSERT INTO education (school, degree, field, start_year, end_year, details) VALUES (%s, %s, %s, %s, %s, %s)',
                e
            )

    # Certifications
    cur.execute('SELECT COUNT(*) FROM certifications')
    if cur.fetchone()[0] == 0:
        certifications = [
            ('AWS Certified Solutions Architect',
             'Amazon Web Services',
             2023,
             'https://aws.amazon.com',
             'Professional level certification demonstrating expertise in designing distributed systems on AWS.'),

            ('Google Cloud Professional Developer',
             'Google Cloud',
             2022,
             'https://cloud.google.com',
             'Validates ability to build scalable and reliable cloud-native applications using Google Cloud technologies.'),

            ('Certified Kubernetes Administrator',
             'Cloud Native Computing Foundation',
             2023,
             'https://cncf.io',
             'Demonstrates skills in container orchestration, deployment, and management of Kubernetes clusters.'),

            ('Python Programming Certificate',
             'Python Institute',
             2021,
             'https://pythoninstitute.org',
             'Advanced certification covering object-oriented programming, data structures, and Python best practices.')
        ]
        for c in certifications:
            cur.execute(
                'INSERT INTO certifications (title, issuer, year, credential_url, description) VALUES (%s, %s, %s, %s, %s)',
                c
            )

    conn.commit()
    cur.close()
    conn.close()
    print('Database initialized successfully (without duplicates)!')

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
        if username == 'Michel' and password == '$Nomenyaro01':
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

# --- PROJECTS CRUD ---
@app.route('/admin/projects')
@login_required
def admin_projects():
    conn = get_db() 
    cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) 
    cur.execute('SELECT * FROM projects ORDER BY id DESC') 
    projects = cur.fetchall() 
    cur.close() 
    conn.close() 
    
    return render_template('admin/projects.html', projects=projects)
    
@app.route('/admin/projects/add', methods=['GET', 'POST']) 
@login_required 
def admin_add_project(): 
    if request.method == 'POST': 
        title = request.form.get('title') 
        description = request.form.get('description') 
        image = request.form.get('image') 
        link = request.form.get('link') 
        tags = request.form.get('tags') 
        conn = get_db() 
        cur = conn.cursor() 
        cur.execute( 'INSERT INTO projects (title, description, image, link, tags) VALUES (%s, %s, %s, %s, %s)', (title, description, image, link, tags) ) 
        conn.commit() 
        cur.close() 
        conn.close() 
        
        flash('Project added successfully!', 'success') 
        
        return redirect(url_for('admin_projects')) 
    return render_template('admin/project_form.html', project=None)

@app.route('/admin/projects/edit/<int:id>', methods=['GET', 'POST']) 
@login_required 
def admin_edit_project(id): 
    conn = get_db() 
    cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) 
    cur.execute('SELECT * FROM projects WHERE id=%s', (id,)) 
    project = cur.fetchone() 
    if request.method == 'POST': 
        title = request.form.get('title') 
        description = request.form.get('description') 
        image = request.form.get('image') 
        link = request.form.get('link') 
        tags = request.form.get('tags') 
        cur.execute( 'UPDATE projects SET title=%s, description=%s, image=%s, link=%s, tags=%s WHERE id=%s', (title, description, image, link, tags, id) ) 
        conn.commit() 
        cur.close() 
        conn.close() 
        
        flash('Project updated successfully!', 'success') 
        return redirect(url_for('admin_projects')) 
    
    cur.close() 
    conn.close() 
    
    return render_template('admin/project_form.html', project=project) 

@app.route('/admin/projects/delete/<int:id>') 
@login_required 
def admin_delete_project(id): 
    conn = get_db() 
    cur = conn.cursor() 
    cur.execute('DELETE FROM projects WHERE id=%s', (id,)) 
    conn.commit() 
    cur.close() 
    conn.close() 
    
    flash('Project deleted successfully!', 'success') 
    return redirect(url_for('admin_projects')) 

# --- EDUCATION CRUD --- 
@app.route('/admin/education') 
@login_required 
def admin_education(): 
    conn = get_db() 
    cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) 
    cur.execute('SELECT * FROM education ORDER BY start_year DESC') 
    education = cur.fetchall() 
    cur.close() 
    conn.close() 
    return render_template('admin/education.html', education=education) 

@app.route('/admin/education/add', methods=['GET', 'POST']) 
@login_required 
def admin_add_education(): 
    if request.method == 'POST': 
        school = request.form.get('school') 
        degree = request.form.get('degree') 
        field = request.form.get('field') 
        start_year = request.form.get('start_year') 
        end_year = request.form.get('end_year') 
        details = request.form.get('details') 
        conn = get_db() 
        cur = conn.cursor() 
        cur.execute( 'INSERT INTO education (school, degree, field, start_year, end_year, details) VALUES (%s, %s, %s, %s, %s, %s)', (school, degree, field, start_year, end_year, details) ) 
        conn.commit() 
        cur.close() 
        conn.close() 
        flash('Education record added successfully!', 'success') 
        return redirect(url_for('admin_education')) 
    
    return render_template('admin/education_form.html', education=None) 

@app.route('/admin/education/edit/<int:id>', methods=['GET', 'POST']) 
@login_required 
def admin_edit_education(id): 
    conn = get_db() 
    cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) 
    cur.execute('SELECT * FROM education WHERE id=%s', (id,)) 
    education = cur.fetchone() 
    if request.method == 'POST': 
        school = request.form.get('school') 
        degree = request.form.get('degree') 
        field = request.form.get('field') 
        start_year = request.form.get('start_year')
        end_year = request.form.get('end_year') 
        details = request.form.get('details') 
        cur.execute( 'UPDATE education SET school=%s, degree=%s, field=%s, start_year=%s, end_year=%s, details=%s WHERE id=%s', (school, degree, field, start_year, end_year, details, id) ) 
        conn.commit() 
        cur.close() 
        conn.close() 
        flash('Education record updated successfully!', 'success') 
        return redirect(url_for('admin_education')) 
    cur.close() 
    conn.close() 
    return render_template('admin/education_form.html', education=education) 

@app.route('/admin/education/delete/<int:id>') 
@login_required 
def admin_delete_education(id): 
    conn = get_db() 
    cur = conn.cursor() 
    cur.execute('DELETE FROM education WHERE id=%s', (id,)) 
    conn.commit() 
    cur.close() 
    conn.close() 
    flash('Education record deleted successfully!', 'success') 
    return redirect(url_for('admin_education')) 

# --- CERTIFICATIONS CRUD --- 
@app.route('/admin/certifications') 
@login_required 
def admin_certifications(): 
    conn = get_db() 
    cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) 
    cur.execute('SELECT * FROM certifications ORDER BY year DESC') 
    certs = cur.fetchall()
    cur.close()
    conn.close()
    return render_template('admin/certifications.html', certifications=certs)

@app.route('/admin/certifications/add', methods=['GET', 'POST'])
@login_required
def admin_add_certification():
    if request.method == 'POST':
        title = request.form.get('title')
        issuer = request.form.get('issuer')
        year = request.form.get('year')
        credential_url = request.form.get('credential_url')
        description = request.form.get('description')
        conn = get_db()
        cur = conn.cursor()
        cur.execute(
            'INSERT INTO certifications (title, issuer, year, credential_url, description) VALUES (%s, %s, %s, %s, %s)',
            (title, issuer, year, credential_url, description)
        )
        conn.commit()
        cur.close()
        conn.close()
        flash('Certification added successfully!', 'success')
        return redirect(url_for('admin_certifications'))
    return render_template('admin/certification_form.html', certification=None)

@app.route('/admin/certifications/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def admin_edit_certification(id):
    conn = get_db()
    cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    cur.execute('SELECT * FROM certifications WHERE id=%s', (id,))
    certification = cur.fetchone()
    if request.method == 'POST':
        title = request.form.get('title')
        issuer = request.form.get('issuer')
        year = request.form.get('year')
        credential_url = request.form.get('credential_url')
        description = request.form.get('description')
        cur.execute(
            'UPDATE certifications SET title=%s, issuer=%s, year=%s, credential_url=%s, description=%s WHERE id=%s',
            (title, issuer, year, credential_url, description, id)
        )
        conn.commit()
        cur.close()
        conn.close()
        flash('Certification updated successfully!', 'success')
        return redirect(url_for('admin_certifications'))
    cur.close()
    conn.close()
    return render_template('admin/certification_form.html', certification=certification)

@app.route('/admin/certifications/delete/<int:id>')
@login_required
def admin_delete_certification(id):
    conn = get_db()
    cur = conn.cursor()
    cur.execute('DELETE FROM certifications WHERE id=%s', (id,))
    conn.commit()
    cur.close()
    conn.close()
    flash('Certification deleted successfully!', 'success')
    return redirect(url_for('admin_certifications'))

# --- MESSAGES ---
@app.route('/admin/messages')
@login_required
def admin_messages():
    conn = get_db()
    cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    cur.execute('SELECT * FROM messages ORDER BY timestamp DESC')
    messages = cur.fetchall()
    cur.close()
    conn.close()
    return render_template('admin/messages.html', messages=messages)


if __name__ == '__main__':
    app.run(debug=True)
