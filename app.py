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

DATABASE_URL = os.getenv('DATABASE_URL')

UPLOAD_FOLDER = 'static/images'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
os.makedirs(UPLOAD_FOLDER, exist_ok=True)


def get_db():
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

        if username == 'admin' and password == 'admin123':
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
        cur.execute(
            'INSERT INTO projects (title, description, image, link, tags) VALUES (%s, %s, %s, %s, %s)',
            (title, description, image, link, tags)
        )
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

        cur.execute(
            'UPDATE projects SET title=%s, description=%s, image=%s, link=%s, tags=%s WHERE id=%s',
            (title, description, image, link, tags, id)
        )
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
        cur.execute(
            'INSERT INTO education (school, degree, field, start_year, end_year, details) VALUES (%s, %s, %s, %s, %s, %s)',
            (school, degree, field, start_year, end_year, details)
        )
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

        cur.execute(
            'UPDATE education SET school=%s, degree=%s, field=%s, start_year=%s, end_year=%s, details=%s WHERE id=%s',
            (school, degree, field, start_year, end_year, details, id)
        )
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
