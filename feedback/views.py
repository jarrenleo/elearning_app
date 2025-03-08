from django.contrib import messages
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from courses.models import Course
from feedback.models import Feedback


@login_required
def feedback_view(request):
    # Check if the user is a student
    if request.user.role == request.user.Role.STUDENT:
        # Get courses where the student is enrolled
        courses = Course.objects.filter(students=request.user)
        # Render the feedback form with the courses as select options
        return render(request, "feedback_form.html", {"courses": courses})

    # Check if the user is a teacher
    if request.user.role == request.user.Role.TEACHER:
        # Get courses where the teacher is the author
        teacher_courses = Course.objects.filter(teachers=request.user)
        # Render the feedback list from the students of the courses
        feedback_list = Feedback.objects.filter(course__in=teacher_courses)
        return render(request, "view_feedback.html", {"feedback_list": feedback_list})


@login_required
def submit_feedback_view(request):
    # Get the course id, subject and message from the request
    course_id = request.POST.get("course")
    subject = request.POST.get("subject")
    message = request.POST.get("message")

    # Get the course
    course = get_object_or_404(Course, id=course_id)

    # Create feedback
    Feedback.objects.create(
        student=request.user,
        course=course,
        subject=subject,
        message=message,
    )
    messages.success(request, "Feedback submitted successfully")

    # Redirect to the student dashboard
    return redirect("dashboard:student")
