from ninja import Schema
from pydantic import EmailStr, field_validator
from typing import Optional, List
from datetime import datetime

class RegisterSchema(Schema):
    username: str
    email: EmailStr
    password: str
    role: str = "student"

    @field_validator("role")
    @classmethod
    def validate_role(cls, v):
        if v not in ("admin", "instructor", "student"):
            raise ValueError("Role must be admin, instructor, or student")
        return v

class LoginSchema(Schema):
    username: str
    password: str

class TokenSchema(Schema):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"

class RefreshSchema(Schema):
    refresh_token: str

class UpdateProfileSchema(Schema):
    email: Optional[EmailStr] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    password: Optional[str] = None


class CategorySchema(Schema):
    id: int
    name: str
    parent_id: Optional[int] = None


class UserOutSchema(Schema):
    id: int
    username: str
    email: str
    role: str


class LessonOutSchema(Schema):
    id: int
    title: str
    order: int


class CourseCreateSchema(Schema):
    title: str
    category_id: int
    instructor_id: int


class CourseUpdateSchema(Schema):
    title: Optional[str] = None
    category_id: Optional[int] = None


class CourseListSchema(Schema):
    id: int
    title: str
    instructor: UserOutSchema
    category: CategorySchema
    total_lessons: int


class CourseDetailSchema(Schema):
    id: int
    title: str
    instructor: UserOutSchema
    category: CategorySchema
    lessons: List[LessonOutSchema]


class PaginatedCoursesSchema(Schema):
    total: int
    page: int
    page_size: int
    results: List[CourseListSchema]


class EnrollSchema(Schema):
    course_id: int
    student_id: int


class ProgressUpdateSchema(Schema):
    lesson_id: int
    student_id: int
    completed: bool = True


class ProgressOutSchema(Schema):
    lesson_id: int
    lesson_title: str
    completed: bool


class EnrolledCourseSchema(Schema):
    enrollment_id: int
    course: CourseListSchema
    enrolled_at: datetime
    progress: List[ProgressOutSchema]


class MessageSchema(Schema):
    message: str