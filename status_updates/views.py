from django.contrib import messages
from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required
from .models import StatusUpdate


@login_required
def create_status_update_view(request):
    # Get the content from the request
    content = request.POST.get("content")

    # If the content is not empty
    if content:
        # Create a status update
        StatusUpdate.objects.create(user=request.user, content=content)
        messages.success(request, "Status update posted successfully")
    else:
        # Else, send error message
        messages.error(request, "Please enter a status update")

    # If the user is a student
    if request.user.role == request.user.Role.STUDENT:
        # Redirect to the student dashboard with the updated status updates
        return redirect("dashboard:student")
    # If the user is a teacher
    if request.user.role == request.user.Role.TEACHER:
        # Redirect to the teacher dashboard with the updated status updates
        return redirect("dashboard:teacher")


@login_required
def delete_status_update_view(request, id):
    # Get the status update
    status_update = StatusUpdate.objects.get(id=id)

    # Delete the status update
    status_update.delete()
    messages.success(request, "Status update deleted successfully")

    # If the user is a student
    if request.user.role == request.user.Role.STUDENT:
        # Redirect to the student dashboard with the updated status updates
        return redirect("dashboard:student")
    # If the user is a teacher
    if request.user.role == request.user.Role.TEACHER:
        # Redirect to the teacher dashboard with the updated status updates
        return redirect("dashboard:teacher")
