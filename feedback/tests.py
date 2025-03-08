from django.test import TestCase
from django.urls import reverse
from accounts.models import User
from courses.models import Course
from feedback.models import Feedback


class FeedbackViewTests(TestCase):
    def setUp(self):
        # Create test users
        self.student = User.objects.create_user(
            username="test_student",
            password="123456",
            first_name="Test",
            last_name="Student",
            email="student@test.com",
            role=User.Role.STUDENT,
        )
        self.teacher = User.objects.create_user(
            username="test_teacher",
            password="123456",
            first_name="Test",
            last_name="Teacher",
            email="teacher@test.com",
            role=User.Role.TEACHER,
        )

        # Create test course
        self.course = Course.objects.create(title="Test Course")
        self.course.students.add(self.student)
        self.course.teachers.add(self.teacher)

    def test_feedback_view_student(self):
        self.client.force_login(self.student)
        response = self.client.get(reverse("feedback:feedback"))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "feedback_form.html")
        self.assertIn("courses", response.context)

    def test_feedback_view_teacher(self):
        self.client.force_login(self.teacher)
        response = self.client.get(reverse("feedback:feedback"))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "view_feedback.html")
        self.assertIn("feedback_list", response.context)

    def test_submit_feedback(self):
        self.client.force_login(self.student)
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
        self.client.force_login(self.student)
        feedback_data = {
            "course": 999,  # Invalid course ID
            "subject": "Test Subject",
            "message": "Test Message",
        }
        response = self.client.post(reverse("feedback:submit_feedback"), feedback_data)

        self.assertEqual(response.status_code, 404)
