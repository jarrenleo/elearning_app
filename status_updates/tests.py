from django.test import TestCase
from django.urls import reverse
from accounts.models import User
from .models import StatusUpdate


class StatusUpdateViewsTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="test_student",
            password="123456",
            first_name="Test",
            last_name="Student",
            email="student@test.com",
            role=User.Role.STUDENT,
        )
        self.status_update = StatusUpdate.objects.create(
            user=self.user, content="Test status update"
        )

    def test_create_status_update_view(self):
        self.client.force_login(self.user)
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

    def test_delete_status_update_view(self):
        self.client.force_login(self.user)
        status_update = StatusUpdate.objects.create(
            user=self.user, content="Status to delete"
        )
        response = self.client.post(
            reverse("status_updates:delete_status_update", args=[status_update.id])
        )

        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse("dashboard:student"))
        self.assertFalse(StatusUpdate.objects.filter(id=status_update.id).exists())

    def test_login_required(self):
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
