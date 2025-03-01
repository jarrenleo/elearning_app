from datetime import datetime
from django.utils import timezone
from django.contrib import messages
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from accounts.models import User
from .models import Course, Topic, TopicAttachment
from notifications.utils import notify_course_update, notify_course_enrollment


@login_required
def course_view(request, course_id):
    # Get the course
    course = get_object_or_404(Course, id=course_id)

    # Check if user is enrolled or is a teacher
    if (
        request.user not in course.teachers.all()
        and request.user not in course.students.all()
    ):
        messages.error(request, "You are not enrolled in this course")
        return redirect("dashboard:student")

    # Get the course topics
    topics = Topic.objects.filter(course=course)

    # Render the course template
    return render(
        request,
        "courses/course.html",
        {
            "course": course,
            "topics": topics,
        },
    )


@login_required
def enroll_course_view(request):
    # Check if user is a student
    if request.user.role != request.user.Role.STUDENT:
        return redirect("dashboard:teacher")

    if request.method == "GET":
        # Get all courses except ones student is already enrolled in
        courses = Course.objects.exclude(students=request.user)

        # Render the enroll course template
        return render(request, "courses/enroll_course.html", {"courses": courses})

    if request.method == "POST":
        # Get the selected courses
        selected_courses = request.POST.getlist("selected_courses")
        # Enroll the student in the selected courses
        for course_id in selected_courses:
            course = get_object_or_404(Course, id=course_id)
            course.students.add(request.user)

            course.save()
            # Notify the teacher that the student has enrolled in the course
            notify_course_enrollment(request.user, course)
        messages.success(request, "Courses enrolled successfully")

        # Redirect to the student dashboard with the enrolled courses
        return redirect("dashboard:student")


@login_required
def withdraw_course_view(request, course_id):
    # Check if user is a student
    if request.user.role != request.user.Role.STUDENT:
        return redirect("dashboard:teacher")

    # Get the course
    course = get_object_or_404(Course, id=course_id, students=request.user)

    # Withdraw the student from the course
    course.students.remove(request.user)
    course.save()
    messages.success(request, "Course withdrawn successfully")

    # Redirect to the student dashboard with the updated courses
    return redirect("dashboard:student")


@login_required
def create_course_view(request):
    # Check if user is a teacher
    if request.user.role != request.user.Role.TEACHER:
        return redirect("dashboard:student")

    if request.method == "GET":
        # Render the create course template
        return render(request, "courses/create_course.html")

    if request.method == "POST":
        # Get the course title and description
        title = request.POST["title"]
        description = request.POST["description"]

        # Create the course
        course = Course.objects.create(title=title, description=description)
        # Add the teacher to the course
        course.teachers.add(request.user)
        messages.success(request, "Course created successfully")

        # Redirect to the teacher dashboard with the created course
        return redirect("dashboard:teacher")


@login_required
def edit_course_view(request, course_id):
    # Check if user is a teacher
    if request.user.role != request.user.Role.TEACHER:
        return redirect("dashboard:student")

    # Get the course and topics
    course = get_object_or_404(Course, id=course_id)
    topics = Topic.objects.filter(course=course)

    if request.method == "GET":
        # Render the edit course template
        return render(
            request,
            "courses/edit_course.html",
            {"course": course, "topics": topics},
        )

    if request.method == "POST":
        # Get the course title and description
        title = request.POST["title"]
        description = request.POST["description"]

        # Update the course
        course.title = title
        course.description = description

        course.save()
        # Notify the students that the course has been updated
        notify_course_update(course)
        messages.success(request, "Course information updated successfully")

        # Redirect to the edit course template with the updated course and topics
        return redirect("courses:edit_course_view", course_id=course_id)


@login_required
def delete_course_view(request, course_id):
    # Check if user is a teacher
    if request.user.role != request.user.Role.TEACHER:
        return redirect("dashboard:student")

    # Get the course
    course = get_object_or_404(Course, id=course_id, teachers=request.user)

    # Delete all attachment files for all topics in the course
    for topic in course.topics.all():
        for attachment in topic.attachments.all():
            attachment.file.delete(save=False)

    # Delete the course
    course.delete()
    messages.success(request, "Course deleted successfully")

    # Redirect to the teacher dashboard with the updated courses
    return redirect("dashboard:teacher")


@login_required
def create_topic_view(request, course_id):
    # Get the course
    course = get_object_or_404(Course, id=course_id, teachers=request.user)

    if request.method == "GET":
        # Render the create topic template
        return render(request, "courses/create_topic.html", {"course_id": course_id})

    if request.method == "POST":
        # Get the deadline and make it timezone-aware
        deadline = request.POST["deadline"]
        deadline = timezone.make_aware(datetime.strptime(deadline, "%Y-%m-%dT%H:%M"))

        # Create the topic
        topic = Topic.objects.create(
            title=request.POST["title"],
            deadline=deadline,
            content=request.POST["content"],
            course=course,
            created_by=request.user,
        )
        # Create attachments
        files = request.FILES.getlist("attachments")
        if files:
            for file in files:
                TopicAttachment.objects.create(
                    topic=topic,
                    file=file,
                    file_name=file.name,
                    file_type=file.content_type,
                )
        messages.success(request, "Topic created successfully")

        # Redirect to the edit course template with the created topic
        return redirect("courses:edit_course_view", course_id=course_id)


@login_required
def edit_topic_view(request, course_id, topic_id):
    # Get the course, topic and attachments
    course = get_object_or_404(Course, id=course_id, teachers=request.user)
    topic = get_object_or_404(Topic, id=topic_id, course=course)
    attachments = TopicAttachment.objects.filter(topic=topic)

    if request.method == "GET":
        # Render the edit topic template
        return render(
            request,
            "courses/edit_topic.html",
            {"topic": topic, "course_id": course_id, "attachments": attachments},
        )

    if request.method == "POST":
        # Get the topic title, deadline and content
        title = request.POST["title"]
        deadline = request.POST["deadline"]
        content = request.POST["content"]

        # Get the attachments
        files = request.FILES.getlist("attachments")
        if files:
            # Delete existing attachments
            for attachment in topic.attachments.all():
                attachment.delete()
                attachment.file.delete(save=False)

            # Create new attachment
            for file in files:
                TopicAttachment.objects.create(
                    topic=topic,
                    file=file,
                    file_name=file.name,
                    file_type=file.content_type,
                )

        # Update the topic
        topic.title = title
        topic.deadline = deadline
        topic.content = content

        topic.save()
        notify_course_update(course)
        messages.success(request, "Topic updated successfully")

        # Redirect to the edit course template with the updated topic
        return redirect("courses:edit_course_view", course_id=course_id)


@login_required
def delete_topic_view(request, course_id, topic_id):
    # Get the topic
    topic = get_object_or_404(
        Topic, id=topic_id, course__id=course_id, course__teachers=request.user
    )

    # Delete the attachment files
    for attachment in topic.attachments.all():
        # This deletes the actual file from storage
        attachment.file.delete(save=False)

    # Delete the topic
    topic.delete()
    messages.success(request, "Topic deleted successfully")

    # Redirect to the edit course template with the updated topics
    return redirect("courses:edit_course_view", course_id=course_id)


@login_required
def remove_student_view(request, course_id, student_id):
    # Get the course and student
    course = get_object_or_404(Course, id=course_id, teachers=request.user)
    student = get_object_or_404(User, id=student_id)

    # Remove the student from the course
    course.students.remove(student)
    course.save()
    messages.success(request, "Student removed successfully")

    # Redirect to the teacher dashboard with the updated students
    return redirect("dashboard:teacher")
