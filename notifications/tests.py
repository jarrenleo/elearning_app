from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from courses.models import Course
from .models import Notification

class NotificationViewTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = get_user_model().objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.course = Course.objects.create(
            title='Test Course',
            description='Test Description'
        )
        self.notification = Notification.objects.create(
            recipient=self.user,
            notification_type='TEST',
            title='Test Notification',
            message='Test Message',
            course=self.course
        )

    def test_notifications_view_authenticated(self):
        """Test that authenticated users can access notifications page"""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('notifications:notifications'))
        
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'notifications/notifications.html')
        self.assertContains(response, 'Test Notification')
        self.assertContains(response, 'Test Message')

    def test_notifications_view_unauthenticated(self):
        """Test that unauthenticated users are redirected to login"""
        response = self.client.get(reverse('notifications:notifications'))
        self.assertEqual(response.status_code, 302)

    def test_mark_all_read(self):
        """Test marking all notifications as read"""
        self.client.login(username='testuser', password='testpass123')
        
        # Create an unread notification
        unread_notification = Notification.objects.create(
            recipient=self.user,
            notification_type='TEST',
            title='Unread Notification',
            message='Unread Message',
            course=self.course,
            is_read=False
        )
        
        response = self.client.post(reverse('notifications:mark_all_read'))
        
        self.assertEqual(response.status_code, 302)
        unread_notification.refresh_from_db()
        self.assertTrue(unread_notification.is_read)

    def test_mark_all_read_unauthenticated(self):
        """Test that unauthenticated users cannot mark notifications as read"""
        response = self.client.post(reverse('notifications:mark_all_read'))
        self.assertEqual(response.status_code, 302)

