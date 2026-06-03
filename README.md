# Simple LMS
Simple LMS adalah project Learning Management System (LMS) sederhana berbasis Django, PostgreSQL, dan Docker.

Project ini dibuat untuk memenuhi tugas Capstone Progress 1, 2, 3 & 4:

- Progress 1: Docker & Django Foundation
- Progress 2: Database Design & ORM Implementation
- Progress 3: REST API dengan Django Ninja
- Progress 4: Advanced Features & Integration

---

## 🔧 Cara Menjalankan Project

### 1. Clone Repository
```bash
git clone <repo-url>
cd simple-lms
```

### 2. Buat file `.env`
```bash
copy .env.example .env
```

### 3. Jalankan Docker
```bash
docker-compose up --build
```

### 4. Jalankan Migration
```bash
docker-compose exec web python manage.py makemigrations
docker-compose exec web python manage.py migrate
```

### 5. Seed Data MongoDB (Progress 4)
```bash
docker-compose exec web python lms/seed_mongo.py
```

### 6. Buat Superuser (Opsional)
```bash
docker-compose exec web python manage.py createsuperuser
```

### 7. Akses Project
- Django App → http://localhost:8000
- Django Admin → http://localhost:8000/admin
- API Docs (Swagger) → http://localhost:8000/api/docs
- Flower (Celery Monitor) → http://localhost:5555
- RabbitMQ Dashboard → http://localhost:15672 (guest/guest)

### 8. Mematikan Docker
```bash
docker-compose down
```

---

## ⚙️ Environment Variables

Project ini menggunakan konfigurasi berikut (di `.env`):

| Variable | Keterangan |
|----------|------------|
| DEBUG | Mode debug Django |
| SECRET_KEY | Secret key Django |
| DB_NAME | Nama database PostgreSQL |
| DB_USER | Username database |
| DB_PASSWORD | Password database |
| DB_HOST | Host database (db) |
| DB_PORT | Port database (5432) |
| REDIS_URL | URL koneksi Redis |
| MONGO_URI | URI koneksi MongoDB |
| MONGO_DB | Nama database MongoDB |
| CELERY_BROKER_URL | URL RabbitMQ broker |
| CELERY_RESULT_BACKEND | Backend hasil Celery |

---

## 🚀 Features

### Progress 1
- Docker
- Setup Django
- PostgreSQL
- Project jalan di localhost

### Progress 2
- Models (User, Course, dll)
- Relasi database
- Django Admin
- Query Optimization
- N+1 Demo

### Progress 3
- REST API dengan Django Ninja
- JWT Authentication (access + refresh token)
- Role-Based Access Control (RBAC)
- Swagger UI dokumentasi otomatis
- Pydantic schema validation
- CRUD endpoints untuk Course
- Enrollment & Progress tracking

### Progress 4
- Redis caching (course list & detail)
- Cache invalidation otomatis
- Rate limiting (60 requests/menit)
- MongoDB activity logs & analytics
- Aggregation pipeline (top courses, daily summary)
- Celery async tasks (email, certificate, report)
- RabbitMQ message broker
- Flower monitoring dashboard

---

## 🔌 API Endpoints

### Authentication
| Method | Endpoint | Deskripsi |
|--------|----------|-----------|
| POST | `/api/auth/register` | Register user baru |
| POST | `/api/auth/login` | Login & dapat JWT token |
| POST | `/api/auth/refresh` | Refresh access token |
| GET | `/api/auth/me` | Info user saat ini |
| PUT | `/api/auth/me` | Update profil |

### Courses
| Method | Endpoint | Deskripsi |
|--------|----------|-----------|
| GET | `/api/courses` | List semua course (pagination + filter + cache) |
| GET | `/api/courses/{id}` | Detail course (cache) |
| POST | `/api/courses` | Buat course baru |
| PATCH | `/api/courses/{id}` | Update course |
| DELETE | `/api/courses/{id}` | Hapus course |

### Enrollments
| Method | Endpoint | Deskripsi |
|--------|----------|-----------|
| POST | `/api/enrollments` | Daftar ke course |
| GET | `/api/enrollments/student/{id}` | Course yang diikuti student |
| POST | `/api/enrollments/{id}/progress` | Update progress lesson |

### Analytics (MongoDB)
| Method | Endpoint | Deskripsi |
|--------|----------|-----------|
| POST | `/api/analytics/log` | Catat aktivitas user |
| GET | `/api/analytics/popular-courses` | Top course terpopuler |
| GET | `/api/analytics/user-activity/{id}` | Aktivitas user |
| GET | `/api/analytics/daily-summary` | Ringkasan aktivitas harian |
| POST | `/api/analytics/create-indexes` | Buat MongoDB indexes |

---

## ⚡ Celery Tasks

| Task | Deskripsi | Trigger |
|------|-----------|---------|
| `send_enrollment_email` | Kirim email konfirmasi enrollment | Saat student enroll |
| `generate_certificate` | Generate sertifikat kelulusan | Saat progress 100% |
| `update_course_statistics` | Update statistik enrollment | Scheduled (periodic) |
| `export_course_report` | Export CSV report course | Async on demand |

---

## 🛠️ Tech Stack
- Python 3.12
- Django 6
- PostgreSQL 15
- Docker & Docker Compose
- Django Ninja (REST API)
- Pydantic (Schema Validation)
- PyJWT (Authentication)
- Redis (Caching & Rate Limiting)
- MongoDB (Activity Logs & Analytics)
- Celery (Async Tasks)
- RabbitMQ (Message Broker)
- Flower (Celery Monitoring)

---

## 🧱 Data Models

### 1. User
- username
- email
- role (admin, instructor, student)

### 2. Category
- name
- parent (self-referencing)

### 3. Course
- title
- instructor (User)
- category (Category)

### 4. Lesson
- title
- content
- order
- course (Course)

### 5. Enrollment
- student (User)
- course (Course)
- enrolled_at
- *Unique constraint: student + course*

### 6. Progress
- student (User)
- lesson (Lesson)
- completed
- completed_at

---

## 📊 MongoDB Collections

### activity_logs
```json
{
  "user_id": 1,
  "action": "view_course",
  "course_name": "Django Basics",
  "timestamp": "2025-01-15T10:30:00Z",
  "metadata": {
    "ip": "192.168.1.1",
    "browser": "Chrome"
  }
}
```

### learning_analytics
```json
{
  "student_id": 1,
  "course_id": 1,
  "lesson_id": 1,
  "completed": true,
  "timestamp": "2025-01-15T10:30:00Z"
}
```

---

## 📁 Project Structure

```
simple-lms/
├── config/
│   ├── __init__.py
│   ├── asgi.py
│   ├── celery.py
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── lms/
│   ├── migrations/
│   ├── __init__.py
│   ├── admin.py
│   ├── api.py
│   ├── api_analytics.py
│   ├── api_auth.py
│   ├── api_courses.py
│   ├── api_enrollments.py
│   ├── apps.py
│   ├── auth.py
│   ├── models.py
│   ├── mongo.py
│   ├── rate_limit.py
│   ├── schemas.py
│   ├── seed_mongo.py
│   ├── tasks.py
│   ├── tests.py
│   └── views.py
├── .env
├── .env.example
├── docker-compose.yml
├── Dockerfile
├── .gitignore
├── manage.py
├── README.md
└── requirements.txt
```

---

*Project ini dibuat untuk mata kuliah Pemrograman Sisi Server*