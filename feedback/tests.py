from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from courses.models import Course
from feedback.models import Feedback


class FeedbackViewTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.User = get_user_model()

        # Create test users
        self.student = self.User.objects.create_user(
            username="student", password="password123", role=self.User.Role.STUDENT
        )
        self.teacher = self.User.objects.create_user(
            username="teacher", password="password123", role=self.User.Role.TEACHER
        )

        # Create test course
        self.course = Course.objects.create(title="Test Course")
        self.course.students.add(self.student)
        self.course.teachers.add(self.teacher)

    def test_feedback_view_student(self):
        self.client.login(username="student", password="password123")
        response = self.client.get(reverse("feedback:feedback"))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "feedback_form.html")
        self.assertIn("courses", response.context)

    def test_feedback_view_teacher(self):
        self.client.login(username="teacher", password="password123")
        response = self.client.get(reverse("feedback:feedback"))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "view_feedback.html")
        self.assertIn("feedback_list", response.context)

    def test_submit_feedback(self):
        self.client.login(username="student", password="password123")

        feedback_data = {
            "course": self.course.id,
            "subject": "Test Subject",
            "message": "Test Message",
        }

        response = self.client.post(reverse("feedback:submit_feedback"), feedback_data)

        # Check redirect
        self.assertRedirects(response, reverse("dashboard:student"))

        # Verify feedback was created
        feedback = Feedback.objects.first()
        self.assertEqual(feedback.subject, "Test Subject")
        self.assertEqual(feedback.message, "Test Message")
        self.assertEqual(feedback.student, self.student)
        self.assertEqual(feedback.course, self.course)

    def test_submit_feedback_invalid_course(self):
        self.client.login(username="student", password="password123")

        feedback_data = {
            "course": 999,  # Invalid course ID
            "subject": "Test Subject",
            "message": "Test Message",
        }

        response = self.client.post(reverse("feedback:submit_feedback"), feedback_data)

        self.assertEqual(response.status_code, 404)
