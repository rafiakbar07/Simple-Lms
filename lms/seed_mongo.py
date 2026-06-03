from pymongo import MongoClient
from datetime import datetime, timedelta
import random

client = MongoClient('mongodb://admin:password123@mongodb:27017/')
db = client['lms_analytics']

# Hapus data lama
db.activity_logs.drop()
db.learning_analytics.drop()

# Data dummy
courses = [
    "Django Basics",
    "Python Advanced",
    "Docker Fundamentals",
    "REST API Design",
    "Database Optimization",
    "Redis Caching",
    "Authentication & Security",
    "Automated Testing"
]

actions = [
    "view_course",
    "enroll",
    "post_comment",
    "view_content",
    "submit_quiz",
    "download_material"
]

browsers = ["Chrome", "Firefox", "Safari", "Edge"]

# Generate 500 activity logs
logs = []
for i in range(500):
    user_id = random.randint(1, 50)
    action = random.choice(actions)
    course = random.choice(courses)
    days_ago = random.randint(0, 30)
    timestamp = datetime.now() - timedelta(
        days=days_ago,
        hours=random.randint(0, 23),
        minutes=random.randint(0, 59)
    )

    log = {
        "user_id": user_id,
        "action": action,
        "course_name": course,
        "timestamp": timestamp,
        "metadata": {
            "ip": f"192.168.1.{random.randint(1, 255)}",
            "browser": random.choice(browsers)
        }
    }
    logs.append(log)

result = db.activity_logs.insert_many(logs)
print(f"Inserted {len(result.inserted_ids)} activity logs")

# Generate learning analytics
learning_logs = []
for i in range(200):
    learning_logs.append({
        "student_id": random.randint(1, 50),
        "course_id": random.randint(1, 10),
        "lesson_id": random.randint(1, 50),
        "completed": random.choice([True, False]),
        "timestamp": datetime.now() - timedelta(
            days=random.randint(0, 30),
            hours=random.randint(0, 23)
        )
    })

db.learning_analytics.insert_many(learning_logs)
print(f"Inserted {len(learning_logs)} learning analytics")

# Buat indexes
db.activity_logs.create_index([("user_id", 1), ("timestamp", -1)])
db.activity_logs.create_index([("action", 1)])
db.activity_logs.create_index([("course_name", 1), ("action", 1)])
print("Indexes created successfully!")

# Verifikasi
print(f"\nTotal activity_logs: {db.activity_logs.count_documents({})}")
print(f"Total learning_analytics: {db.learning_analytics.count_documents({})}")

# Top 5 course terpopuler
print("\nTop 5 Popular Courses:")
pipeline = [
    {"$match": {"action": "view_course"}},
    {"$group": {"_id": "$course_name", "views": {"$sum": 1}}},
    {"$sort": {"views": -1}},
    {"$limit": 5}
]
for course in db.activity_logs.aggregate(pipeline):
    print(f"  - {course['_id']}: {course['views']} views")