# FINAL PROJECT REPORT
## Simple LMS Extended Backend

---

## 👤 Identitas
- **Nama:** Muhammad Rafi Akbar Hakim
- **NIM:** A11.2023.14917
- **Kelas:** 4618
- **Mata Kuliah:** Pemrograman Sisi Server (A11.54403)
- **Pengajar:** Fahri Firdausillah, S.Kom, M.CS
- **URL Repository:** https://github.com/rafiakbar07/Simple-Lms

---

## 📋 Deskripsi Project
Simple LMS adalah aplikasi Learning Management System (LMS) sederhana berbasis Django yang dikembangkan menggunakan Docker, PostgreSQL, Redis, MongoDB, Celery, dan RabbitMQ. Project ini menyediakan REST API lengkap untuk pengelolaan course, enrollment, dan progress belajar mahasiswa. Project ini merupakan kelanjutan dari tugas Capstone Progress 1-4 yang kemudian dikembangkan lebih lanjut dengan menambahkan fitur-fitur lanjutan.

---

## ✅ Fitur Dasar yang Sudah Berjalan
- Docker & Docker Compose (semua service berjalan)
- Django project dengan PostgreSQL
- Model utama: User, Category, Course, Lesson, Enrollment, Progress
- REST API menggunakan Django Ninja
- JWT Authentication (access token + refresh token)
- Role-Based Access Control (admin, instructor, student)
- Endpoint dasar: course, enrollment, progress
- Swagger/OpenAPI dokumentasi di `/api/docs`
- Redis caching untuk course list & detail
- Cache invalidation strategy
- Rate limiting berbasis Redis
- MongoDB activity logging & learning analytics
- Celery async tasks (email, certificate, report)
- RabbitMQ message broker
- Flower monitoring dashboard

---

## 🚀 Fitur Tambahan yang Dipilih

| No | Fitur | Kategori | Poin | Status |
|----|-------|----------|------|--------|
| 1 | Health check & metrics endpoint | Observability (L) | 12 | ✅ Selesai |
| 2 | Cache monitoring sederhana | Redis/Performance (D) | 10 | ✅ Selesai |
| 3 | Export analytics CSV/JSON + async | Celery/Analytics (F & E) | 12 | ✅ Selesai |
| 4 | Seed/reset demo data command | Developer Experience (I) | 10 | ✅ Selesai |

**Total Poin Fitur Tambahan: 44 poin**

---

## 💡 Penjelasan Implementasi

### 1. Health Check & Metrics Endpoint (12 poin)
Endpoint `GET /api/health` melakukan pengecekan real-time terhadap semua service yang berjalan:
- **Django** — status aplikasi
- **PostgreSQL** — koneksi database + latency (ms)
- **Redis** — koneksi cache + latency (ms)
- **MongoDB** — koneksi database + latency (ms)
- **Celery Broker (RabbitMQ)** — koneksi message broker + latency (ms)

Endpoint `GET /api/metrics` menampilkan statistik jumlah data di sistem:
- Total user per role (admin, instructor, student)
- Total course, lesson, enrollment, progress

File: `lms/api_health.py`

### 2. Cache Monitoring Sederhana (10 poin)
Endpoint untuk memonitor kondisi Redis cache secara real-time:
- `GET /api/cache/stats` — statistik Redis: memory usage, hit/miss ratio, connected clients, uptime
- `GET /api/cache/keys` — list semua cache keys beserta TTL-nya
- `GET /api/cache/check/{key}` — cek apakah key tertentu ada di cache
- `DELETE /api/cache/clear` — hapus cache berdasarkan pattern

Fitur ini sangat berguna untuk debugging caching strategy yang sudah diimplementasikan pada course list/detail.

File: `lms/api_cache.py`

### 3. Export Analytics CSV/JSON + Async (12 poin)
Fitur export data dalam berbagai format:
- `GET /api/export/courses/csv` — export semua course ke CSV (synchronous)
- `GET /api/export/courses/json` — export semua course ke JSON (synchronous)
- `POST /api/export/courses/{id}/async` — export report course via Celery (asynchronous)
- `GET /api/export/task-status/{task_id}` — cek status task Celery
- `GET /api/export/activity-logs/csv` — export activity logs dari MongoDB
- `GET /api/export/popular-courses/json` — export top courses dari MongoDB
- `GET /api/export/daily-summary/csv` — export ringkasan aktivitas harian

File: `lms/api_export.py`

### 4. Seed/Reset Demo Data Command (10 poin)
Management command Django untuk membuat data demo secara otomatis:
```bash
python manage.py seed_demo_data         # Buat data demo
python manage.py seed_demo_data --reset # Reset dan buat ulang
```
Command ini membuat akun demo untuk setiap role, kategori, course, lesson, enrollment, dan progress data sehingga project mudah diuji tanpa perlu input manual.

File: `lms/management/commands/seed_demo_data.py`

---

## 🔧 Cara Menjalankan Project

### 1. Clone Repository
```bash
git clone https://github.com/rafiakbar07/Simple-Lms.git
cd Simple-Lms
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
docker-compose exec web python manage.py migrate
```

### 5. Seed Demo Data
```bash
docker-compose exec web python manage.py seed_demo_data
```

### 6. Seed MongoDB (opsional)
```bash
docker-compose exec web python lms/seed_mongo.py
```

### 7. Akses Project
| Service | URL |
|---------|-----|
| Django App | http://localhost:8000 |
| Django Admin | http://localhost:8000/admin |
| API Docs (Swagger) | http://localhost:8000/api/docs |
| Flower (Celery Monitor) | http://localhost:5555 |
| RabbitMQ Dashboard | http://localhost:15672 |

### 8. Mematikan Docker
```bash
docker-compose down
```

---

## 👥 Akun Demo

| Role | Username | Password |
|------|----------|----------|
| Admin | `admin_demo` | `admin123` |
| Instructor | `instructor_demo` | `instructor123` |
| Student | `student_demo` | `student123` |
| Student 2 | `student_demo2` | `student123` |

---

## 🔌 Endpoint Penting

### Authentication
| Method | Endpoint | Deskripsi |
|--------|----------|-----------|
| POST | `/api/auth/register` | Register user baru |
| POST | `/api/auth/login` | Login & dapat JWT token |
| POST | `/api/auth/refresh` | Refresh access token |
| GET | `/api/auth/me` | Info user saat ini |

### Courses
| Method | Endpoint | Deskripsi |
|--------|----------|-----------|
| GET | `/api/courses` | List courses (pagination + filter + cache) |
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
| GET | `/api/analytics/popular-courses` | Top course terpopuler |
| GET | `/api/analytics/user-activity/{id}` | Aktivitas user |
| GET | `/api/analytics/daily-summary` | Ringkasan aktivitas harian |

### Health & Monitoring
| Method | Endpoint | Deskripsi |
|--------|----------|-----------|
| GET | `/api/health` | Cek status semua service |
| GET | `/api/metrics` | Statistik data sistem |
| GET | `/api/cache/stats` | Statistik Redis cache |
| GET | `/api/cache/keys` | List cache keys & TTL |

### Export Analytics
| Method | Endpoint | Deskripsi |
|--------|----------|-----------|
| GET | `/api/export/courses/csv` | Export course ke CSV |
| GET | `/api/export/courses/json` | Export course ke JSON |
| POST | `/api/export/courses/{id}/async` | Export async via Celery |
| GET | `/api/export/task-status/{task_id}` | Cek status task |

---

## 📸 Screenshot / Bukti Pengujian

Screenshot tersedia di folder `docs/screenshots/`:

1. Swagger UI — semua endpoint
2. Health Check response (semua service "ok")
3. Metrics endpoint response
4. Cache Stats response
5. Cache Keys response
6. Export CSV response
7. Export JSON response
8. Export Async + Task Status response
9. Flower Celery Monitor
10. RabbitMQ Dashboard
11. Seed Data terminal output

---

## 🔧 Kendala dan Solusi

| No | Kendala | Solusi |
|----|---------|--------|
| 1 | `django-celery-beat` tidak support Django 6 | Hapus versi spesifik di requirements.txt, biarkan pip pilih versi compatible |
| 2 | Docker image corrupt saat build | Jalankan `docker system prune -a --volumes` lalu restart Docker Desktop |
| 3 | Error `email-validator is not installed` | Tambahkan `email-validator==2.1.1` di requirements.txt |
| 4 | PostgreSQL password authentication failed | Jalankan `docker-compose down -v` untuk hapus volume lama lalu build ulang |
| 5 | Field `content` tidak ada di model Lesson | Hapus field `content` dari seed_demo_data.py |
| 6 | Import warning Pylance di VS Code | Install package di lokal dengan `pip install <package>` |

---

## 📝 Kesimpulan

Mengerjakan Final Project Simple LMS Extended Backend memberikan pengalaman yang sangat berharga dalam membangun sistem backend yang kompleks dan terintegrasi. Saya berhasil mengintegrasikan berbagai teknologi modern seperti Django, PostgreSQL, Redis, MongoDB, Celery, dan RabbitMQ dalam satu sistem yang kohesif menggunakan Docker.

Tantangan terbesar adalah menangani dependency conflict antar package Python dan masalah Docker image yang corrupt. Namun, melalui proses troubleshooting yang teliti, semua masalah berhasil diselesaikan.

Fitur-fitur tambahan yang diimplementasikan (Health Check, Cache Monitoring, Export Analytics, dan Seed Data) berhasil meningkatkan kualitas dan kemudahan pengujian sistem. Proyek ini memberikan pemahaman mendalam tentang arsitektur backend modern yang production-ready.