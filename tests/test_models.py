from django.contrib.auth.models import User
from django.test import TestCase

from django_discussions.models import Comment, Thread
from tests.example_app.models import BlogPost, Product


class ThreadModelTest(TestCase):
    """Test Thread model functionality."""

    def setUp(self):
        """Set up test data."""
        self.user = User.objects.create_user(username="testuser", password="testpass123")
        self.blog_post = BlogPost.objects.create(title="Test Post", slug="test-post", content="Test content")

    def test_create_thread_with_uuid(self):
        """Test creating a thread with UUID discussion_id."""
        thread = Thread.objects.create(
            discussion_id=self.blog_post.discussion_id,
            title="Test Thread",
            content="Test content",
            author=self.user,
        )

        self.assertEqual(thread.discussion_id, str(self.blog_post.uuid))
        self.assertEqual(thread.title, "Test Thread")
        self.assertIsNotNone(thread.short_uuid)

    def test_create_thread_with_slug(self):
        """Test creating a thread with slug discussion_id."""
        product = Product.objects.create(name="Test Product", slug="test-product", description="Test", price=9.99)

        thread = Thread.objects.create(
            discussion_id=product.discussion_id,
            title="Product Discussion",
            content="Great product!",
            author=self.user,
        )

        self.assertEqual(thread.discussion_id, "test-product")
        self.assertEqual(thread.title, "Product Discussion")

    def test_thread_comment_count(self):
        """Test thread comment_count property."""
        thread = Thread.objects.create(
            discussion_id="test-123",
            title="Test Thread",
            content="Test",
            author=self.user,
        )

        self.assertEqual(thread.comment_count, 0)

        # Add comments
        Comment.objects.create(thread=thread, content="Comment 1", author=self.user)
        Comment.objects.create(thread=thread, content="Comment 2", author=self.user)

        self.assertEqual(thread.comment_count, 2)

    def test_get_seo_threads(self):
        """Test get_seo_threads class method."""
        discussion_id = "test-discussion"

        # Create multiple threads
        Thread.objects.create(
            discussion_id=discussion_id, title="Thread 1", content="Content 1", author=self.user, is_spam=False
        )
        Thread.objects.create(
            discussion_id=discussion_id, title="Thread 2", content="Content 2", author=self.user, is_spam=True
        )
        Thread.objects.create(
            discussion_id=discussion_id, title="Thread 3", content="Content 3", author=self.user, is_spam=False
        )

        # Get SEO threads (should exclude spam)
        seo_threads = Thread.get_seo_threads(discussion_id, max_count=10)

        self.assertEqual(seo_threads.count(), 2)
        for thread in seo_threads:
            self.assertFalse(thread.is_spam)


class CommentModelTest(TestCase):
    """Test Comment model functionality."""

    def setUp(self):
        """Set up test data."""
        self.user = User.objects.create_user(username="testuser", password="testpass123")
        self.thread = Thread.objects.create(
            discussion_id="test-123", title="Test Thread", content="Test content", author=self.user
        )

    def test_create_comment(self):
        """Test creating a comment."""
        comment = Comment.objects.create(thread=self.thread, content="Test comment", author=self.user)

        self.assertEqual(comment.content, "Test comment")
        self.assertEqual(comment.thread, self.thread)
        self.assertIsNotNone(comment.short_uuid)

    def test_threaded_comments(self):
        """Test nested comment replies."""
        parent_comment = Comment.objects.create(thread=self.thread, content="Parent comment", author=self.user)

        reply = Comment.objects.create(
            thread=self.thread, content="Reply to parent", author=self.user, parent=parent_comment
        )

        self.assertEqual(reply.parent, parent_comment)
        self.assertEqual(parent_comment.replies.count(), 1)
        self.assertEqual(parent_comment.replies.first(), reply)
