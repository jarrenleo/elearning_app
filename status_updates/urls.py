from django.urls import path
from . import views

app_name = "status_updates"

urlpatterns = [
    path("create/", views.create_status_update_view, name="create_status_update"),
    path(
        "delete/<int:id>/",
        views.delete_status_update_view,
        name="delete_status_update",
    ),
]
