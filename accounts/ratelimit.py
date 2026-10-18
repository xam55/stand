from django.core.cache import cache


def is_allowed(key: str, *, limit: int, period: int) -> bool:
    cache_key = f"ratelimit:{key}"
    cache.add(cache_key, 0, timeout=period)
    try:
        count = cache.incr(cache_key)
    except ValueError:
        cache.set(cache_key, 1, timeout=period)
        count = 1
    return count <= limit


def client_ip(request) -> str:
    return request.META.get("HTTP_X_REAL_IP") or request.META.get("REMOTE_ADDR", "")
