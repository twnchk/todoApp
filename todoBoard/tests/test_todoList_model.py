from django.test import TestCase
from django.db import IntegrityError

from todoBoard.models import TodoList
from users.models import CustomUser


class TodoListModelTest(TestCase):
    def setUp(self):
        self.user = CustomUser.objects.create_user(username='testUser321',
                                                   email='test@example.com',
                                                   password='testing123456')
        self.test_object = TodoList.objects.create(title='test_board', description='test_description', owner=self.user)

    def create_test_superuser(self):
        self.user = CustomUser.objects.create_superuser(username='testSuperUser321',
                                                        email='test@example.com',
                                                        password='testing123456')

    def create_not_allowed_user(self):
        self.user = CustomUser.objects.create_user(username='unauthorizedUser',
                                                   email='unauthorizedUser@example.com',
                                                   password='testing123456')

    def test_do_not_create_todolist_without_title(self):
        with self.assertRaises(IntegrityError):
            TodoList.objects.create(title=None, description=None, owner=self.user)

    def test_show_delete_button_user_is_superuser(self):
        self.create_test_superuser()

        self.assertTrue(self.test_object.show_delete_button(self.user))

    def test_show_delete_button_user_allowed(self):
        self.assertTrue(self.test_object.show_delete_button(self.user))
        self.assertEqual(str(self.test_object), 'test_board')

    def test_show_delete_button_user_not_in_allowed_group(self):
        self.create_not_allowed_user()
        self.assertFalse(self.test_object.show_delete_button(self.user))

    def test_is_user_allowed_for_superuser(self):
        self.create_test_superuser()
        self.assertTrue(self.test_object.is_user_allowed(self.user))

    def test_is_user_allowed(self):
        self.assertTrue(self.test_object.is_user_allowed(self.user))

    def test_is_user_allowed_for_not_allowed_user(self):
        self.create_not_allowed_user()
        self.assertFalse(self.test_object.is_user_allowed(self.user))
