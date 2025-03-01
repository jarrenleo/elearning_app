from django.urls import path
from . import views

app_name = "courses"

urlpatterns = [
    path("<int:course_id>/", views.course_view, name="course_view"),
    path("enroll/", views.enroll_course_view, name="enroll_course_view"),
    path(
        "withdraw/<int:course_id>/",
        views.withdraw_course_view,
        name="withdraw_course_view",
    ),
    path("create/", views.create_course_view, name="create_course_view"),
    path("<int:course_id>/edit/", views.edit_course_view, name="edit_course_view"),
    path(
        "<int:course_id>/delete/", views.delete_course_view, name="delete_course_view"
    ),
    path(
        "<int:course_id>/edit/topic/create/",
        views.create_topic_view,
        name="create_topic_view",
    ),
    path(
        "<int:course_id>/edit/topic/<int:topic_id>/edit/",
        views.edit_topic_view,
        name="edit_topic_view",
    ),
    path(
        "<int:course_id>/edit/topic/<int:topic_id>/delete/",
        views.delete_topic_view,
        name="delete_topic_view",
    ),
    path(
        "<int:course_id>/remove_student/<int:student_id>/",
        views.remove_student_view,
        name="remove_student_view",
    ),
]
