from django.test import TestCase
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType

from todoBoard.models import TodoItem
from todoBoard.models import TodoList
from users.models import CustomUser

class TodoItemTest(TestCase):
    def test_is_user_allowed_for_superuser(self):
        # Prepare dummy user object
        expected_username = "testUser321"
        expected_password = "testing123456"
        expected_email = "test@example.com"
        user = CustomUser.objects.create_superuser(expected_username, expected_email, expected_password)

        test_board = TodoList.objects.create(title='test', description=None)

        task_name = 'test_task'
        # Create test object
        test_object = TodoItem.objects.create(name=task_name,
                                              description=None,
                                              author=user,
                                              board=test_board)

        # Do not add any permissions to user or test_object
        self.assertTrue(test_object.is_user_allowed(user))
        self.assertEqual(str(test_object), task_name)

    def test_is_user_allowed_user_not_in_board_group(self):
        # Prepare dummy user object
        expected_username = "testUser321"
        expected_password = "testing123456"
        expected_email = "test@example.com"
        user = CustomUser.objects.create_user(expected_username, expected_email, expected_password)

        test_board = TodoList.objects.create(title='test', description=None)

        # Create test object
        test_object = TodoItem.objects.create(name='test',
                                              description=None,
                                              author=user,
                                              board=test_board)

        self.assertFalse(test_object.is_user_allowed(user))

    def test_is_user_allowed_user_in_board_group(self):
        # Prepare dummy user object
        expected_username = "testUser321"
        expected_password = "testing123456"
        expected_email = "test@example.com"
        user = CustomUser.objects.create_user(expected_username, expected_email, expected_password)

        test_board = TodoList.objects.create(title='test', description=None)

        # Create test object
        test_object = TodoItem.objects.create(name='test',
                                              description=None,
                                              author=user,
                                              board=test_board)

        test_permissions_group, _ = Group.objects.get_or_create(name=f'Board {test_board.title} Admin')
        test_board_content_type = ContentType.objects.get_for_model(TodoList)

        # Add all permissions
        test_board_admin_permissions = Permission.objects.filter(content_type=test_board_content_type)
        test_permissions_group.permissions.add(*test_board_admin_permissions)

        test_object.board.allowed_groups.add(test_permissions_group)
        user.groups.add(test_permissions_group)

        self.assertTrue(test_object.is_user_allowed(user))
