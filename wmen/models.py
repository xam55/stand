from django.conf import settings
from django.db import models

from .file_storage import private_storage


# Create your models here.



class Women(models.Model):
    title = models.CharField(max_length=255)
    content = models.TextField(blank=True)
    time_create = models.DateTimeField(auto_now_add=True)
    time_update = models.DateTimeField(auto_now=True)
    is_published = models.BooleanField(default=True)
    photo = models.ImageField(upload_to="photos/%Y/%m/",blank=True,null=True)
    photo_raw = models.FileField(storage=private_storage, upload_to="uploads/%Y/%m/", blank=True, null=True)

    cat = models.ForeignKey(
        "Category",
        on_delete=models.PROTECT,
        null=True
    )


class Category(models.Model):
    name = models.CharField(max_length=100, db_index=True)

    def __str__(self):
        return self.name


class Report(models.Model):
    class Status(models.TextChoices):
        PENDING = "pending", "В очереди"
        RUNNING = "running", "Собирается"
        DONE = "done", "Готов"
        FAILED = "failed", "Ошибка"

    ACTIVE_STATUSES = (Status.PENDING, Status.RUNNING)

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="reports")
    status = models.CharField(max_length=20, choices=Status, default=Status.PENDING)
    file = models.FileField(storage=private_storage, upload_to="reports/%Y/%m/", blank=True)
    rows = models.PositiveIntegerField(default=0)
    error = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    finished_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["-created_at"]
        constraints = [
            models.UniqueConstraint(
                fields=["user"],
                condition=models.Q(status__in=["pending", "running"]),
                name="one_active_report_per_user",
            ),
        ]

    def __str__(self):
        return f"Отчёт #{self.pk} ({self.get_status_display()})"