from ninja import Router
from ninja.errors import HttpError
from django.contrib.auth.hashers import make_password, check_password
from lms.models import User
from lms.schemas import (
    RegisterSchema, LoginSchema, TokenSchema,
    RefreshSchema, UserOutSchema, UpdateProfileSchema
)
from lms.auth import create_access_token, create_refresh_token, decode_token, jwt_auth

router = Router(tags=["Authentication"])


@router.post("/register", response={201: UserOutSchema}, auth=None)
def register(request, payload: RegisterSchema):
    """Register user baru."""
    if User.objects.filter(username=payload.username).exists():
        raise HttpError(400, "Username already exists")
    if User.objects.filter(email=payload.email).exists():
        raise HttpError(400, "Email already registered")
    user = User.objects.create(
        username=payload.username,
        email=payload.email,
        password=make_password(payload.password),
        role=payload.role,
    )
    return 201, user


@router.post("/login", response=TokenSchema, auth=None)
def login(request, payload: LoginSchema):
    """Login dan dapat JWT token."""
    try:
        user = User.objects.get(username=payload.username)
    except User.DoesNotExist:
        raise HttpError(401, "Invalid credentials")
    if not check_password(payload.password, user.password):
        raise HttpError(401, "Invalid credentials")
    return TokenSchema(
        access_token=create_access_token(user.id),
        refresh_token=create_refresh_token(user.id),
    )


@router.post("/refresh", response=TokenSchema, auth=None)
def refresh_token(request, payload: RefreshSchema):
    """Refresh access token."""
    decoded = decode_token(payload.refresh_token)
    if decoded.get("type") != "refresh":
        raise HttpError(401, "Invalid refresh token")
    try:
        user = User.objects.get(id=decoded["user_id"])
    except User.DoesNotExist:
        raise HttpError(401, "User not found")
    return TokenSchema(
        access_token=create_access_token(user.id),
        refresh_token=create_refresh_token(user.id),
    )


@router.get("/me", response=UserOutSchema, auth=jwt_auth)
def get_me(request):
    """Get current user."""
    return request.auth


@router.put("/me", response=UserOutSchema, auth=jwt_auth)
def update_me(request, payload: UpdateProfileSchema):
    """Update profil user."""
    user = request.auth
    if payload.email:
        if User.objects.filter(email=payload.email).exclude(id=user.id).exists():
            raise HttpError(400, "Email already in use")
        user.email = payload.email
    if payload.first_name is not None:
        user.first_name = payload.first_name
    if payload.last_name is not None:
        user.last_name = payload.last_name
    if payload.password:
        user.password = make_password(payload.password)
    user.save()
    return user