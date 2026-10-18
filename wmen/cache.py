from collections.abc import Callable

from django.core.cache import cache

WOMEN_LIST_VERSION_KEY = "women:list:version"
WOMEN_LIST_TTL = 300


def get_or_set_women_page(page: int, build: Callable[[], dict]) -> dict:
    key = f"women:list:v{_list_version()}:page:{page}"
    data = cache.get(key)
    if data is None:
        data = build()
        cache.set(key, data, WOMEN_LIST_TTL)
    return data


def invalidate_women_list() -> None:
    try:
        cache.incr(WOMEN_LIST_VERSION_KEY)
    except ValueError:
        cache.set(WOMEN_LIST_VERSION_KEY, 1, timeout=None)


def _list_version() -> int:
    return cache.get_or_set(WOMEN_LIST_VERSION_KEY, 1, timeout=None)
