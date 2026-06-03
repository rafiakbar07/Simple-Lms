from django.core.cache import cache
from ninja.errors import HttpError


def rate_limit(key: str, limit: int = 60, window: int = 60):
    """
    Rate limiter: max 60 requests per 60 detik.
    key: identifier unik (IP address)
    """
    cache_key = f"rate_limit:{key}"
    count = cache.get(cache_key, 0)

    if count >= limit:
        raise HttpError(429, f"Too many requests. Limit: {limit} per {window} seconds.")

    if count == 0:
        cache.set(cache_key, 1, timeout=window)
    else:
        cache.incr(cache_key)