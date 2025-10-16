from django.urls import path

from . import views

app_name = "django_discussions"

urlpatterns = [
    path("<str:discussion_id>/", views.index, name="index"),
    path("thread/<slug:short_uuid>/", views.thread_detail, name="thread_detail"),
    path("<str:discussion_id>/create/", views.create_thread, name="create_thread"),
    path("comment/<slug:thread_short_uuid>/create/", views.create_comment, name="create_comment"),
    path("thread/<slug:short_uuid>/delete/", views.delete_thread, name="delete_thread"),
    path("comment/<slug:short_uuid>/delete/", views.delete_comment, name="delete_comment"),
]
