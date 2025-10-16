# CLAUDE.md - Django Discussions Package

This file provides guidance to Claude Code when working with the `django-discussions` package.

## Project Overview

**Django Discussions** is a standalone Django package providing threaded discussions that can be attached to any model using a simple UUID/slug identifier pattern. No ForeignKeys, no GenericForeignKey complexity - just a string identifier.

**Key Features**:
- Zero coupling to parent models
- UUID-based attachment (works with any unique identifier)
- HTMX-ready templates for dynamic interactions
- SEO-friendly with server-side rendering support
- Threaded comment replies
- Built-in moderation flags
- Template tags for easy integration

## Package Structure

```
django-discussions/
├── src/django_discussions/
│   ├── __init__.py              # Package initialization
│   ├── apps.py                  # Django app configuration
│   ├── models.py                # Thread and Comment models
│   ├── views.py                 # HTMX views (discussion_id based)
│   ├── urls.py                  # URL patterns
│   ├── admin.py                 # Django admin interface
│   ├── templates/django_discussions/  # 9 HTMX templates
│   ├── static/django_discussions/     # CSS files
│   ├── templatetags/
│   │   └── discussion_tags.py   # SEO template tags
│   ├── management/
│   │   └── commands/
│   └── migrations/
│       └── 0001_initial.py
├── tests/                       # Test suite
│   ├── settings.py              # Test Django configuration
│   ├── manage.py                # Django test runner
│   ├── example_app/             # Example models
│   └── test_models.py           # Model tests
├── pyproject.toml               # Package configuration
├── README.md                    # User documentation
├── LICENSE                      # MIT License
├── Makefile                     # Development commands
└── CLAUDE.md                    # This file
```

## Core Architecture

### The UUID Pattern (No Coupling!)

Unlike traditional discussion systems that use ForeignKeys or GenericForeignKeys, this package uses a simple string identifier pattern:

```python
# Thread model - just stores a string
class Thread(models.Model):
    discussion_id = CharField(max_length=255, db_index=True)  # That's it!
    # ... other fields
```

**Parent models don't need ANY changes:**

```python
# User's model (no changes required!)
class BlogPost(models.Model):
    uuid = models.UUIDField(default=uuid.uuid4)
    # ... rest of model

# In template:
# <div hx-get="/discussions/{{ blog_post.uuid }}/">...</div>
```

**Key benefits:**
- No migrations when adding discussions to new models
- No database relationships = no orphan issues
- Works with ANY unique identifier (UUID, slug, ShortUUID, composite IDs)
- Package is completely agnostic to parent models

### Models

**Thread (121 lines in models.py:48-168)**
```python
class Thread(models.Model):
    discussion_id = CharField(max_length=255, db_index=True)  # Links to parent
    title = CharField(max_length=255)
    content = TextField()
    author = ForeignKey(User)
    short_uuid = ShortUUIDField(unique=True)

    # Moderation flags
    is_active, is_spam, is_deleted, is_locked, is_archived, is_edited

    # SEO helpers
    @property
    def should_render_for_seo(self) -> bool

    @classmethod
    def get_seo_threads(cls, discussion_id, max_count=10)
```

**Comment (56 lines in models.py:113-168)**
```python
class Comment(models.Model):
    thread = ForeignKey(Thread)
    content = TextField()
    author = ForeignKey(User)
    parent = ForeignKey('self', null=True)  # Threaded replies
    short_uuid = ShortUUIDField(unique=True)

    # Moderation flags
    is_active, is_pinned, is_spam, is_deleted, is_locked, is_archived, is_edited
```

### Views (Discussion ID Based)

All views accept `discussion_id` as a string parameter:

```python
def index(request, discussion_id: str)
def create_thread(request, discussion_id: str)  # @login_required
def create_comment(request, thread_short_uuid: str)  # @login_required
def delete_thread(request, short_uuid: str)  # @login_required
def delete_comment(request, short_uuid: str)  # @login_required
```

**URL patterns:**
```
/discussions/<discussion_id>/                    # List threads
/discussions/<discussion_id>/create/             # Create thread
/discussions/thread/<short_uuid>/                # Thread detail
/discussions/comment/<short_uuid>/create/        # Create comment
/discussions/thread/<short_uuid>/delete/         # Delete thread
/discussions/comment/<short_uuid>/delete/        # Delete comment
```

### Templates (9 HTMX Templates)

All templates use HTMX for dynamic interactions:

1. **index.html** - Main discussion list with "New Thread" button
2. **_thread_header.html** - Thread preview in list
3. **_thread_detail.html** - Full thread with comments
4. **_thread_form.html** - Create thread form
5. **_comment.html** - Single comment display
6. **_comments_section.html** - All comments for thread
7. **_comment_form.html** - Create comment form
8. **thread_detail.html** - Standalone thread page
9. **create_comment.html** - Standalone comment form

**Template namespace:** `django_discussions/`

### SEO Template Tags

**Three template tags** in `templatetags/discussion_tags.py`:

```django
{% load discussion_tags %}

<!-- Server-render discussions for SEO -->
{% render_discussions_seo discussion_id=blog_post.uuid max_threads=10 %}

<!-- Get thread count -->
{% thread_count discussion_id=blog_post.uuid %}

<!-- Add structured data (schema.org JSON-LD) -->
{% discussion_structured_data discussion_id=blog_post.uuid %}
```

## Development Setup

This package is part of the Directory Platform workspace:

```bash
# From workspace root
cd django-discussions
uv sync --extra dev

# Run tests
make test
# or
PYTHONPATH=. uv run python tests/manage.py test

# Code quality
make format lint typecheck
```

## Critical Constraints

### NEVER Do These

- ❌ Add ForeignKeys to external models
- ❌ Import models from parent projects (entities, categories, etc.)
- ❌ Use GenericForeignKey or ContentType
- ❌ Require parent models to have specific fields
- ❌ Make assumptions about discussion_id format

### ALWAYS Do These

- ✅ Treat `discussion_id` as an opaque string
- ✅ Use `discussion_id` for all lookups and filtering
- ✅ Keep package completely standalone
- ✅ Provide SEO helpers (not requirements)
- ✅ Test with multiple identifier types (UUID, slug, custom)

## Common Commands

```bash
# Run tests
make test
PYTHONPATH=. uv run python tests/manage.py test

# Code quality
make lint
make format
make typecheck
make check  # All checks + tests

# Development
uv sync --extra dev
```

## Integration Examples

### Example 1: UUID-based

```python
# User's model
class Article(models.Model):
    uuid = models.UUIDField(default=uuid.uuid4)

# Template
<div hx-get="/discussions/{{ article.uuid }}/">...</div>
```

### Example 2: Slug-based

```python
# User's model
class Category(models.Model):
    slug = models.SlugField(unique=True)

# Template
<div hx-get="/discussions/{{ category.slug }}/">...</div>
```

### Example 3: Custom ID

```python
# User's model
class Product(models.Model):
    id = models.AutoField(primary_key=True)

    @property
    def discussion_id(self):
        return f"product-{self.id}"

# Template
<div hx-get="/discussions/{{ product.discussion_id }}/">...</div>
```

## Testing

### Example Models (tests/example_app/models.py)

Two example models demonstrate different identifier patterns:

**BlogPost** - Uses UUID:
```python
class BlogPost(models.Model):
    uuid = models.UUIDField(default=uuid.uuid4)

    @property
    def discussion_id(self):
        return str(self.uuid)
```

**Product** - Uses slug:
```python
class Product(models.Model):
    slug = models.SlugField(unique=True)

    @property
    def discussion_id(self):
        return self.slug
```

### Running Tests

```bash
# All tests
make test

# Specific test
PYTHONPATH=. uv run python tests/manage.py test tests.test_models.ThreadModelTest

# Verbose
make test-verbose
```

## Architecture Decisions

### Why UUID Pattern vs GenericForeignKey?

**GenericForeignKey approach:**
- Requires ContentType lookups
- Complex queries and joins
- Orphan cleanup via signals
- Tight coupling to Django models
- 2 database fields (content_type + object_id)

**UUID pattern approach:**
- Simple string matching
- Direct index lookups
- No orphan issues (discussions exist independently)
- Works with ANY system (even external APIs)
- 1 database field (discussion_id)

**Decision:** UUID pattern wins on simplicity and flexibility.

### Why No Cleanup/Migration Helpers?

**Philosophy:** Discussions are independent content. If a blog post is deleted, the discussions about it can remain as historical record (like Reddit's `[deleted]` posts).

**User options:**
1. Keep orphaned discussions (default - storage is cheap)
2. Implement cleanup in their own project
3. Use soft deletes on parent models

## Extension Points

### Custom Settings

```python
# settings.py (user's project)
DISCUSSIONS_SETTINGS = {
    'MAX_THREADS_PER_PAGE': 20,
    'MAX_COMMENTS_PER_THREAD': 100,
    'MIN_TITLE_LENGTH': 3,
    'MAX_TITLE_LENGTH': 100,
}
```

### Template Overrides

Users can override any template:

```
their_project/
  templates/
    django_discussions/
      index.html              # Override thread list
      _comment.html           # Override comment display
```

### Admin Customization

Models are auto-registered in admin with search/filtering. Users can unregister and customize if needed.

## Dependencies

**Runtime:**
- Django 4.2+
- shortuuid 1.0+

**Development:**
- ruff (linting/formatting)
- mypy (type checking)
- django-stubs
- faker (test data generation)

## Comparison to django-seo-audit

Both packages follow similar architecture:

| Aspect | django-seo-audit | django-discussions |
|--------|------------------|-------------------|
| **Pattern** | Protocol-based mixin | UUID-based attachment |
| **Coupling** | Requires mixin on model | Zero coupling |
| **Discovery** | Auto-discovers auditable models | Works with any identifier |
| **Integration** | Add mixin to model | Pass UUID to template |
| **Use case** | SEO audit framework | Discussion threads |

## Publishing to PyPI

Similar process to django-seo-audit:

1. Update version in `pyproject.toml` and `__init__.py`
2. Run quality checks: `make check`
3. Commit version bump
4. Create GitHub release with tag matching version
5. GitHub Actions workflow publishes to PyPI automatically

See django-seo-audit/CLAUDE.md for detailed publishing instructions.

## Troubleshooting

**Tests failing:**
```bash
# Check Django setup
PYTHONPATH=. uv run python tests/manage.py check

# Run migrations
PYTHONPATH=. uv run python tests/manage.py migrate
```

**Template not found:**
- Check INSTALLED_APPS includes "django_discussions"
- Verify APP_DIRS = True in TEMPLATES setting

**HTMX not working:**
- Ensure HTMX library is loaded in parent project
- Check browser console for errors
- Verify URLs are configured correctly

## Related Files

- **Workspace CLAUDE.md**: `/Users/samtexas/src/directory-platform/CLAUDE.md`
- **directory-builder CLAUDE.md**: `/Users/samtexas/src/directory-platform/directory-builder/CLAUDE.md`
- **README.md**: User-facing documentation
- **pyproject.toml**: Package configuration

## Quick Reference

**Key files:**
- `models.py` - Thread (discussion_id), Comment
- `views.py` - All views accept discussion_id
- `urls.py` - Simple `/discussions/<discussion_id>/` patterns
- `templatetags/discussion_tags.py` - SEO helpers

**Integration one-liner:**
```django
<div hx-get="/discussions/{{ object.uuid }}/">Loading...</div>
```

**That's it!** No model changes, no migrations, no complexity.
