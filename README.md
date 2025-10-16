# Django Threaded Discussions

A standalone Django app for threaded discussions with HTMX support. Attach discussions to any model using a simple UUID identifier pattern.

## Features

- **Zero Coupling**: Attach discussions to any model without modifying it
- **UUID-Based**: Use any unique identifier (UUID, slug, ShortUUID, etc.)
- **HTMX Ready**: Built-in HTMX templates for dynamic interactions
- **SEO Friendly**: Server-side rendering support with structured data helpers
- **Threaded Comments**: Nested comment replies with parent/child relationships
- **User Permissions**: Built-in authentication and ownership checks
- **Spam Protection**: Flags for spam detection and moderation
- **Lightweight**: Minimal dependencies, maximum flexibility

## Installation

### From PyPI (when published)

```bash
pip install django-threaded-discussions
```

### From Source (Development)

```bash
# In your workspace directory
git clone https://github.com/directory-platform/django-threaded-discussions.git
cd django-threaded-discussions
pip install -e .
```

### UV Workspace (Recommended for development)

Add to your workspace `pyproject.toml`:

```toml
[tool.uv.workspace]
members = [
    "your-project",
    "django-threaded-discussions",
]
```

Then run:

```bash
uv sync
```

## Quick Start

### 1. Add to Django Settings

```python
# settings.py
INSTALLED_APPS = [
    # ...
    "django_discussions",
]
```

### 2. Run Migrations

```python
python manage.py migrate django_discussions
```

### 3. Include URLs

```python
# urls.py
urlpatterns = [
    # ...
    path("discussions/", include("django_discussions.urls")),
]
```

### 4. Add to Your Templates

```django
<!-- blog_post_detail.html -->
<div class="discussion-section">
    <!-- HTMX lazy-load discussions -->
    <div hx-get="/discussions/{{ blog_post.uuid }}/"
         hx-trigger="load">
        Loading discussions...
    </div>
</div>

<!-- Or server-render for SEO -->
{% load discussion_tags %}
{% render_discussions_seo discussion_id=blog_post.uuid %}
```

That's it! No changes to your models required.

## How It Works

Django Threaded Discussions uses a simple `discussion_id` string field to link threads to your content. This means:

- ✅ No ForeignKeys to your models
- ✅ No GenericForeignKey complexity
- ✅ No migrations when adding new model types
- ✅ Works with any unique identifier you already have

## Usage Examples

### With UUID Field

```python
class BlogPost(models.Model):
    uuid = models.UUIDField(default=uuid.uuid4, unique=True)
    # ... other fields
```

```django
<div hx-get="/discussions/{{ blog_post.uuid }}/">...</div>
```

### With Slug Field

```python
class Article(models.Model):
    slug = models.SlugField(unique=True)
    # ... other fields
```

```django
<div hx-get="/discussions/{{ article.slug }}/">...</div>
```

### With ShortUUID

```python
from shortuuid.django_fields import ShortUUIDField

class Product(models.Model):
    short_id = ShortUUIDField(unique=True)
    # ... other fields
```

```django
<div hx-get="/discussions/{{ product.short_id }}/">...</div>
```

### With Custom Identifier

```python
class Entity(models.Model):
    id = models.AutoField(primary_key=True)

    @property
    def discussion_id(self):
        return f"entity-{self.id}"
```

```django
<div hx-get="/discussions/{{ entity.discussion_id }}/">...</div>
```

## Authentication & Permissions

Discussions integrate seamlessly with Django's auth system:

**Public Views (No Login Required):**
- View discussion threads
- View comments
- See thread counts

**Authenticated Views (`@login_required`):**
- Create new threads
- Post comments
- Reply to comments

**Ownership Checks:**
- Delete own threads/comments
- Superusers can delete any content

```python
# Automatically enforced
@login_required
def create_thread(request, discussion_id):
    thread = Thread.objects.create(
        discussion_id=discussion_id,
        author=request.user,  # ← Django's auth
        # ...
    )
```

## SEO Optimization

### Server-Side Rendering

Render discussions on first page load for SEO:

```python
# views.py
from django_discussions.models import Thread

def blog_post_detail(request, slug):
    post = get_object_or_404(BlogPost, slug=slug)

    # Get SEO-worthy threads
    seo_threads = Thread.get_seo_threads(
        discussion_id=str(post.uuid),
        max_count=5
    )

    context = {
        'post': post,
        'seo_threads': seo_threads,
    }
    return render(request, 'blog_detail.html', context)
```

```django
<!-- blog_detail.html -->
<div id="discussions">
    <!-- Server-rendered for SEO -->
    {% for thread in seo_threads %}
        {% include "django_discussions/_thread.html" %}
    {% endfor %}

    <!-- HTMX load more -->
    <div hx-get="/discussions/{{ post.uuid }}/?offset=5">
        Load more...
    </div>
</div>
```

### Structured Data

Add schema.org markup for rich snippets:

```django
{% load discussion_tags %}
{% discussion_structured_data discussion_id=post.uuid %}
```

Generates:

```json
{
  "@context": "https://schema.org",
  "@type": "DiscussionForumPosting",
  "headline": "Thread title",
  "commentCount": 42,
  // ... etc
}
```

## Template Tags

```django
{% load discussion_tags %}

<!-- Render SEO-optimized discussions -->
{% render_discussions_seo discussion_id="abc-123" max_threads=10 %}

<!-- Get thread count -->
{% thread_count discussion_id="abc-123" %}

<!-- Structured data for SEO -->
{% discussion_structured_data discussion_id="abc-123" %}
```

## Models

### Thread

```python
class Thread(models.Model):
    discussion_id = CharField(max_length=255)  # Your unique identifier
    title = CharField(max_length=255)
    content = TextField()
    author = ForeignKey(User)
    short_uuid = ShortUUIDField(unique=True)

    # Moderation flags
    is_active = BooleanField(default=True)
    is_spam = BooleanField(default=False)
    is_deleted = BooleanField(default=False)
    is_locked = BooleanField(default=False)

    # Timestamps
    created_at = DateTimeField(auto_now_add=True)
    updated_at = DateTimeField(auto_now=True)
```

### Comment

```python
class Comment(models.Model):
    thread = ForeignKey(Thread)
    content = TextField()
    author = ForeignKey(User)
    parent = ForeignKey('self', null=True)  # Threaded replies
    short_uuid = ShortUUIDField(unique=True)

    # Moderation flags
    is_active = BooleanField(default=True)
    is_pinned = BooleanField(default=False)
    is_spam = BooleanField(default=False)

    # Timestamps
    created_at = DateTimeField(auto_now_add=True)
    updated_at = DateTimeField(auto_now=True)
```

## Customization

### Settings

```python
# settings.py
DISCUSSIONS_SETTINGS = {
    'MAX_THREADS_PER_PAGE': 20,
    'MAX_COMMENTS_PER_THREAD': 100,
    'ALLOW_ANONYMOUS_VIEWING': True,
    'MIN_TITLE_LENGTH': 3,
    'MAX_TITLE_LENGTH': 100,
}
```

### Custom Templates

Override any template by creating `templates/django_discussions/` in your project:

```
your_project/
  templates/
    django_discussions/
      index.html              # Override thread list
      _thread_header.html     # Override thread display
      _comment.html           # Override comment display
```

### Admin Interface

Discussions are registered in Django admin with search and filtering:

```python
# Automatic admin registration
# Access at /admin/django_discussions/thread/
# Access at /admin/django_discussions/comment/
```

## Development

### Setup

```bash
git clone https://github.com/directory-platform/django-threaded-discussions.git
cd django-threaded-discussions
uv sync --extra dev
```

### Running Tests

```bash
make test
# or
PYTHONPATH=. uv run python tests/manage.py test
```

### Code Quality

```bash
make lint          # Ruff linting
make format        # Auto-format
make typecheck     # Mypy type checking
make check         # All checks + tests
```

## Requirements

- Python 3.12+
- Django 4.2+
- shortuuid 1.0+

## Contributing

Contributions welcome! Please:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

MIT License - see LICENSE file for details.

## Credits

Built by the Directory Platform team as part of the directory ecosystem.

## Links

- **Documentation**: [Coming soon]
- **GitHub**: https://github.com/directory-platform/django-threaded-discussions
- **Issues**: https://github.com/directory-platform/django-threaded-discussions/issues
- **PyPI**: https://pypi.org/project/django-threaded-discussions/ (after first release)
