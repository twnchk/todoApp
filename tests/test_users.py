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

    def test_profile_creation(self):
        profile = Profile.objects.get(user=self.user)
        self.assertIsNotNone(profile)
        self.assertEqual(profile.user, self.user)

        # To ensure that valid path for avatar is used
        self.assertNotEqual(profile.avatar, 'default.png')
        self.assertEqual(profile.avatar, 'avatars/default.png')


class ProfileViewTest(TestCase):
    expected_username = "testUser321"
    expected_password = "testing123456"
    expected_email = "test@example.com"

    def setUp(self):
        self.user = CustomUser.objects.create_user(self.expected_username,
                                                   self.expected_email,
                                                   self.expected_password)
        self.client = Client()

    def test_user_profile_login_successful(self):
        login = self.client.login(username=self.expected_username, password=self.expected_password)
        self.assertTrue(login)

        response = self.client.get(reverse('user_profile'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'user_profile.html')
        self.assertEqual(response.context['user'], self.user)

    def test_user_profile_login_not_successful(self):
        login = self.client.login(username=self.expected_username, password='invalid_passwd')
        self.assertFalse(login)

        response = self.client.get(reverse('user_profile'))

        self.assertEqual(response.status_code, 302)

        # TODO: Assert that user is redirected to home page
        # self.assertTemplateUsed(response, 'user_profile.html')
