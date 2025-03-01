from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from .models import StatusUpdate

User = get_user_model()


class StatusUpdateViewsTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.student = User.objects.create_user(
            username="student", password="password123", role=User.Role.STUDENT
        )
        self.teacher = User.objects.create_user(
            username="teacher", password="password123", role=User.Role.TEACHER
        )
        self.status_update = StatusUpdate.objects.create(
            user=self.student, content="Test status update"
        )

    def test_create_status_update_view_student(self):
        # Login as student
        self.client.login(username="student", password="password123")

        # Test creating with valid content
        response = self.client.post(
            reverse("status_updates:create_status_update"),
            {"content": "New status update"},
        )
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse("dashboard:student"))
        self.assertTrue(
            StatusUpdate.objects.filter(content="New status update").exists()
        )

        # Test creating with empty content
        response = self.client.post(
            reverse("status_updates:create_status_update"), {"content": ""}
        )
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse("dashboard:student"))

    def test_create_status_update_view_teacher(self):
        # Login as teacher
        self.client.login(username="teacher", password="password123")

        response = self.client.post(
            reverse("status_updates:create_status_update"),
            {"content": "Teacher status update"},
        )
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse("dashboard:teacher"))
        self.assertTrue(
            StatusUpdate.objects.filter(content="Teacher status update").exists()
        )

    def test_delete_status_update_view_student(self):
        # Login as student
        self.client.login(username="student", password="password123")

        status_update = StatusUpdate.objects.create(
            user=self.student, content="Status to delete"
        )

        response = self.client.post(
            reverse("status_updates:delete_status_update", args=[status_update.id])
        )
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse("dashboard:student"))
        self.assertFalse(StatusUpdate.objects.filter(id=status_update.id).exists())

    def test_delete_status_update_view_teacher(self):
        # Login as teacher
        self.client.login(username="teacher", password="password123")

        status_update = StatusUpdate.objects.create(
            user=self.teacher, content="Teacher status to delete"
        )

        response = self.client.post(
            reverse("status_updates:delete_status_update", args=[status_update.id])
        )
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse("dashboard:teacher"))
        self.assertFalse(StatusUpdate.objects.filter(id=status_update.id).exists())

    def test_login_required(self):
        # Test without login
        response = self.client.post(
            reverse("status_updates:create_status_update"),
            {"content": "Should not work"},
        )
        self.assertEqual(response.status_code, 302)
        self.assertIn("login", response.url)

        response = self.client.post(
            reverse("status_updates:delete_status_update", args=[self.status_update.id])
        )
        self.assertEqual(response.status_code, 302)
        self.assertIn("login", response.url)
