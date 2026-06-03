from ninja import Router, Query
from ninja.errors import HttpError
from typing import Optional
from django.core.cache import cache
from lms.models import Course, Category, User
from lms.schemas import (
    CourseCreateSchema, CourseUpdateSchema,
    CourseDetailSchema, PaginatedCoursesSchema, MessageSchema
)
from lms.rate_limit import rate_limit

router = Router(tags=["Courses"])

CACHE_TTL = 60 * 5  # 5 menit


def serialize_detail(course):
    return {
        "id": course.id,
        "title": course.title,
        "instructor": {
            "id": course.instructor.id,
            "username": course.instructor.username,
            "email": course.instructor.email,
            "role": course.instructor.role,
        },
        "category": {
            "id": course.category.id,
            "name": course.category.name,
            "parent_id": course.category.parent_id,
        },
        "lessons": [
            {"id": l.id, "title": l.title, "order": l.order}
            for l in course.lesson_set.all()
        ],
    }


@router.get("", response=PaginatedCoursesSchema)
def list_courses(
    request,
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    category_id: Optional[int] = None,
    search: Optional[str] = None,
):
    # Rate limiting
    rate_limit(request.META.get("REMOTE_ADDR", "unknown"))

    # Cache
    cache_key = f"courses:list:{page}:{page_size}:{category_id}:{search}"
    cached = cache.get(cache_key)
    if cached:
        return cached

    qs = Course.objects.for_listing()
    if category_id:
        qs = qs.filter(category_id=category_id)
    if search:
        qs = qs.filter(title__icontains=search)
    total = qs.count()
    courses = qs[(page - 1) * page_size: page * page_size]

    result = {
        "total": total,
        "page": page,
        "page_size": page_size,
        "results": [
            {
                "id": c.id,
                "title": c.title,
                "instructor": {
                    "id": c.instructor.id,
                    "username": c.instructor.username,
                    "email": c.instructor.email,
                    "role": c.instructor.role,
                },
                "category": {
                    "id": c.category.id,
                    "name": c.category.name,
                    "parent_id": c.category.parent_id,
                },
                "total_lessons": c.total_lessons,
            }
            for c in courses
        ],
    }

    cache.set(cache_key, result, CACHE_TTL)
    return result


@router.get("/{course_id}", response=CourseDetailSchema)
def get_course(request, course_id: int):
    # Rate limiting
    rate_limit(request.META.get("REMOTE_ADDR", "unknown"))

    # Cache
    cache_key = f"courses:detail:{course_id}"
    cached = cache.get(cache_key)
    if cached:
        return cached

    try:
        course = (
            Course.objects
            .select_related("instructor", "category")
            .prefetch_related("lesson_set")
            .get(id=course_id)
        )
    except Course.DoesNotExist:
        raise HttpError(404, "Course not found")

    result = serialize_detail(course)
    cache.set(cache_key, result, CACHE_TTL)
    return result


@router.post("", response={201: CourseDetailSchema})
def create_course(request, payload: CourseCreateSchema):
    try:
        instructor = User.objects.get(id=payload.instructor_id)
    except User.DoesNotExist:
        raise HttpError(404, "Instructor not found")
    try:
        category = Category.objects.get(id=payload.category_id)
    except Category.DoesNotExist:
        raise HttpError(404, "Category not found")

    course = Course.objects.create(
        title=payload.title,
        instructor=instructor,
        category=category,
    )

    # Invalidate cache list
    cache.delete_pattern("courses:list:*")

    course = (
        Course.objects
        .select_related("instructor", "category")
        .prefetch_related("lesson_set")
        .get(id=course.id)
    )
    return 201, serialize_detail(course)


@router.patch("/{course_id}", response=CourseDetailSchema)
def update_course(request, course_id: int, payload: CourseUpdateSchema):
    try:
        course = (
            Course.objects
            .select_related("instructor", "category")
            .prefetch_related("lesson_set")
            .get(id=course_id)
        )
    except Course.DoesNotExist:
        raise HttpError(404, "Course not found")

    if payload.title is not None:
        course.title = payload.title
    if payload.category_id is not None:
        try:
            course.category = Category.objects.get(id=payload.category_id)
        except Category.DoesNotExist:
            raise HttpError(404, "Category not found")
    course.save()

    # Invalidate cache
    cache.delete(f"courses:detail:{course_id}")
    cache.delete_pattern("courses:list:*")

    return serialize_detail(course)


@router.delete("/{course_id}", response=MessageSchema)
def delete_course(request, course_id: int):
    try:
        course = Course.objects.get(id=course_id)
    except Course.DoesNotExist:
        raise HttpError(404, "Course not found")

    title = course.title
    course.delete()

    # Invalidate cache
    cache.delete(f"courses:detail:{course_id}")
    cache.delete_pattern("courses:list:*")

    return {"message": f"Course '{title}' deleted successfully"}