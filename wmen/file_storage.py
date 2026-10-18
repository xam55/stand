from functools import cache

from django.conf import settings
from django.core.files.storage import storages
from storages.backends.s3 import S3Storage


def private_storage():
    return storages["private"]


def private_file_url(name: str) -> str:
    return _signing_storage().url(name)


@cache
def _signing_storage() -> S3Storage:
    options = {**settings.STORAGES["private"]["OPTIONS"], "endpoint_url": settings.S3_PUBLIC_ENDPOINT_URL}
    return S3Storage(**options)
