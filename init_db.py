import sqlite3

def init_database():
    conn = sqlite3.connect('portfolio.db')
    cursor = conn.cursor()

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS projects (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            description TEXT NOT NULL,
            image TEXT,
            link TEXT,
            tags TEXT
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS education (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            school TEXT NOT NULL,
            degree TEXT NOT NULL,
            field TEXT,
            start_year INTEGER NOT NULL,
            end_year INTEGER,
            details TEXT
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS certifications (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            issuer TEXT NOT NULL,
            year INTEGER NOT NULL,
            credential_url TEXT,
            description TEXT
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT NOT NULL,
            message TEXT NOT NULL,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    cursor.execute('INSERT INTO projects (title, description, image, link, tags) VALUES (?, ?, ?, ?, ?)',
                  ('E-Commerce Platform',
                   'A full-stack e-commerce platform with payment integration, user authentication, and admin dashboard. Built with modern technologies and responsive design.',
                   'https://images.pexels.com/photos/3183150/pexels-photo-3183150.jpeg?auto=compress&cs=tinysrgb&w=800',
                   'https://github.com',
                   'Python, Flask, PostgreSQL, Bootstrap'))

    cursor.execute('INSERT INTO projects (title, description, image, link, tags) VALUES (?, ?, ?, ?, ?)',
                  ('Task Management App',
                   'A collaborative task management application with real-time updates, team collaboration features, and project tracking capabilities.',
                   'https://images.pexels.com/photos/3184291/pexels-photo-3184291.jpeg?auto=compress&cs=tinysrgb&w=800',
                   'https://github.com',
                   'React, Node.js, MongoDB, Socket.io'))

    cursor.execute('INSERT INTO projects (title, description, image, link, tags) VALUES (?, ?, ?, ?, ?)',
                  ('Weather Dashboard',
                   'A beautiful weather dashboard that displays current weather, forecasts, and historical data with interactive charts and maps.',
                   'https://images.pexels.com/photos/1118873/pexels-photo-1118873.jpeg?auto=compress&cs=tinysrgb&w=800',
                   'https://github.com',
                   'JavaScript, API Integration, Chart.js'))

    cursor.execute('INSERT INTO projects (title, description, image, link, tags) VALUES (?, ?, ?, ?, ?)',
                  ('Portfolio CMS',
                   'A content management system specifically designed for portfolios, allowing easy updates and customization without coding knowledge.',
                   'https://images.pexels.com/photos/196644/pexels-photo-196644.jpeg?auto=compress&cs=tinysrgb&w=800',
                   'https://github.com',
                   'Django, SQLite, Bootstrap, REST API'))

    cursor.execute('INSERT INTO education (school, degree, field, start_year, end_year, details) VALUES (?, ?, ?, ?, ?, ?)',
                  ('Stanford University',
                   'Master of Science',
                   'Computer Science',
                   2019,
                   2021,
                   'Specialized in Machine Learning and Artificial Intelligence. Completed thesis on Deep Learning applications in Computer Vision.'))

    cursor.execute('INSERT INTO education (school, degree, field, start_year, end_year, details) VALUES (?, ?, ?, ?, ?, ?)',
                  ('University of California, Berkeley',
                   'Bachelor of Science',
                   'Software Engineering',
                   2015,
                   2019,
                   'Graduated with honors. Focus on full-stack web development and database systems. Active member of CS club and hackathon participant.'))

    cursor.execute('INSERT INTO education (school, degree, field, start_year, end_year, details) VALUES (?, ?, ?, ?, ?, ?)',
                  ('Online Bootcamp',
                   'Certificate',
                   'Full Stack Web Development',
                   2014,
                   2015,
                   'Intensive 6-month program covering HTML, CSS, JavaScript, Python, databases, and deployment.'))

    cursor.execute('INSERT INTO certifications (title, issuer, year, credential_url, description) VALUES (?, ?, ?, ?, ?)',
                  ('AWS Certified Solutions Architect',
                   'Amazon Web Services',
                   2023,
                   'https://aws.amazon.com',
                   'Professional level certification demonstrating expertise in designing distributed systems on AWS.'))

    cursor.execute('INSERT INTO certifications (title, issuer, year, credential_url, description) VALUES (?, ?, ?, ?, ?)',
                  ('Google Cloud Professional Developer',
                   'Google Cloud',
                   2022,
                   'https://cloud.google.com',
                   'Validates ability to build scalable and reliable cloud-native applications using Google Cloud technologies.'))

    cursor.execute('INSERT INTO certifications (title, issuer, year, credential_url, description) VALUES (?, ?, ?, ?, ?)',
                  ('Certified Kubernetes Administrator',
                   'Cloud Native Computing Foundation',
                   2023,
                   'https://cncf.io',
                   'Demonstrates skills in container orchestration, deployment, and management of Kubernetes clusters.'))

    cursor.execute('INSERT INTO certifications (title, issuer, year, credential_url, description) VALUES (?, ?, ?, ?, ?)',
                  ('Python Programming Certificate',
                   'Python Institute',
                   2021,
                   'https://pythoninstitute.org',
                   'Advanced certification covering object-oriented programming, data structures, and Python best practices.'))

    conn.commit()
    conn.close()
    print('Database initialized successfully with sample data!')

if __name__ == '__main__':
    init_database()
