from django.apps import AppConfig


class WmenConfig(AppConfig):
    name = 'wmen'

    def ready(self):
        from . import signals  # noqa: F401
