from django.core.management.base import BaseCommand
from django.contrib.auth.hashers import make_password
from lms.models import User, Category, Course, Lesson, Enrollment, Progress


class Command(BaseCommand):
    help = "Seed database dengan data demo (akun admin, instructor, student, course, dll)"

    def add_arguments(self, parser):
        parser.add_argument(
            "--reset",
            action="store_true",
            help="Hapus semua data demo sebelum membuat ulang",
        )

    def handle(self, *args, **options):
        if options["reset"]:
            self.stdout.write("Menghapus data demo lama...")
            Progress.objects.all().delete()
            Enrollment.objects.all().delete()
            Lesson.objects.all().delete()
            Course.objects.all().delete()
            Category.objects.all().delete()
            User.objects.filter(username__in=[
                "admin_demo", "instructor_demo", "student_demo", "student_demo2"
            ]).delete()
            self.stdout.write(self.style.WARNING("Data demo lama telah dihapus."))

        self.stdout.write("Membuat data demo...")

        # ===== USERS =====
        admin, _ = User.objects.get_or_create(
            username="admin_demo",
            defaults={
                "email": "admin@simplelms.com",
                "password": make_password("admin123"),
                "role": "admin",
                "is_staff": True,
                "is_superuser": True,
                "first_name": "Admin",
                "last_name": "Demo",
            }
        )

        instructor, _ = User.objects.get_or_create(
            username="instructor_demo",
            defaults={
                "email": "instructor@simplelms.com",
                "password": make_password("instructor123"),
                "role": "instructor",
                "first_name": "Instructor",
                "last_name": "Demo",
            }
        )

        student, _ = User.objects.get_or_create(
            username="student_demo",
            defaults={
                "email": "student@simplelms.com",
                "password": make_password("student123"),
                "role": "student",
                "first_name": "Student",
                "last_name": "Demo",
            }
        )

        student2, _ = User.objects.get_or_create(
            username="student_demo2",
            defaults={
                "email": "student2@simplelms.com",
                "password": make_password("student123"),
                "role": "student",
                "first_name": "Student",
                "last_name": "Two",
            }
        )

        self.stdout.write(self.style.SUCCESS("✓ Users created"))

        # ===== CATEGORIES =====
        cat_programming, _ = Category.objects.get_or_create(
            name="Programming", defaults={"parent": None}
        )
        cat_web, _ = Category.objects.get_or_create(
            name="Web Development", defaults={"parent": cat_programming}
        )
        cat_data, _ = Category.objects.get_or_create(
            name="Data Science", defaults={"parent": cat_programming}
        )

        self.stdout.write(self.style.SUCCESS("✓ Categories created"))

        # ===== COURSES =====
        course1, _ = Course.objects.get_or_create(
            title="Django for Beginners",
            defaults={"instructor": instructor, "category": cat_web}
        )

        course2, _ = Course.objects.get_or_create(
            title="REST API dengan Django Ninja",
            defaults={"instructor": instructor, "category": cat_web}
        )

        course3, _ = Course.objects.get_or_create(
            title="Pengantar Data Science",
            defaults={"instructor": instructor, "category": cat_data}
        )

        self.stdout.write(self.style.SUCCESS("✓ Courses created"))

        # ===== LESSONS =====
        lessons_data = [
            (course1, "Pengenalan Django", 1),
            (course1, "Setup Project Django", 2),
            (course1, "Models dan Database", 3),
            (course1, "Views dan Templates", 4),
            (course2, "Apa itu REST API", 1),
            (course2, "Setup Django Ninja", 2),
            (course2, "Membuat Endpoint Pertama", 3),
            (course3, "Pengenalan Data Science", 1),
            (course3, "Tools dan Library", 2),
        ]

        for course, title, order in lessons_data:
            Lesson.objects.get_or_create(
                course=course, title=title, defaults={"order": order}
            )

        self.stdout.write(self.style.SUCCESS("✓ Lessons created"))

        # ===== ENROLLMENTS =====
        enrollment1, _ = Enrollment.objects.get_or_create(
            student=student, course=course1
        )
        Enrollment.objects.get_or_create(
            student=student, course=course2
        )
        Enrollment.objects.get_or_create(
            student=student2, course=course1
        )

        self.stdout.write(self.style.SUCCESS("✓ Enrollments created"))

        # ===== PROGRESS =====
        course1_lessons = Lesson.objects.filter(course=course1).order_by("order")
        for i, lesson in enumerate(course1_lessons):
            Progress.objects.get_or_create(
                student=student,
                lesson=lesson,
                defaults={"completed": i < 2}
            )

        self.stdout.write(self.style.SUCCESS("✓ Progress created"))

        # ===== SUMMARY =====
        self.stdout.write("\n" + "=" * 50)
        self.stdout.write(self.style.SUCCESS("SEED DATA BERHASIL DIBUAT!"))
        self.stdout.write("=" * 50)
        self.stdout.write("\nAkun Demo:")
        self.stdout.write("  Admin      -> username: admin_demo      | password: admin123")
        self.stdout.write("  Instructor -> username: instructor_demo | password: instructor123")
        self.stdout.write("  Student    -> username: student_demo    | password: student123")
        self.stdout.write("  Student 2  -> username: student_demo2   | password: student123")
        self.stdout.write("\nData:")
        self.stdout.write(f"  Categories  : {Category.objects.count()}")
        self.stdout.write(f"  Courses     : {Course.objects.count()}")
        self.stdout.write(f"  Lessons     : {Lesson.objects.count()}")
        self.stdout.write(f"  Enrollments : {Enrollment.objects.count()}")
        self.stdout.write(f"  Progress    : {Progress.objects.count()}")
        self.stdout.write("=" * 50)