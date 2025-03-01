from django.test import TestCase
from django.urls import reverse
from django.utils import timezone
from datetime import timedelta
from django.core.files.uploadedfile import SimpleUploadedFile
from accounts.models import User
from .models import Course, Topic


class CourseViewTests(TestCase):
    def setUp(self):
        # Create test users
        self.teacher = User.objects.create_user(
            email="teacher@test.com", password="password123", role=User.Role.TEACHER
        )
        self.student = User.objects.create_user(
            email="student@test.com", password="password123", role=User.Role.STUDENT
        )

        # Create test course
        self.course = Course.objects.create(
            title="Test Course", description="Test Description"
        )
        self.course.teachers.add(self.teacher)
        self.course.students.add(self.student)

        # Create test topic
        self.topic = Topic.objects.create(
            title="Test Topic",
            deadline=timezone.now() + timedelta(days=7),
            content="Test Content",
            course=self.course,
            created_by=self.teacher,
        )

    def test_course_view(self):
        self.client.force_login(self.student)
        response = self.client.get(
            reverse("courses:course_view", args=[self.course.id])
        )
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "courses/course.html")
        self.assertIn("course", response.context)
        self.assertIn("topics", response.context)

    def test_enroll_course_view(self):
        self.client.force_login(self.student)
        new_course = Course.objects.create(
            title="New Course", description="New Description"
        )

        # Test GET
        response = self.client.get(reverse("courses:enroll_course_view"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "courses/enroll_course.html")

        # Test POST
        response = self.client.post(
            reverse("courses:enroll_course_view"), {"selected_courses": [new_course.id]}
        )
        self.assertRedirects(response, reverse("dashboard:student"))
        self.assertTrue(new_course.students.filter(id=self.student.id).exists())

    def test_create_course_view(self):
        self.client.force_login(self.teacher)

        # Test GET
        response = self.client.get(reverse("courses:create_course_view"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "courses/create_course.html")

        # Test POST
        response = self.client.post(
            reverse("courses:create_course_view"),
            {"title": "New Course", "description": "New Description"},
        )
        self.assertRedirects(response, reverse("dashboard:teacher"))
        self.assertTrue(Course.objects.filter(title="New Course").exists())

    def test_edit_topic_view(self):
        self.client.force_login(self.teacher)

        # Test GET
        response = self.client.get(
            reverse("courses:edit_topic_view", args=[self.course.id, self.topic.id])
        )
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "courses/edit_topic.html")

        # Test POST
        test_file = SimpleUploadedFile("test.txt", b"test content")
        response = self.client.post(
            reverse("courses:edit_topic_view", args=[self.course.id, self.topic.id]),
            {
                "title": "Updated Topic",
                "deadline": timezone.now() + timedelta(days=14),
                "content": "Updated Content",
                "attachments": [test_file],
            },
        )
        self.assertRedirects(
            response, reverse("courses:edit_course_view", args=[self.course.id])
        )
        self.topic.refresh_from_db()
        self.assertEqual(self.topic.title, "Updated Topic")

    def test_delete_course_view(self):
        self.client.force_login(self.teacher)
        response = self.client.post(
            reverse("courses:delete_course_view", args=[self.course.id])
        )
        self.assertRedirects(response, reverse("dashboard:teacher"))
        self.assertFalse(Course.objects.filter(id=self.course.id).exists())

    def test_remove_student_view(self):
        self.client.force_login(self.teacher)
        response = self.client.post(
            reverse(
                "courses:remove_student_view", args=[self.course.id, self.student.id]
            )
        )
        self.assertRedirects(response, reverse("dashboard:teacher"))
        self.assertFalse(self.course.students.filter(id=self.student.id).exists())

    def test_unauthorized_access(self):
        # Test student trying to access teacher views
        self.client.force_login(self.student)
        response = self.client.get(reverse("courses:create_course_view"))
        self.assertRedirects(response, reverse("dashboard:student"))

        # Test teacher trying to access student views
        self.client.force_login(self.teacher)
        response = self.client.get(reverse("courses:enroll_course_view"))
        self.assertRedirects(response, reverse("dashboard:teacher"))
