from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include("accounts.urls")),
    path("dashboard/", include("dashboard.urls")),
    path("home/", include("home.urls")),
    path("search/", include("search.urls")),
    path("course/", include("courses.urls")),
    path("status-updates/", include("status_updates.urls")),
    path("feedback/", include("feedback.urls")),
    path("notifications/", include("notifications.urls")),
]
