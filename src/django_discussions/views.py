from django.contrib.auth.decorators import login_required
from django.http import HttpRequest, HttpResponse
from django.shortcuts import get_object_or_404, render

from django_discussions.models import Comment, Thread

"""
These views are all designed for HTMX requests.
"""


def index(request: HttpRequest, discussion_id: str) -> HttpResponse:
    """Render the discussion index for a given discussion_id."""
    threads = Thread.objects.filter(is_active=True, discussion_id=discussion_id).order_by("-created_at")

    data = {
        "discussion_id": discussion_id,
        "threads": threads,
    }

    return render(request, "django_discussions/index.html", data)


def thread_detail(request: HttpRequest, short_uuid: str) -> HttpResponse:
    """Render the thread detail page."""
    thread = get_object_or_404(Thread, short_uuid=short_uuid, is_active=True)

    data = {
        "thread": thread,
    }

    return render(request, "django_discussions/_thread_detail.html", data)


@login_required
def create_thread(request: HttpRequest, discussion_id: str) -> HttpResponse:
    """Create a new thread and HTMX reply with the new thread."""
    error = None

    if request.method == "GET":
        data = {"discussion_id": discussion_id}
        return render(request, "django_discussions/_thread_form.html", data)

    # POST request
    title = request.POST.get("thread_title", "")
    content = request.POST.get("thread_content", "")

    min_title_length = 3
    max_title_length = 100
    if len(title) > max_title_length or len(title) < min_title_length:
        error = f"Title must be between {min_title_length} and {max_title_length} characters."

    if not title or not content:
        error = "Title and content are required."

    if error:
        response = render(
            request,
            "django_discussions/_thread_form.html",
            {
                "error": error,
                "discussion_id": discussion_id,
                "thread_title": title,
                "thread_content": content,
            },
        )
        response.headers["HX-Retarget"] = "#new-thread-form"
        response.headers["HX-Reswap"] = "innerHTML"
        return response

    thread = Thread.objects.create(
        title=title,
        content=content,
        author=request.user,
        discussion_id=discussion_id,
    )

    return render(
        request,
        "django_discussions/_thread_header.html",
        {
            "thread": thread,
            "success": "Thread created successfully.",
            "close_thread_form": True,
        },
    )


@login_required
def create_comment(request: HttpRequest, thread_short_uuid: str) -> HttpResponse:
    """Create a new comment."""
    thread = get_object_or_404(Thread, short_uuid=thread_short_uuid, is_active=True)

    if request.method == "POST":
        content = request.POST.get("content")

        if not content:
            return render(
                request,
                "django_discussions/_comment_form.html",
                {
                    "error": "Content is required.",
                    "thread": thread,
                },
            )

        thread.comments.create(content=content, author=request.user)
        return render(
            request,
            "django_discussions/_comments_section.html",
            {
                "thread": thread,
                "success": "Comment created successfully.",
            },
        )

    return render(request, "django_discussions/_comment_form.html", {"thread": thread})


@login_required
def delete_thread(request: HttpRequest, short_uuid: str) -> HttpResponse:
    """Delete a thread."""
    thread = get_object_or_404(Thread, short_uuid=short_uuid, is_active=True)

    if request.user != thread.author and not request.user.is_superuser:
        # return 403 Forbidden response
        return HttpResponse(status=403)

    thread.delete()
    return render(request, "index.html")


@login_required
def delete_comment(request: HttpRequest, short_uuid: str) -> HttpResponse:
    """Delete a comment."""
    comment = get_object_or_404(Comment, short_uuid=short_uuid, is_active=True)

    if request.user != comment.author and not request.user.is_superuser:
        # return 403 Forbidden response
        return HttpResponse(status=403)

    comment.delete()
    return render(request, "django_discussions/thread_detail.html", {"comment": comment})
