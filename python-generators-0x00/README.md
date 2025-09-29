ALX Travel App & Python Generators Project

This project consists of two main components:

    Django ALX Travel App - A Django-based web application with API documentation and MySQL configuration

    Python Generators with MySQL - A demonstration of Python generators for streaming database rows efficiently

🏗️ Part 1: Django ALX Travel App

A complete Django project setup with REST API, Swagger documentation, and MySQL database configuration.
Project Structure
text

alx_travel_app/
├── requirements.txt
├── manage.py
├── alx_travel_app/
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
└── listings/
    ├── models.py
    ├── views.py
    ├── urls.py
    └── serializers.py

Features

    Django REST Framework for building Web APIs

    Swagger/OpenAPI Documentation with drf-yasg

    MySQL Database configuration with environment variables

    CORS Headers for cross-origin requests

    Listings App with CRUD operations

Setup Instructions

    Clone and setup environment:
    bash

python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

Install dependencies:
bash

pip install -r requirements.txt

Configure environment variables:
Create a .env file:
bash

SECRET_KEY=your-django-secret-key-here
DEBUG=True
DATABASE_URL=mysql://username:password@localhost:3306/alx_travel_db
ALLOWED_HOSTS=localhost,127.0.0.1

Run migrations:
bash

python manage.py makemigrations
python manage.py migrate

Start development server:
bash

python manage.py runserver

API Endpoints

    API Documentation: http://127.0.0.1:8000/swagger/

    Admin Panel: http://127.0.0.1:8000/admin/

    Listings API: http://127.0.0.1:8000/api/listings/

🔄 Part 2: Python Generators with MySQL

A demonstration of Python generators for efficiently streaming database rows one by one.
Files

    seed.py - Database setup and generator functions

    0-main.py - Demonstration script

    user_data.csv - Sample data file

Generator Functions
1. Single Row Generator
python

def stream_users(connection):
    """Streams rows from user_data table one by one"""
    cursor = connection.cursor()
    cursor.execute("SELECT user_id, name, email, age FROM user_data")
    
    while True:
        row = cursor.fetchone()
        if row is None:
            break
        yield row

2. Batch Generator
python

def stream_users_batch(connection, batch_size=100):
    """Streams rows in batches for better performance"""
    cursor = connection.cursor()
    cursor.execute("SELECT user_id, name, email, age FROM user_data")
    
    while True:
        rows = cursor.fetchmany(batch_size)
        if not rows:
            break
        yield rows

Setup and Usage

    Install dependencies:
    bash

pip install mysql-connector-python==8.1.0

Set environment variables (optional):
bash

export DB_HOST=localhost
export DB_USER=root
export DB_PASSWORD=your_password
export DB_PORT=3306

Run the demonstration:
bash

python3 0-main.py

Benefits of Using Generators

    Memory Efficiency: Only one row/batch loaded in memory at a time

    Lazy Evaluation: Data processed as needed, not all at once

    Performance: Can handle very large datasets without memory issues

    Clean Code: Simple iteration pattern with for loops

Example Usage
python

# Process users one by one
for user in stream_users(connection):
    user_id, name, email, age = user
    print(f"Processing: {name}")

# Process users in batches
for batch in stream_users_batch(connection, batch_size=50):
    print(f"Processing {len(batch)} users")
    for user in batch:
        process_user(user)

🗃️ Database Schema
ALX_prodev Database
sql

CREATE TABLE user_data (
    user_id VARCHAR(36) PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    email VARCHAR(255) NOT NULL,
    age DECIMAL(5,2) NOT NULL,
    INDEX idx_user_id (user_id)
);

📊 Sample Data Format

The user_data.csv file should contain:
csv

user_id,name,email,age
00234e50-34eb-4ce2-94ec-26e3fa749796,Dan Altenwerth Jr.,Molly59@gmail.com,67
006bfede-724d-4cdd-a2a6-59700f40d0da,Glenda Wisozk,Miriam21@gmail.com,119

🛠️ Technologies Used
Django App

    Django 4.2.7

    Django REST Framework 3.14.0

    MySQL Client 2.2.0

    drf-yasg 1.21.7 (Swagger Documentation)

    django-environ 0.10.0

Generators Project

    Python 3.x

    mysql-connector-python 8.1.0

📝 Key Concepts Demonstrated

    Django Project Setup with modern best practices

    REST API Development with proper documentation

    Database Configuration using environment variables

    Python Generators for memory-efficient data processing

    MySQL Integration with proper connection handling

    CSV Data Import with batch processing

🚀 Future Enhancements

    Add authentication and authorization

    Implement pagination for large datasets

    Add more API endpoints and filters

    Implement caching for better performance

    Add unit tests and integration tests
