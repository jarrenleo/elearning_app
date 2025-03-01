from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Notification


@login_required
def notifications_view(request):
    # Get all notifications for the current user
    notifications = Notification.objects.filter(recipient=request.user).select_related(
        "course"
    )

    # Render the notifications page
    return render(
        request, "notifications/notifications.html", {"notifications": notifications}
    )


@login_required
def mark_all_read(request):
    # Mark all notifications as read
    Notification.objects.filter(recipient=request.user, is_read=False).update(
        is_read=True
    )
    messages.success(request, "All notifications marked as read")

    # Redirect to the notifications page with all notifications marked as read
    return redirect("notifications:notifications")
