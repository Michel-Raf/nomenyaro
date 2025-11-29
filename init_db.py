import os
import psycopg2
from psycopg2 import sql
from datetime import datetime

DATABASE_URL = os.getenv('DATABASE_URL')

def init_database():
    conn = psycopg2.connect(DATABASE_URL, sslmode='require')
    cur = conn.cursor()

    # Create tables
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

    # Insert sample data
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

    education = [
        ('Stanford University',
         'Master of Science',
         'Computer Science',
         2019,
         2021,
         'Specialized in Machine Learning and Artificial Intelligence. Completed thesis on Deep Learning applications in Computer Vision.'),

        ('University of California, Berkeley',
         'Bachelor of Science',
         'Software Engineering',
         2015,
         2019,
         'Graduated with honors. Focus on full-stack web development and database systems. Active member of CS club and hackathon participant.'),

        ('Online Bootcamp',
         'Certificate',
         'Full Stack Web Development',
         2014,
         2015,
         'Intensive 6-month program covering HTML, CSS, JavaScript, Python, databases, and deployment.')
    ]

    for e in education:
        cur.execute(
            'INSERT INTO education (school, degree, field, start_year, end_year, details) VALUES (%s, %s, %s, %s, %s, %s)',
            e
        )

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
    print('Database initialized successfully with sample data!')


if __name__ == '__main__':
    init_database()
