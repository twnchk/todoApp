from django.test import TestCase, Client
from django.urls import reverse
from users.models import CustomUser, Profile
from django.contrib.auth import get_user_model

class ProfileViewTest(TestCase):
    expected_username = "testUser321"
    expected_password = "testing123456"
    expected_email = "test@example.com"

    def setUp(self):
        self.user = CustomUser.objects.create_user(self.expected_username,
                                                   self.expected_email,
                                                   self.expected_password)
        self.client = Client()

    def login_user(self):
        login = self.client.login(username=self.expected_username, password=self.expected_password)
        self.assertTrue(login)

    def test_user_profile_login_successful(self):
        self.login_user()

        response = self.client.get(reverse('user_profile', kwargs={'id': self.user.id}))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'user_profile.html')
        self.assertEqual(response.context['user'], self.user)
        self.assertEqual(str(self.user.profile), self.user.username)
        self.assertEqual(repr(self.user), 'User(username=testUser321)')

    def test_user_profile_user_not_logged(self):
        response = self.client.get(reverse('user_profile', kwargs={'id': self.user.id}))

        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, '/login/?next=/profile/1')

    def test_register_view_user_authenticated(self):
        """
        Verify that authenticated user cannot access register view
        """
        self.login_user()
        response = self.client.get(reverse('register'))

        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, '/boards/')

    def test_register_view_get_request(self):
        response = self.client.get(reverse('register'))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'register.html')
        self.assertIn('form', response.context)

    def test_register_view_post_request(self):
        form_data = {
            'username': 'JohnDoe321',
            'email': 'johndoe.jd@imaginary.com',
            'password1': 'testing123456',
            'password2': 'testing123456'
        }
        form_url = reverse('register')

        response = self.client.post(path=form_url, data=form_data)
        users = get_user_model().objects.all()

        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, '/boards/')
        self.assertEqual(users.count(), 2)

    def test_register_view_post_request_form_not_valid(self):
        form_data = {
            'username': 'JohnDoe321',
            'email': 'johndoe.jd@imaginary.com',
            'password1': 'testing123456',
            'password2': 'testing6453'
        }
        form_url = reverse('register')

        response = self.client.post(path=form_url, data=form_data)
        users = get_user_model().objects.all()

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'register.html')
        self.assertEqual(users.count(), 1)
        self.assertIn('form', response.context)
        form = response.context['form']
        self.assertTrue(form.errors)
        self.assertIn('password2', form.errors)

