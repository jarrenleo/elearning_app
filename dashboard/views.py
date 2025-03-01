from django.utils import timezone
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from courses.models import Course, Topic
from status_updates.models import StatusUpdate


@login_required
def student_dashboard_view(request):
    courses = Course.objects.filter(students=request.user)
    deadlines = Topic.objects.filter(
        course__students=request.user,
        deadline__gte=timezone.now(),
    ).order_by("deadline")
    status_updates = StatusUpdate.objects.filter(user=request.user)

    return render(
        request,
        "student_dashboard.html",
        {"courses": courses, "deadlines": deadlines, "status_updates": status_updates},
    )


@login_required
def teacher_dashboard_view(request):
    status_updates = StatusUpdate.objects.filter(user=request.user)
    courses = Course.objects.filter(teachers=request.user)

    return render(
        request,
        "teacher_dashboard.html",
        {"courses": courses, "status_updates": status_updates},
    )
