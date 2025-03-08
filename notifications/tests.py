from django.test import TestCase
from django.urls import reverse
from courses.models import Course
from accounts.models import User
from .models import Notification


class NotificationViewTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="test_teacher",
            password="123456",
            first_name="Test",
            last_name="Teacher",
            email="teacher@test.com",
            role=User.Role.TEACHER,
        )
        self.course = Course.objects.create(
            title="Test Course", description="Test Description"
        )
        self.notification = Notification.objects.create(
            recipient=self.user,
            notification_type="TEST",
            title="Test Notification",
            message="Test Message",
            course=self.course,
        )

    # Test that authenticated users can access notifications page
    def test_notifications_view_authenticated(self):
        self.client.force_login(self.user)
        response = self.client.get(reverse("notifications:notifications"))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "notifications/notifications.html")
        self.assertContains(response, "Test Notification")
        self.assertContains(response, "Test Message")

    # Test that unauthenticated users are redirected to login
    def test_notifications_view_unauthenticated(self):
        response = self.client.get(reverse("notifications:notifications"))

        self.assertEqual(response.status_code, 302)

    # Test marking all notifications as read
    def test_mark_all_read(self):
        self.client.force_login(self.user)
        # Create an unread notification
        unread_notification = Notification.objects.create(
            recipient=self.user,
            notification_type="TEST",
            title="Unread Notification",
            message="Unread Message",
            course=self.course,
            is_read=False,
        )
        response = self.client.post(reverse("notifications:mark_all_read"))

        self.assertEqual(response.status_code, 302)

        unread_notification.refresh_from_db()

        self.assertTrue(unread_notification.is_read)

    # Test that unauthenticated users cannot mark notifications as read
    def test_mark_all_read_unauthenticated(self):
        response = self.client.post(reverse("notifications:mark_all_read"))

        self.assertEqual(response.status_code, 302)
