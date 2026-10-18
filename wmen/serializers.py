from rest_framework import serializers

from .file_storage import private_file_url
from .models import Report

MAX_PHOTO_SIZE = 10 * 1024 * 1024


class WomenSerializer(serializers.Serializer):
    title = serializers.CharField(max_length=255)
    content = serializers.CharField()
    time_create = serializers.DateTimeField(read_only=True)
    time_update = serializers.DateTimeField(read_only=True)
    is_published = serializers.BooleanField(default=True)
    photo = serializers.ImageField(required=False, allow_null=True)
    cat_id = serializers.IntegerField()

    def validate_photo(self, photo):
        if photo and photo.size > MAX_PHOTO_SIZE:
            raise serializers.ValidationError("Фото должно быть не больше 10 МБ.")
        return photo


class ReportSerializer(serializers.ModelSerializer):
    download_url = serializers.SerializerMethodField()

    class Meta:
        model = Report
        fields = ("id", "status", "rows", "error", "created_at", "finished_at", "download_url")

    def get_download_url(self, report) -> str | None:
        if report.status != Report.Status.DONE or not report.file:
            return None
        return private_file_url(report.file.name)
