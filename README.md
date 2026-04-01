🚀 Cara Menjalankan Project
1. Clone repository
git clone <repo-url>
cd simple-lms

2. Jalankan Docker Compose
docker-compose up --build

3. Akses di browser
http://localhost:8000

⚙️ Environment Variables

Project ini menggunakan konfigurasi berikut:

POSTGRES_DB : nama database
POSTGRES_USER : username database
POSTGRES_PASSWORD : password database
DB_HOST : host database (postgres_db)
DB_PORT : port database (5432)

📁 Project Structure
simple-lms/
├── docker-compose.yml
├── Dockerfile
├── .env.example
├── requirements.txt
├── manage.py
├── config/
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
└── README.md