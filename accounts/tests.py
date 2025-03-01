from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model

User = get_user_model()


class AccountsTestCase(TestCase):
    def setUp(self):
        # This runs before each test
        self.client = Client()
        self.student = User.objects.create_user(
            username="student",
            password="password123",
            email="student@test.com",
            role="STUDENT",
        )
        self.teacher = User.objects.create_user(
            username="teacher",
            password="password123",
            email="teacher@test.com",
            role="TEACHER",
        )

    def test_login_view_get(self):
        # Test GET request to login page
        response = self.client.get(reverse("accounts:login"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "login.html")

    def test_login_view_post_success_student(self):
        # Test successful student login
        response = self.client.post(
            reverse("accounts:login"),
            {"username": "student", "password": "password123"},
        )
        self.assertRedirects(response, reverse("dashboard:student"))
        self.assertTrue("_auth_user_id" in self.client.session)

    def test_login_view_post_success_teacher(self):
        # Test successful teacher login
        response = self.client.post(
            reverse("accounts:login"),
            {"username": "teacher", "password": "password123"},
        )
        self.assertRedirects(response, reverse("dashboard:teacher"))
        self.assertTrue("_auth_user_id" in self.client.session)

    def test_login_view_post_invalid_credentials(self):
        # Test login with wrong password
        response = self.client.post(
            reverse("accounts:login"),
            {"username": "student", "password": "wrongpassword"},
        )
        self.assertRedirects(response, reverse("accounts:login"))
        messages = list(response.wsgi_request._messages)
        self.assertEqual(str(messages[0]), "Invalid username or password")

    def test_signup_view_get(self):
        # Test GET request to signup page
        response = self.client.get(reverse("accounts:signup"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "signup.html")

    def test_signup_view_post_success(self):
        # Test successful signup
        response = self.client.post(
            reverse("accounts:signup"),
            {
                "username": "newstudent",
                "password": "password123",
                "email": "new@test.com",
                "first_name": "New",
                "last_name": "Student",
                "role": "STUDENT",
            },
        )
        self.assertRedirects(response, reverse("accounts:login"))
        self.assertTrue(User.objects.filter(username="newstudent").exists())

    def test_signup_view_post_duplicate_username(self):
        # Test signup with existing username
        response = self.client.post(
            reverse("accounts:signup"),
            {
                "username": "student",  # This username already exists
                "password": "password123",
                "email": "another@test.com",
                "first_name": "Another",
                "last_name": "Student",
                "role": "STUDENT",
            },
        )
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "signup.html")
        self.assertContains(response, "Account with this username already exists")

    def test_profile_view_authenticated(self):
        # Test profile view for authenticated user
        self.client.login(username="student", password="password123")
        response = self.client.get(reverse("accounts:profile"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "profile.html")

    def test_profile_view_unauthenticated(self):
        # Test profile view for unauthenticated user
        response = self.client.get(reverse("accounts:profile"))
        self.assertRedirects(
            response, f"{reverse('accounts:login')}?next={reverse('accounts:profile')}"
        )

    def test_logout_view(self):
        # Test logout functionality
        self.client.login(username="student", password="password123")
        response = self.client.get(reverse("accounts:logout"))
        self.assertRedirects(response, reverse("accounts:login"))
        self.assertFalse("_auth_user_id" in self.client.session)

    def test_change_profile_information(self):
        # Test profile information update
        self.client.login(username="student", password="password123")
        response = self.client.post(
            reverse("accounts:change_profile_information"),
            {
                "username": "updatedstudent",
                "first_name": "Updated",
                "last_name": "Name",
                "email": "updated@test.com",
                "biography": "New biography",
            },
        )
        self.assertRedirects(response, reverse("accounts:profile"))
        updated_user = User.objects.get(id=self.student.id)
        self.assertEqual(updated_user.username, "updatedstudent")
        self.assertEqual(updated_user.biography, "New biography")

    def test_change_password(self):
        # Test password change
        self.client.login(username="student", password="password123")
        response = self.client.post(
            reverse("accounts:change_profile_password"),
            {
                "current_password": "password123",
                "new_password": "newpassword123",
                "confirm_password": "newpassword123",
            },
        )
        self.assertRedirects(response, reverse("accounts:profile"))
        # Verify can login with new password
        success = self.client.login(username="student", password="newpassword123")
        self.assertTrue(success)
