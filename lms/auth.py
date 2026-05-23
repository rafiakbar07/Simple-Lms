import jwt
from datetime import datetime, timedelta, timezone
from django.conf import settings
from ninja.security import HttpBearer
from ninja.errors import HttpError
from lms.models import User

ACCESS_TOKEN_EXPIRE_MINUTES = 60
REFRESH_TOKEN_EXPIRE_DAYS = 7
ALGORITHM = "HS256"


def create_access_token(user_id: int) -> str:
    payload = {
        "user_id": user_id,
        "type": "access",
        "exp": datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES),
        "iat": datetime.now(timezone.utc),
    }
    return jwt.encode(payload, settings.SECRET_KEY, algorithm=ALGORITHM)


def create_refresh_token(user_id: int) -> str:
    payload = {
        "user_id": user_id,
        "type": "refresh",
        "exp": datetime.now(timezone.utc) + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS),
        "iat": datetime.now(timezone.utc),
    }
    return jwt.encode(payload, settings.SECRET_KEY, algorithm=ALGORITHM)


def decode_token(token: str) -> dict:
    try:
        return jwt.decode(token, settings.SECRET_KEY, algorithms=[ALGORITHM])
    except jwt.ExpiredSignatureError:
        raise HttpError(401, "Token has expired")
    except jwt.InvalidTokenError:
        raise HttpError(401, "Invalid token")


def get_user_from_token(token: str) -> User:
    payload = decode_token(token)
    if payload.get("type") != "access":
        raise HttpError(401, "Invalid token type")
    try:
        return User.objects.get(id=payload["user_id"])
    except User.DoesNotExist:
        raise HttpError(401, "User not found")


class JWTAuth(HttpBearer):
    def authenticate(self, request, token: str):
        try:
            user = get_user_from_token(token)
            request.user = user
            return user
        except HttpError:
            return None

jwt_auth = JWTAuth()


# ===== ROLE DECORATORS =====

def require_role(*roles):
    def decorator(func):
        def wrapper(request, *args, **kwargs):
            user = request.auth
            if user is None:
                raise HttpError(401, "Authentication required")
            if user.role not in roles:
                raise HttpError(403, f"Access denied. Required: {', '.join(roles)}")
            return func(request, *args, **kwargs)
        wrapper.__name__ = func.__name__
        wrapper.__doc__ = func.__doc__
        return wrapper
    return decorator

def is_instructor(func):
    return require_role("instructor", "admin")(func)

def is_admin(func):
    return require_role("admin")(func)

def is_student(func):
    return require_role("student", "admin")(func)