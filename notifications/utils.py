from .models import Notification


def notify_course_update(course):
    """Create notifications for all students when a course is updated"""
    for student in course.students.all():
        Notification.objects.create(
            recipient=student,
            notification_type="COURSE_UPDATE",
            title="Course Updated",
            message=f"The {course.title} course has been updated",
            course=course,
        )


def notify_course_enrollment(student, course):
    """Create notification for teacher when a student enrolls"""
    for teacher in course.teachers.all():
        Notification.objects.create(
            recipient=teacher,
            notification_type="COURSE_ENROLLMENT",
            title="New Student Enrollment",
            message=f"{student.first_name} {student.last_name} enrolled into your {course.title} course",
            course=course,
        )
