from django.contrib import admin

from .models import Category, Report, Women

admin.site.register(Women)
admin.site.register(Category)


@admin.register(Report)
class ReportAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "status", "rows", "created_at", "finished_at")
    list_filter = ("status",)
    readonly_fields = ("file", "rows", "error", "created_at", "finished_at")
