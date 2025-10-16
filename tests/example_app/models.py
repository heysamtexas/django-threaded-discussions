import uuid

from django.db import models


class BlogPost(models.Model):
    """Example model: Blog post with UUID for discussions."""

    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=True)
    content = models.TextField()
    uuid = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

    @property
    def discussion_id(self):
        """Return UUID as discussion identifier."""
        return str(self.uuid)


class Product(models.Model):
    """Example model: Product with slug for discussions."""

    name = models.CharField(max_length=200)
    slug = models.SlugField(unique=True)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

    @property
    def discussion_id(self):
        """Return slug as discussion identifier."""
        return self.slug
