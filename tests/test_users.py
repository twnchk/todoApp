from django.test import TestCase
from users.models import CustomUser, Profile


class ProfileTest(TestCase):
    expected_username = "testUser321"
    expected_password = "testing123456"
    expected_email = "test@example.com"

    def setUp(self):
        self.user = CustomUser.objects.create_user(self.expected_username, self.expected_email, self.expected_password)

    def test_user_creation(self):
        self.assertEqual(self.user.username, self.expected_username)
        self.assertEqual(self.user.email, self.expected_email)
        self.assertTrue(self.user.check_password(self.expected_password))

    def test_profile_creation(self):
        profile = Profile.objects.get(user=self.user)
        self.assertIsNotNone(profile)
        self.assertEqual(profile.user, self.user)
