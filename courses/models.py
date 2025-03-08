from django.db import models
from django.conf import settings


# Course model
class Course(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField()
    teachers = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        related_name="teaching_courses",
        limit_choices_to={"role": "TEACHER"},
    )
    students = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        through="CourseEnrolment",
        related_name="enrolled_courses",
        limit_choices_to={"role": "STUDENT"},
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


# Course enrolment model
class CourseEnrolment(models.Model):
    student = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        limit_choices_to={"role": "STUDENT"},
    )
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    enrolled_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ["student", "course"]


# Topic model
class Topic(models.Model):
    title = models.CharField(max_length=255)
    deadline = models.DateTimeField()
    content = models.TextField()
    course = models.ForeignKey(
        "Course", on_delete=models.CASCADE, related_name="topics"
    )
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        limit_choices_to={"role": "TEACHER"},
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


# Topic attachment model
class TopicAttachment(models.Model):
    topic = models.ForeignKey(
        Topic, on_delete=models.CASCADE, related_name="attachments"
    )
    file = models.FileField(upload_to="topic_attachments/")
    file_name = models.CharField(max_length=255)
    file_type = models.CharField(max_length=100)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    # When a topic attachment is deleted, delete the actual file from storage
    def delete(self, *args, **kwargs):
        self.file.delete(save=False)
        super().delete(*args, **kwargs)
