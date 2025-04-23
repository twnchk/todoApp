from django.test import TestCase
from django.db import IntegrityError
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from todoBoard.models import TodoList
from users.models import CustomUser


class TodoListModelTest(TestCase):
    def setUp(self):
        self.test_object = TodoList.objects.create(title='test_board', description='test_description')
        self.existing_group = Group.objects.create(name='test_board admins')
        self.user = CustomUser.objects.create_user(username='testUser321',
                                                   email='test@example.com',
                                                   password='testing123456')

    def create_test_superuser(self):
        return CustomUser.objects.create_superuser(username='testSuperUser321',
                                                   email='test@example.com',
                                                   password='testing123456')

    def test_do_not_create_todolist_without_title(self):
        with self.assertRaises(IntegrityError):
            TodoList.objects.create(title=None, description=None)

    def test_show_delete_button_user_is_superuser(self):
        user = self.create_test_superuser()

        self.assertTrue(self.test_object.show_delete_button(user))

    def test_show_delete_button_user_is_in_allowed_group(self):
        """
        Verify that show_delete_button returns true for user that is in board group
        """
        test_permissions_group, _ = Group.objects.get_or_create(name=f'Board {self.test_object.title} Admin')
        test_board_content_type = ContentType.objects.get_for_model(TodoList)

        # Add all permissions
        test_board_admin_permissions = Permission.objects.filter(content_type=test_board_content_type)
        test_permissions_group.permissions.add(*test_board_admin_permissions)

        self.test_object.allowed_groups.add(test_permissions_group)
        self.user.groups.add(test_permissions_group)

        self.assertTrue(self.test_object.show_delete_button(self.user))
        self.assertEqual(str(self.test_object), 'test_board')

    def test_show_delete_button_user_not_in_allowed_group(self):
        """
        Verify that show_delete_button returns false for user that is NOT in board group
        """

        # Do not add any permissions to user or test_object
        self.assertFalse(self.test_object.show_delete_button(self.user))

    def test_is_user_allowed_for_superuser(self):
        # Do not add any permissions to user or test_object
        self.user = self.create_test_superuser()
        self.assertTrue(self.test_object.is_user_allowed(self.user))
