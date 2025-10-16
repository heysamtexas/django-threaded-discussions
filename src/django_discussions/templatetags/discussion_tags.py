from django import template
from django.utils.safestring import mark_safe

from django_discussions.models import Thread

register = template.Library()


@register.inclusion_tag("django_discussions/_thread_header.html")
def render_discussions_seo(discussion_id: str, max_threads: int = 10):
    """
    Render SEO-optimized discussions for a given discussion_id.

    This tag server-renders discussions for SEO purposes, ensuring
    Google can crawl and index the discussion content.

    Usage:
        {% load discussion_tags %}
        {% render_discussions_seo discussion_id=blog_post.uuid %}
        {% render_discussions_seo discussion_id=blog_post.uuid max_threads=5 %}
    """
    threads = Thread.get_seo_threads(discussion_id=str(discussion_id), max_count=max_threads)

    return {
        "threads": threads,
        "discussion_id": discussion_id,
    }


@register.simple_tag
def thread_count(discussion_id: str) -> int:
    """
    Return the count of active threads for a discussion_id.

    Usage:
        {% load discussion_tags %}
        {% thread_count discussion_id=blog_post.uuid %}
    """
    return Thread.objects.filter(discussion_id=str(discussion_id), is_active=True).count()


@register.simple_tag
def discussion_structured_data(discussion_id: str):
    """
    Generate schema.org structured data for discussions.

    Returns JSON-LD markup for DiscussionForumPosting that can
    be indexed by search engines for rich snippets.

    Usage:
        {% load discussion_tags %}
        {% discussion_structured_data discussion_id=blog_post.uuid %}
    """
    threads = Thread.objects.filter(discussion_id=str(discussion_id), is_active=True, is_spam=False)[:5]

    if not threads:
        return ""

    structured_data_items = []

    for thread in threads:
        comments_data = []
        for comment in thread.comments.filter(is_active=True, is_spam=False)[:10]:
            comments_data.append(
                {
                    "@type": "Comment",
                    "text": comment.content[:200],  # Limit to 200 chars
                    "author": {
                        "@type": "Person",
                        "name": comment.author.username,
                    },
                    "datePublished": comment.created_at.isoformat(),
                }
            )

        thread_data = {
            "@context": "https://schema.org",
            "@type": "DiscussionForumPosting",
            "headline": thread.title,
            "text": thread.content[:500],  # Limit to 500 chars
            "author": {
                "@type": "Person",
                "name": thread.author.username,
            },
            "datePublished": thread.created_at.isoformat(),
            "commentCount": thread.comment_count,
        }

        if comments_data:
            thread_data["comment"] = comments_data

        structured_data_items.append(thread_data)

    if not structured_data_items:
        return ""

    # Generate JSON-LD script tag
    import json

    json_str = json.dumps(
        structured_data_items[0] if len(structured_data_items) == 1 else structured_data_items, indent=2
    )

    html = f'<script type="application/ld+json">\n{json_str}\n</script>'

    return mark_safe(html)
