Simple LMS
Simple LMS adalah project Learning Management System (LMS) sederhana berbasis Django, PostgreSQL, dan Docker.

Project ini dibuat untuk memenuhi tugas Capstone Progress 1 & Progress 2:

Progress 1: Docker & Django Foundation
Progress 2: Database Design & ORM Implementation

🔧 Cara Menjalankan Project
1. Clone Repository
git clone <repo-url>
cd simple-lms
2. Jalankan Docker
docker-compose up --build
3. Jalankan Migration
docker-compose exec web python manage.py makemigrations
docker-compose exec web python manage.py migrate
4. Buat Superuser (Opsional)
docker-compose exec web python manage.py createsuperuser
5. Akses Project
Django App → http://localhost:8000
Django Admin → http://localhost:8000/admin

⚙️ Environment Variables
Project ini menggunakan konfigurasi berikut:
POSTGRES_DB : nama database
POSTGRES_USER : username database
POSTGRES_PASSWORD : password database
DB_HOST : host database (postgres_db)
DB_PORT : port database (5432)

🚀 Features
Progress 1
Docker
Setup Django
PostgreSQL
Project jalan di localhost

Progress 2
Models (User, Course, dll)
Relasi database
Django Admin
Query Optimization
N+1 Demo

 🛠️ Tech Stack
- Python 3.13
- Django 6
- PostgreSQL
- Docker & Docker Compose

🧱 Data Models
1. User
username
email
role (admin, instructor, student)

2. Category
name
parent (self-referencing)

3. Course
title
description
instructor (User)
category (Category)

4. Lesson
title
content
order
course (Course)

5. Enrollment
student (User)
course (Course)
enrolled_at

Unique constraint: student + course

6. Progress
student (User)
lesson (Lesson)
completed
completed_at

📁 Project Structure
simple-lms/
├── config/
│   ├── __init__.py
│   ├── asgi.py
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── lms/
│   ├── migrations/
│   ├── __init__.py
│   ├── admin.py
│   ├── apps.py
│   ├── models.py
│   ├── tests.py
│   └── views.py
├── .env.example
├── docker-compose.yml
├── Dockerfile
├── manage.py
├── README.md
└── requirements.txt