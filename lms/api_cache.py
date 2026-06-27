from ninja import Router
from django.core.cache import cache
from ninja.errors import HttpError

router = Router(tags=["Cache Monitoring"])


def get_redis_client():
    """Ambil raw Redis client dari django-redis."""
    return cache.client.get_client(write=True)


@router.get("/keys", response=dict)
def list_cache_keys(request, pattern: str = "*"):
    """
    List semua cache keys yang sesuai pattern.
    Default pattern '*' menampilkan semua keys.
    """
    try:
        redis_client = get_redis_client()
        keys = redis_client.keys(f"*{pattern}*")

        result = []
        for key in keys[:100]:
            key_str = key.decode("utf-8") if isinstance(key, bytes) else key
            ttl = redis_client.ttl(key)
            result.append({
                "key": key_str,
                "ttl_seconds": ttl,
            })

        return {
            "pattern": pattern,
            "total_keys": len(result),
            "keys": result,
        }
    except Exception as e:
        raise HttpError(500, f"Failed to list cache keys: {str(e)}")


@router.get("/stats", response=dict)
def cache_stats(request):
    """
    Statistik Redis: jumlah keys, memory usage, hit/miss info.
    """
    try:
        redis_client = get_redis_client()
        info = redis_client.info()

        return {
            "total_keys": redis_client.dbsize(),
            "used_memory": info.get("used_memory_human", "N/A"),
            "connected_clients": info.get("connected_clients", 0),
            "keyspace_hits": info.get("keyspace_hits", 0),
            "keyspace_misses": info.get("keyspace_misses", 0),
            "hit_rate": _calculate_hit_rate(
                info.get("keyspace_hits", 0),
                info.get("keyspace_misses", 0)
            ),
            "uptime_seconds": info.get("uptime_in_seconds", 0),
        }
    except Exception as e:
        raise HttpError(500, f"Failed to get cache stats: {str(e)}")


@router.get("/check/{key}", response=dict)
def check_cache_key(request, key: str):
    """
    Cek apakah sebuah key ada di cache, beserta TTL-nya.
    """
    value = cache.get(key)
    exists = value is not None

    result = {
        "key": key,
        "exists": exists,
    }

    if exists:
        redis_client = get_redis_client()
        full_keys = redis_client.keys(f"*{key}*")
        if full_keys:
            ttl = redis_client.ttl(full_keys[0])
            result["ttl_seconds"] = ttl

    return result


@router.delete("/clear", response=dict)
def clear_cache(request, pattern: str = None):
    """
    Hapus cache. Jika pattern diberikan, hanya hapus key yang cocok.
    Jika tidak, hapus SEMUA cache (hati-hati!).
    """
    try:
        redis_client = get_redis_client()

        if pattern:
            keys = redis_client.keys(f"*{pattern}*")
            if keys:
                redis_client.delete(*keys)
            return {"message": f"Deleted {len(keys)} keys matching '{pattern}'"}
        else:
            cache.clear()
            return {"message": "All cache cleared"}
    except Exception as e:
        raise HttpError(500, f"Failed to clear cache: {str(e)}")


def _calculate_hit_rate(hits: int, misses: int) -> str:
    total = hits + misses
    if total == 0:
        return "N/A"
    rate = (hits / total) * 100
    return f"{rate:.2f}%"