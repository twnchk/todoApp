from django.test import TestCase, Client
from django.urls import reverse
from users.models import CustomUser, Profile


class ProfileModelTest(TestCase):
    expected_username = "testUser321"
    expected_password = "testing123456"
    expected_email = "test@example.com"

    def setUp(self):
        self.user = CustomUser.objects.create_user(self.expected_username,
                                                   self.expected_email,
                                                   self.expected_password)

    def test_user_creation(self):
        self.assertEqual(self.user.username, self.expected_username)
        self.assertEqual(self.user.email, self.expected_email)
        self.assertTrue(self.user.check_password(self.expected_password))
        self.assertEqual(str(self.user), self.user.username)

    def test_profile_creation(self):
        profile = Profile.objects.get(user=self.user)
        self.assertIsNotNone(profile)
        self.assertEqual(profile.user, self.user)

        # To ensure that valid path for avatar is used
        self.assertNotEqual(profile.avatar, 'default.png')
        self.assertEqual(profile.avatar, 'avatars/default.png')

