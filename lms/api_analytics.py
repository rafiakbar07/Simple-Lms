from ninja import Router
from ninja.errors import HttpError
from lms.mongo import (
    log_activity,
    get_popular_courses,
    get_user_activity_summary,
    get_daily_activity_summary,
    create_indexes,
)

router = Router(tags=["Analytics"])


@router.post("/log", response=dict)
def log_user_activity(request, user_id: int, action: str, course_name: str = None):
    """Mencatat aktivitas user ke MongoDB."""
    try:
        log_id = log_activity(
            user_id=user_id,
            action=action,
            course_name=course_name,
        )
        return {"status": "logged", "log_id": log_id}
    except Exception as e:
        raise HttpError(500, f"Failed to log activity: {str(e)}")


@router.get("/popular-courses", response=list)
def popular_courses(request, limit: int = 5):
    """Mengambil top course terpopuler berdasarkan views."""
    try:
        return get_popular_courses(limit=limit)
    except Exception as e:
        raise HttpError(500, f"Failed to get popular courses: {str(e)}")


@router.get("/user-activity/{user_id}", response=dict)
def user_activity(request, user_id: int):
    """Mengambil ringkasan aktivitas user tertentu."""
    try:
        return get_user_activity_summary(user_id=user_id)
    except Exception as e:
        raise HttpError(500, f"Failed to get user activity: {str(e)}")


@router.get("/daily-summary", response=list)
def daily_summary(request, days: int = 7):
    """Mengambil ringkasan aktivitas harian."""
    try:
        return get_daily_activity_summary(days=days)
    except Exception as e:
        raise HttpError(500, f"Failed to get daily summary: {str(e)}")


@router.post("/create-indexes", response=dict)
def setup_indexes(request):
    """Membuat MongoDB indexes untuk optimasi performa."""
    try:
        create_indexes()
        return {"status": "success", "message": "Indexes created successfully"}
    except Exception as e:
        raise HttpError(500, f"Failed to create indexes: {str(e)}")