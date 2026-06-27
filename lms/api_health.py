from ninja import Router
from django.db import connection
from django.core.cache import cache
import time

router = Router(tags=["Health"])


@router.get("/health", response=dict)
def health_check(request):
    """
    Health check endpoint - cek status semua service:
    Django, PostgreSQL, Redis, MongoDB
    """
    health = {
        "status": "ok",
        "services": {}
    }

    # Cek Django
    health["services"]["django"] = {"status": "ok"}

    # Cek PostgreSQL
    try:
        start = time.time()
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
            cursor.fetchone()
        latency = round((time.time() - start) * 1000, 2)
        health["services"]["postgresql"] = {
            "status": "ok",
            "latency_ms": latency
        }
    except Exception as e:
        health["services"]["postgresql"] = {"status": "error", "detail": str(e)}
        health["status"] = "degraded"

    # Cek Redis
    try:
        start = time.time()
        cache.set("health_check_ping", "pong", timeout=5)
        result = cache.get("health_check_ping")
        latency = round((time.time() - start) * 1000, 2)
        if result == "pong":
            health["services"]["redis"] = {
                "status": "ok",
                "latency_ms": latency
            }
        else:
            health["services"]["redis"] = {"status": "error", "detail": "Cache mismatch"}
            health["status"] = "degraded"
    except Exception as e:
        health["services"]["redis"] = {"status": "error", "detail": str(e)}
        health["status"] = "degraded"

    # Cek MongoDB
    try:
        from lms.mongo import get_mongo_db
        start = time.time()
        db = get_mongo_db()
        db.command("ping")
        latency = round((time.time() - start) * 1000, 2)
        health["services"]["mongodb"] = {
            "status": "ok",
            "latency_ms": latency
        }
    except Exception as e:
        health["services"]["mongodb"] = {"status": "error", "detail": str(e)}
        health["status"] = "degraded"

    # Cek Celery (cek broker connection)
    try:
        from config.celery import app as celery_app
        start = time.time()
        conn = celery_app.connection()
        conn.ensure_connection(max_retries=1, timeout=2)
        conn.release()
        latency = round((time.time() - start) * 1000, 2)
        health["services"]["celery_broker"] = {
            "status": "ok",
            "latency_ms": latency
        }
    except Exception as e:
        health["services"]["celery_broker"] = {"status": "error", "detail": str(e)}
        health["status"] = "degraded"

    return health


@router.get("/metrics", response=dict)
def metrics(request):
    """
    Metrics endpoint - statistik sederhana jumlah data di sistem.
    """
    from lms.models import User, Course, Enrollment, Lesson, Progress

    return {
        "users": {
            "total": User.objects.count(),
            "students": User.objects.filter(role="student").count(),
            "instructors": User.objects.filter(role="instructor").count(),
            "admins": User.objects.filter(role="admin").count(),
        },
        "courses": {
            "total": Course.objects.count(),
        },
        "lessons": {
            "total": Lesson.objects.count(),
        },
        "enrollments": {
            "total": Enrollment.objects.count(),
        },
        "progress": {
            "total_records": Progress.objects.count(),
            "completed": Progress.objects.filter(completed=True).count(),
        },
    }