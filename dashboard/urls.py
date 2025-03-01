from django.urls import path
from . import views

app_name = "dashboard"

urlpatterns = [
    path("student/", views.student_dashboard_view, name="student"),
    path("teacher/", views.teacher_dashboard_view, name="teacher"),
]
