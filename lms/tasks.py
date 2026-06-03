import csv
import io
from celery import shared_task
from django.core.mail import send_mail
from django.conf import settings


@shared_task
def send_enrollment_email(student_email: str, student_name: str, course_title: str):
    """Kirim email saat student enroll ke course."""
    subject = f"Enrollment Confirmation - {course_title}"
    message = f"""
Halo {student_name},

Selamat! Kamu berhasil mendaftar ke course:
📚 {course_title}

Selamat belajar!

Salam,
Simple LMS Team
    """
    send_mail(
        subject=subject,
        message=message,
        from_email=settings.EMAIL_HOST_USER or "noreply@simplelms.com",
        recipient_list=[student_email],
        fail_silently=True,
    )
    return f"Email sent to {student_email}"


@shared_task
def generate_certificate(student_name: str, course_title: str, enrollment_id: int):
    """Generate certificate saat course selesai."""
    certificate_data = {
        "enrollment_id": enrollment_id,
        "student_name": student_name,
        "course_title": course_title,
        "certificate_number": f"CERT-{enrollment_id:05d}",
        "status": "generated",
    }
    return certificate_data


@shared_task
def update_course_statistics():
    """Scheduled task: update enrollment count semua course."""
    from lms.models import Course
    from django.db.models import Count

    courses = Course.objects.annotate(enrollment_count=Count("enrollment"))
    updated = []
    for course in courses:
        updated.append({
            "course_id": course.id,
            "title": course.title,
            "enrollment_count": course.enrollment_count,
        })
    return {"updated_courses": len(updated), "data": updated}


@shared_task
def export_course_report(course_id: int):
    """Generate CSV report untuk sebuah course secara async."""
    from lms.models import Course

    try:
        course = Course.objects.prefetch_related(
            "enrollment_set__student"
        ).get(id=course_id)
    except Course.DoesNotExist:
        return {"error": "Course not found"}

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["No", "Student", "Email", "Enrolled At"])

    for i, enrollment in enumerate(course.enrollment_set.all(), start=1):
        writer.writerow([
            i,
            enrollment.student.username,
            enrollment.student.email,
            enrollment.enrolled_at.strftime("%Y-%m-%d %H:%M"),
        ])

    return {
        "course": course.title,
        "total_students": course.enrollment_set.count(),
        "csv_data": output.getvalue(),
    }