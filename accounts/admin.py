from django.contrib import admin

from .models import EmailConfirmation


@admin.register(EmailConfirmation)
class EmailConfirmationAdmin(admin.ModelAdmin):
    list_display = ("user", "token", "created_at")
    search_fields = ("user__email",)
    readonly_fields = ("token", "created_at")
