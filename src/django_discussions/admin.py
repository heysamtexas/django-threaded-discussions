from django.contrib import admin
from django.db.models import QuerySet
from django.http import HttpRequest

from django_discussions.models import Comment, Thread


@admin.register(Thread)
class ThreadAdmin(admin.ModelAdmin):
    """Admin interface for the Thread model."""

    list_display = ("id", "title", "discussion_id", "author", "is_active", "created_at")
    search_fields = ("title", "content", "discussion_id")
    list_filter = ("is_active", "is_spam", "is_deleted", "created_at")
    ordering = ("-created_at",)
    readonly_fields = ("short_uuid", "created_at", "updated_at")

    fieldsets = (
        (
            "Basic Information",
            {
                "fields": ("discussion_id", "title", "content", "author", "short_uuid"),
            },
        ),
        (
            "Moderation",
            {
                "fields": (
                    "is_active",
                    "is_spam",
                    "is_deleted",
                    "is_locked",
                    "is_archived",
                    "is_edited",
                ),
            },
        ),
        (
            "Metadata",
            {
                "fields": ("weight_order", "created_at", "updated_at"),
            },
        ),
    )

    def get_queryset(self, request: HttpRequest) -> QuerySet:
        """Optimize queryset with select_related to avoid N+1 queries."""
        return super().get_queryset(request).select_related("author")


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    """Admin interface for the Comment model."""

    list_display = ("id", "thread", "author", "is_active", "created_at")
    search_fields = ("content",)
    list_filter = ("is_active", "is_spam", "is_pinned", "created_at")
    ordering = ("-created_at",)
    readonly_fields = ("short_uuid", "created_at", "updated_at")
    raw_id_fields = ("thread", "parent")

    fieldsets = (
        (
            "Basic Information",
            {
                "fields": ("thread", "content", "author", "parent", "short_uuid"),
            },
        ),
        (
            "Moderation",
            {
                "fields": (
                    "is_active",
                    "is_pinned",
                    "is_spam",
                    "is_deleted",
                    "is_locked",
                    "is_archived",
                    "is_edited",
                ),
            },
        ),
        (
            "Metadata",
            {
                "fields": ("weight_order", "created_at", "updated_at"),
            },
        ),
    )

    def get_queryset(self, request: HttpRequest) -> QuerySet:
        """Optimize queryset with select_related to avoid N+1 queries."""
        return super().get_queryset(request).select_related("thread", "author", "parent")
