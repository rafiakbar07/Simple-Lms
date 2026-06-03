from pymongo import MongoClient
from django.conf import settings
from datetime import datetime, timezone


def get_mongo_db():
    """Mendapatkan koneksi ke database MongoDB lms_analytics."""
    client = MongoClient(settings.MONGO_URI)
    return client[settings.MONGO_DB]


def log_activity(user_id: int, action: str, course_name: str = None, metadata: dict = None):
    """Mencatat aktivitas user ke MongoDB."""
    db = get_mongo_db()

    log_entry = {
        "user_id": user_id,
        "action": action,
        "timestamp": datetime.now(timezone.utc),
    }

    if course_name:
        log_entry["course_name"] = course_name
    if metadata:
        log_entry["metadata"] = metadata

    result = db.activity_logs.insert_one(log_entry)
    return str(result.inserted_id)


def log_learning(student_id: int, course_id: int, lesson_id: int, completed: bool):
    """Simpan learning analytics ke MongoDB."""
    db = get_mongo_db()
    db.learning_analytics.insert_one({
        "student_id": student_id,
        "course_id": course_id,
        "lesson_id": lesson_id,
        "completed": completed,
        "timestamp": datetime.now(timezone.utc),
    })


def get_activity_logs(user_id: int):
    """Ambil semua activity log user."""
    db = get_mongo_db()
    logs = list(
        db.activity_logs.find(
            {"user_id": user_id},
            {"_id": 0}
        ).sort("timestamp", -1).limit(10)
    )
    for log in logs:
        if "timestamp" in log:
            log["timestamp"] = log["timestamp"].isoformat()
    return logs


def get_popular_courses(limit: int = 5):
    """Top course terpopuler berdasarkan views."""
    db = get_mongo_db()
    pipeline = [
        {"$match": {"action": "view_course"}},
        {"$group": {
            "_id": "$course_name",
            "total_views": {"$sum": 1},
            "unique_users": {"$addToSet": "$user_id"}
        }},
        {"$addFields": {
            "unique_user_count": {"$size": "$unique_users"}
        }},
        {"$sort": {"total_views": -1}},
        {"$limit": limit},
        {"$project": {
            "course": "$_id",
            "total_views": 1,
            "unique_user_count": 1,
            "_id": 0
        }}
    ]
    return list(db.activity_logs.aggregate(pipeline))


def get_user_activity_summary(user_id: int):
    """Ringkasan aktivitas user tertentu."""
    db = get_mongo_db()

    pipeline = [
        {"$match": {"user_id": user_id}},
        {"$group": {
            "_id": "$action",
            "count": {"$sum": 1}
        }}
    ]
    breakdown = list(db.activity_logs.aggregate(pipeline))

    recent = list(
        db.activity_logs.find(
            {"user_id": user_id},
            {"_id": 0, "action": 1, "course_name": 1, "timestamp": 1}
        ).sort("timestamp", -1).limit(10)
    )

    for activity in recent:
        if "timestamp" in activity:
            activity["timestamp"] = activity["timestamp"].isoformat()

    return {
        "user_id": user_id,
        "actions_breakdown": {item["_id"]: item["count"] for item in breakdown},
        "total_actions": sum(item["count"] for item in breakdown),
        "recent_activities": recent
    }


def get_daily_activity_summary(days: int = 7):
    """Ringkasan aktivitas harian."""
    db = get_mongo_db()
    pipeline = [
        {"$group": {
            "_id": {"$dateToString": {"format": "%Y-%m-%d", "date": "$timestamp"}},
            "total_actions": {"$sum": 1},
            "unique_users": {"$addToSet": "$user_id"}
        }},
        {"$addFields": {
            "unique_user_count": {"$size": "$unique_users"}
        }},
        {"$sort": {"_id": -1}},
        {"$limit": days},
        {"$project": {
            "date": "$_id",
            "total_actions": 1,
            "unique_user_count": 1,
            "_id": 0
        }}
    ]
    return list(db.activity_logs.aggregate(pipeline))


def create_indexes():
    """Buat indexes untuk performa query."""
    db = get_mongo_db()

    # Index untuk query aktivitas per user diurutkan terbaru
    db.activity_logs.create_index([("user_id", 1), ("timestamp", -1)])

    # Index untuk query berdasarkan action
    db.activity_logs.create_index([("action", 1)])

    # Index untuk query per course
    db.activity_logs.create_index([("course_name", 1), ("action", 1)])

    print("MongoDB indexes created successfully!")