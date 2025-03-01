from django.db import models
from django.conf import settings
from courses.models import Course


class Notification(models.Model):
    TYPES = (
        ("COURSE_UPDATE", "Course Update"),
        ("COURSE_ENROLLMENT", "Course Enrollment"),
    )

    recipient = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="notifications"
    )
    notification_type = models.CharField(max_length=20, choices=TYPES)
    title = models.CharField(max_length=255)
    message = models.TextField()
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
