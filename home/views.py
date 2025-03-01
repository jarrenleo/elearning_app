from django.utils import timezone
from django.shortcuts import render, get_object_or_404
from accounts.models import User
from courses.models import Course, Topic
from status_updates.models import StatusUpdate


def home(request, username):
    # Get the user
    user = get_object_or_404(User, username=username)
    # Get the status updates
    status_updates = StatusUpdate.objects.filter(user=user)

    # If the user is a student
    if user.role == "STUDENT":
        # Get the courses
        courses = Course.objects.filter(students=user)
        # Get the deadlines
        deadlines = Topic.objects.filter(
            course__students=user,
            deadline__gte=timezone.now(),
        ).order_by("deadline")

        # Render the student home page
        return render(
            request,
            "student_home.html",
            {
                "user": user,
                "courses": courses,
                "status_updates": status_updates,
                "deadlines": deadlines,
            },
        )

    # If the user is a teacher
    if user.role == "TEACHER":
        # Get the courses
        courses = Course.objects.filter(teachers=user)

        # Render the teacher home page
        return render(
            request,
            "teacher_home.html",
            {"user": user, "courses": courses, "status_updates": status_updates},
        )
