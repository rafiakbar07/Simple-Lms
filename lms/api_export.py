from ninja import Router
from ninja.errors import HttpError
from django.http import HttpResponse
import csv
import json

from lms.models import Course
from lms.tasks import export_course_report
from lms.mongo import get_activity_logs, get_popular_courses, get_daily_activity_summary

router = Router(tags=["Export Analytics"])


@router.get("/courses/csv")
def export_courses_csv(request):
    """Export semua data course ke CSV (langsung, synchronous)."""
    response = HttpResponse(content_type="text/csv")
    response["Content-Disposition"] = 'attachment; filename="courses_export.csv"'

    writer = csv.writer(response)
    writer.writerow(["ID", "Title", "Instructor", "Category", "Total Lessons", "Total Enrollments"])

    courses = Course.objects.select_related("instructor", "category").prefetch_related("lesson_set", "enrollment_set")

    for course in courses:
        writer.writerow([
            course.id,
            course.title,
            course.instructor.username,
            course.category.name,
            course.lesson_set.count(),
            course.enrollment_set.count(),
        ])

    return response


@router.get("/courses/json")
def export_courses_json(request):
    """Export semua data course ke JSON."""
    courses = Course.objects.select_related("instructor", "category").prefetch_related("lesson_set", "enrollment_set")

    data = []
    for course in courses:
        data.append({
            "id": course.id,
            "title": course.title,
            "instructor": course.instructor.username,
            "category": course.category.name,
            "total_lessons": course.lesson_set.count(),
            "total_enrollments": course.enrollment_set.count(),
        })

    response = HttpResponse(
        json.dumps(data, indent=2),
        content_type="application/json"
    )
    response["Content-Disposition"] = 'attachment; filename="courses_export.json"'
    return response


@router.post("/courses/{course_id}/async", response=dict)
def export_course_async(request, course_id: int):
    """Export report sebuah course secara ASYNC via Celery."""
    try:
        course = Course.objects.get(id=course_id)
    except Course.DoesNotExist:
        raise HttpError(404, "Course not found")

    task = export_course_report.delay(course_id)

    return {
        "message": f"Export report untuk '{course.title}' sedang diproses",
        "task_id": task.id,
        "check_status_url": f"/api/export/task-status/{task.id}",
    }


@router.get("/task-status/{task_id}", response=dict)
def check_task_status(request, task_id: str):
    """Cek status task Celery berdasarkan task_id."""
    from celery.result import AsyncResult

    result = AsyncResult(task_id)

    response = {
        "task_id": task_id,
        "status": result.status,
    }

    if result.status == "SUCCESS":
        response["result"] = result.result
    elif result.status == "FAILURE":
        response["error"] = str(result.result)

    return response


@router.get("/activity-logs/csv")
def export_activity_logs_csv(request, user_id: int = None, limit: int = 100):
    """Export activity logs dari MongoDB ke CSV."""
    response = HttpResponse(content_type="text/csv")
    response["Content-Disposition"] = 'attachment; filename="activity_logs_export.csv"'

    writer = csv.writer(response)
    writer.writerow(["User ID", "Action", "Course Name", "Timestamp"])

    if user_id:
        logs = get_activity_logs(user_id)
    else:
        from lms.mongo import get_mongo_db
        db = get_mongo_db()
        logs = list(
            db.activity_logs.find({}, {"_id": 0})
            .sort("timestamp", -1)
            .limit(limit)
        )
        for log in logs:
            if "timestamp" in log:
                log["timestamp"] = log["timestamp"].isoformat()

    for log in logs:
        writer.writerow([
            log.get("user_id", ""),
            log.get("action", ""),
            log.get("course_name", ""),
            log.get("timestamp", ""),
        ])

    return response


@router.get("/popular-courses/json")
def export_popular_courses_json(request, limit: int = 10):
    """Export data course terpopuler (dari MongoDB aggregation) ke JSON."""
    data = get_popular_courses(limit=limit)
    response = HttpResponse(
        json.dumps(data, indent=2),
        content_type="application/json"
    )
    response["Content-Disposition"] = 'attachment; filename="popular_courses.json"'
    return response


@router.get("/daily-summary/csv")
def export_daily_summary_csv(request, days: int = 30):
    """Export ringkasan aktivitas harian ke CSV."""
    data = get_daily_activity_summary(days=days)

    response = HttpResponse(content_type="text/csv")
    response["Content-Disposition"] = 'attachment; filename="daily_summary.csv"'

    writer = csv.writer(response)
    writer.writerow(["Date", "Total Actions", "Unique Users"])

    for item in data:
        writer.writerow([
            item.get("date", ""),
            item.get("total_actions", 0),
            item.get("unique_user_count", 0),
        ])

    return response