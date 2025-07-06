from django.test import TestCase

from todoBoard.models import TodoItem
from todoBoard.models import TodoList
from users.models import CustomUser

class TodoItemTest(TestCase):
    def test_is_user_allowed_for_superuser(self):
        # Prepare dummy user object
        expected_password = "testing123456"
        admin_user = CustomUser.objects.create_superuser('testAdmin321', 'test1@example.com', expected_password)
        normal_user = CustomUser.objects.create_user('testUser321', 'test2@example.com', expected_password)

        test_board = TodoList.objects.create(title='test', description=None, owner=normal_user)

        task_name = 'test_task'
        # Create test object
        test_object = TodoItem.objects.create(name=task_name,
                                              description=None,
                                              author=normal_user,
                                              board=test_board)

        # Do not add any permissions to user or test_object
        self.assertTrue(test_object.is_user_allowed(admin_user))
        self.assertEqual(str(test_object), task_name)

    def test_is_user_allowed_user_not_allowed(self):
        # Prepare dummy user object
        expected_password = "testing123456"
        owner_user = CustomUser.objects.create_user('testUser1', 'test1@example.com', expected_password)
        unallowed_user = CustomUser.objects.create_user('testUser2', 'test2@example.com', expected_password)

        test_board = TodoList.objects.create(title='test', description=None, owner=owner_user)

        # Create test object
        test_object = TodoItem.objects.create(name='test',
                                              description=None,
                                              author=owner_user,
                                              board=test_board)

        self.assertFalse(test_object.is_user_allowed(unallowed_user))

    def test_is_user_allowed_user_allowed(self):
        # Prepare dummy user object
        expected_username = "testUser321"
        expected_password = "testing123456"
        expected_email = "test@example.com"
        user = CustomUser.objects.create_user(expected_username, expected_email, expected_password)

        test_board = TodoList.objects.create(title='test', description=None, owner=user)

        # Create test object
        test_object = TodoItem.objects.create(name='test',
                                              description=None,
                                              author=user,
                                              board=test_board)

        test_object.board.allowed_users.add(user)
        self.assertTrue(test_object.is_user_allowed(user))
