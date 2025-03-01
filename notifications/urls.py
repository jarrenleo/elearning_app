from django.urls import path
from . import views

app_name = "notifications"

urlpatterns = [
    path("", views.notifications_view, name="notifications"),
    path("mark-all-read/", views.mark_all_read, name="mark_all_read"),
]
