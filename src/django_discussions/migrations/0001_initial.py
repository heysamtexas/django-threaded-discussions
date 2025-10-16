# Generated migration for django-discussions

import django.db.models.deletion
import shortuuid.django_fields
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="Thread",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("discussion_id", models.CharField(db_index=True, max_length=255)),
                ("title", models.CharField(max_length=255)),
                ("content", models.TextField(blank=True, default="")),
                ("weight_order", models.IntegerField(default=0)),
                ("is_active", models.BooleanField(default=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("is_deleted", models.BooleanField(default=False)),
                ("is_edited", models.BooleanField(default=False)),
                ("is_locked", models.BooleanField(default=False)),
                ("is_archived", models.BooleanField(default=False)),
                ("is_spam", models.BooleanField(default=False)),
                (
                    "short_uuid",
                    shortuuid.django_fields.ShortUUIDField(
                        alphabet=None, editable=False, length=22, max_length=22, prefix="", unique=True
                    ),
                ),
                (
                    "author",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="discussion_threads",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "ordering": ["-created_at"],
            },
        ),
        migrations.CreateModel(
            name="Comment",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("content", models.TextField()),
                ("weight_order", models.IntegerField(default=0)),
                ("is_active", models.BooleanField(default=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("is_deleted", models.BooleanField(default=False)),
                ("is_edited", models.BooleanField(default=False)),
                ("is_pinned", models.BooleanField(default=False)),
                ("is_locked", models.BooleanField(default=False)),
                ("is_archived", models.BooleanField(default=False)),
                ("is_spam", models.BooleanField(default=False)),
                (
                    "short_uuid",
                    shortuuid.django_fields.ShortUUIDField(
                        alphabet=None, editable=False, length=22, max_length=22, prefix="", unique=True
                    ),
                ),
                (
                    "author",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="discussion_comments",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                (
                    "parent",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="replies",
                        to="django_discussions.comment",
                    ),
                ),
                (
                    "thread",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="comments",
                        to="django_discussions.thread",
                    ),
                ),
            ],
            options={
                "ordering": ["created_at"],
            },
        ),
        migrations.AddIndex(
            model_name="thread",
            index=models.Index(fields=["discussion_id", "created_at"], name="django_disc_discuss_e0b0ad_idx"),
        ),
        migrations.AddIndex(
            model_name="thread",
            index=models.Index(fields=["discussion_id", "is_active"], name="django_disc_discuss_5c5d5d_idx"),
        ),
    ]
