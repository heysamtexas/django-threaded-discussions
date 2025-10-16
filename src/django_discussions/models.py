from django.contrib.auth.models import User
from django.db import models
from django.utils import timezone
from django.utils.timesince import timesince
from shortuuid.django_fields import ShortUUIDField

"""
Django Discussions - Threaded discussion system for any Django model.

This app provides threaded discussions that can be attached to any content
using a simple discussion_id identifier (UUID, slug, or any unique string).

There is the Thread model and Comment model.

The thread model is bound to a discussion_id (provided by the parent object).
Threads have the following:
- title field that is used to display the thread.
- content field that is used to display the thread.
- discussion_id field that links to the parent object.
- author (user) field that is used to display the thread.
- weight_order field that is used to order the threads.
- is_active field that is used to hide threads.
- created_at field that is used to order the threads.
- updated_at field that is used to order the threads.
- is_deleted field that is used to hide threads.
- is_edited field that is used to hide threads.
- is_locked field that is used to hide threads.
- is_archived field that is used to hide threads.
- is_spam field that is used to hide threads.

The comment model is bound to a thread, and has a text field, and a user field.
- comments are threaded, so they have a parent field that points to the parent comment.
Comments have the following:
- weight_order field that is used to order the comments in the thread.
- is_active field that is used to hide comments.
- created_at field that is used to order the comments in the thread.
- updated_at field that is used to order the comments in the thread.
- is_deleted field that is used to hide comments.
- is_edited field that is used to hide comments.
- is_locked field that is used to hide comments.
- is_archived field that is used to hide comments.
- is_spam field that is used to hide comments.
- is_deleted field that is used to hide comments.
"""


class Thread(models.Model):
    """Thread model for discussions."""

    # Link to parent object via discussion_id (UUID, slug, etc.)
    discussion_id = models.CharField(max_length=255, db_index=True)

    title = models.CharField(max_length=255)
    content = models.TextField(blank=True, default="")
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name="discussion_threads")
    weight_order = models.IntegerField(default=0)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_deleted = models.BooleanField(default=False)
    is_edited = models.BooleanField(default=False)
    is_locked = models.BooleanField(default=False)
    is_archived = models.BooleanField(default=False)
    is_spam = models.BooleanField(default=False)
    short_uuid = ShortUUIDField(unique=True, editable=False)

    class Meta:
        indexes = [
            models.Index(fields=["discussion_id", "created_at"]),
            models.Index(fields=["discussion_id", "is_active"]),
        ]
        ordering = ["-created_at"]

    def __str__(self) -> str:
        """Return the string representation of the thread."""
        return self.title

    @property
    def comment_count(self) -> int:
        """Return the number of comments in the thread."""
        return self.comments.count()

    @property
    def time_ago(self) -> str:
        """Return the time ago the thread was created in humanized format (eg. 2 days ago)."""
        t = timesince(self.created_at, timezone.now())
        return f"{t} ago"

    @property
    def should_render_for_seo(self) -> bool:
        """Determine if thread should be server-rendered for SEO."""
        return (
            self.is_active
            and not self.is_spam
            and not self.is_deleted
            and len(self.title) >= 10
            and self.comment_count > 0
        )

    @classmethod
    def get_seo_threads(cls, discussion_id: str, max_count: int = 10):
        """Get SEO-worthy threads for a discussion."""
        return cls.objects.filter(
            discussion_id=discussion_id, is_active=True, is_spam=False, is_deleted=False
        ).order_by("-created_at")[:max_count]


class Comment(models.Model):
    """Comment model for discussions."""

    content = models.TextField()
    thread = models.ForeignKey(Thread, on_delete=models.CASCADE, related_name="comments")
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name="discussion_comments")
    parent = models.ForeignKey("self", on_delete=models.CASCADE, blank=True, null=True, related_name="replies")
    weight_order = models.IntegerField(default=0)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_deleted = models.BooleanField(default=False)
    is_edited = models.BooleanField(default=False)
    is_pinned = models.BooleanField(default=False)
    is_locked = models.BooleanField(default=False)
    is_archived = models.BooleanField(default=False)
    is_spam = models.BooleanField(default=False)
    short_uuid = ShortUUIDField(unique=True, editable=False)

    class Meta:
        ordering = ["created_at"]

    def __str__(self) -> str:
        """Return the string representation of the comment."""
        return self.content[:50]

    @property
    def time_ago(self) -> str:
        """Return the time ago the comment was created in humanized format (eg. 2 days ago)."""
        t = timesince(self.created_at, timezone.now())
        return f"{t} ago"
