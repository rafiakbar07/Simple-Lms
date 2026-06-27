from ninja import NinjaAPI
from lms.api_auth import router as auth_router
from lms.api_courses import router as courses_router
from lms.api_enrollments import router as enrollments_router
from lms.api_analytics import router as analytics_router
from lms.api_health import router as health_router
from lms.api_cache import router as cache_router
from lms.api_export import router as export_router

api = NinjaAPI(
    title="Simple LMS API",
    version="1.0.0",
    description="REST API untuk Simple LMS menggunakan Django Ninja",
    docs_url="/docs",
)

api.add_router("/auth/", auth_router)
api.add_router("/courses/", courses_router)
api.add_router("/enrollments/", enrollments_router)
api.add_router("/analytics/", analytics_router)
api.add_router("/", health_router)
api.add_router("/cache/", cache_router)
api.add_router("/export/", export_router)