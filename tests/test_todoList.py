from django.test import TestCase, Client
from django.db import IntegrityError
from django.contrib.auth.models import Group, Permission
from django.urls import reverse
from django.contrib.contenttypes.models import ContentType
from todoBoard.models import TodoList
from users.models import CustomUser


class TodoListTest(TestCase):
    def test_createTodoListWithDescription(self):
        expected_title = "NewBoard"
        expected_description = "Lorem Ipsum"

        test_object = TodoList.objects.create(title=expected_title, description=expected_description)
        fetched_test_object = TodoList.objects.get(id=test_object.id)

        # Verify
        self.assertEqual(fetched_test_object.title, test_object.title)
        self.assertEqual(fetched_test_object.description, test_object.description)
        self.assertEqual(str(fetched_test_object), expected_title)

        # Cleanup
        test_object.delete()

    def test_createTodoListWithoutDescription(self):
        expected_title = "NewBoard"
        expected_description = None

        test_object = TodoList.objects.create(title=expected_title, description=expected_description)

        fetched_test_object = TodoList.objects.get(id=test_object.id)

        # Verify
        self.assertEqual(fetched_test_object.title, test_object.title)
        self.assertEqual(fetched_test_object.description, test_object.description)

        # Cleanup
        test_object.delete()

    def test_do_not_create_todolist_without_title(self):
        with self.assertRaises(IntegrityError):
            TodoList.objects.create(title=None, description=None)

    def test_show_delete_button_user_is_superuser(self):
        # Prepare dummy user object
        expected_username = "testUser321"
        expected_password = "testing123456"
        expected_email = "test@example.com"
        user = CustomUser.objects.create_superuser(expected_username, expected_email, expected_password)

        # Create test object
        test_object = TodoList.objects.create(title='test', description=None)

        self.assertTrue(test_object.show_delete_button(user))

    def test_show_delete_button_user_is_in_allowed_group(self):
        """
        Verify that show_delete_button returns true for user that is in board group
        """

        # Prepare dummy user object
        expected_username = "testUser321"
        expected_password = "testing123456"
        expected_email = "test@example.com"
        user = CustomUser.objects.create_user(expected_username, expected_email, expected_password)

        # Create test object
        test_object = TodoList.objects.create(title='test', description=None)

        test_permissions_group, _ = Group.objects.get_or_create(name=f'Board {test_object.title} Admin')
        test_board_content_type = ContentType.objects.get_for_model(TodoList)

        # Add all permissions
        test_board_admin_permissions = Permission.objects.filter(content_type=test_board_content_type)
        test_permissions_group.permissions.add(*test_board_admin_permissions)

        test_object.allowed_groups.add(test_permissions_group)
        user.groups.add(test_permissions_group)

        self.assertTrue(test_object.show_delete_button(user))


    def test_show_delete_button_user_not_in_allowed_group(self):
        """
        Verify that show_delete_button returns false for user that is NOT in board group
        """

        # Prepare dummy user object
        expected_username = "testUser321"
        expected_password = "testing123456"
        expected_email = "test@example.com"
        user = CustomUser.objects.create_user(expected_username, expected_email, expected_password)

        # Create test object
        test_object = TodoList.objects.create(title='test', description=None)

        # Do not add any permissions to user or test_object
        self.assertFalse(test_object.show_delete_button(user))

    def test_is_user_allowed_for_superuser(self):
        # Prepare dummy user object
        expected_username = "testUser321"
        expected_password = "testing123456"
        expected_email = "test@example.com"
        user = CustomUser.objects.create_superuser(expected_username, expected_email, expected_password)

        # Create test object
        test_object = TodoList.objects.create(title='test', description=None)

        # Do not add any permissions to user or test_object
        self.assertTrue(test_object.is_user_allowed(user))

class TodoListViewTest(TestCase):
    def test_board_detail_user_not_logged_in(self):
        """
        Test that a board cannot be displayed if there is no user logged in
        """
        test_board = TodoList.objects.create(title='test')
        response = self.client.get(reverse('board_detail', args=(test_board.id,)))
        self.assertTemplateUsed(response, 'forbidden.html')
        self.assertEqual(response.status_code, 200)

        test_board.delete()

    def test_board_detail_user_with_permissions(self):
        """
        Test that board can be displayed if user belong to group
        with required permissions
        """
        test_permissions_group, _ = Group.objects.get_or_create(name='Board Test Admin')
        test_board_content_type = ContentType.objects.get_for_model(TodoList)

        # Add all permissions
        test_board_admin_permissions = Permission.objects.filter(content_type=test_board_content_type)
        test_permissions_group.permissions.add(*test_board_admin_permissions)

        test_board = TodoList.objects.create(title='test')
        test_board.allowed_groups.add(test_permissions_group)

        # Prepare dummy user object
        expected_username = "testUser321"
        expected_password = "testing123456"
        expected_email = "test@example.com"
        user = CustomUser.objects.create_user(expected_username, expected_email, expected_password)
        user.groups.add(test_permissions_group)
        self.client = Client()

        login = self.client.login(username=expected_username, password=expected_password)
        self.assertTrue(login)

        response = self.client.get(reverse('board_detail', args=(test_board.id,)))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'board_detail.html')

        test_permissions_group.delete()
        user.delete()
        test_board.delete()

    def test_board_detail_user_without_permissions(self):
        """
        Test that board can NOT be displayed if user does NOT belong to group
        with required permissions
        """
        test_permissions_group, _ = Group.objects.get_or_create(name='Board Test Admin')
        test_board_content_type = ContentType.objects.get_for_model(TodoList)

        # Add all permissions
        test_board_admin_permissions = Permission.objects.filter(content_type=test_board_content_type)
        test_permissions_group.permissions.add(*test_board_admin_permissions)

        test_board = TodoList.objects.create(title='test')
        test_board.allowed_groups.add(test_permissions_group)

        # Prepare dummy user object
        expected_username = "testUser321"
        expected_password = "testing123456"
        expected_email = "test@example.com"
        user = CustomUser.objects.create_user(expected_username, expected_email, expected_password)
        # Do not add user to any group
        self.client = Client()

        login = self.client.login(username=expected_username, password=expected_password)
        self.assertTrue(login)

        response = self.client.get(reverse('board_detail', args=(test_board.id,)))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'forbidden.html')

        test_permissions_group.delete()
        user.delete()
        test_board.delete()

    def test_board_detail_backlog(self):
        test_permissions_group, _ = Group.objects.get_or_create(name='Board Test Admin')
        test_board_content_type = ContentType.objects.get_for_model(TodoList)

        # Add all permissions
        test_board_admin_permissions = Permission.objects.filter(content_type=test_board_content_type)
        test_permissions_group.permissions.add(*test_board_admin_permissions)

        test_board = TodoList.objects.create(title='test')
        test_board.allowed_groups.add(test_permissions_group)

        # Prepare dummy user object
        expected_username = "testUser321"
        expected_password = "testing123456"
        expected_email = "test@example.com"
        user = CustomUser.objects.create_user(expected_username, expected_email, expected_password)
        user.groups.add(test_permissions_group)
        self.client = Client()

        login = self.client.login(username=expected_username, password=expected_password)
        self.assertTrue(login)

        response = self.client.get(reverse('board_backlog', args=(test_board.id,)))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'board_backlog.html')

        test_permissions_group.delete()
        user.delete()
        test_board.delete()

    def test_board_archived_backlog(self):
        test_permissions_group, _ = Group.objects.get_or_create(name='Board Test Admin')
        test_board_content_type = ContentType.objects.get_for_model(TodoList)

        # Add all permissions
        test_board_admin_permissions = Permission.objects.filter(content_type=test_board_content_type)
        test_permissions_group.permissions.add(*test_board_admin_permissions)

        test_board = TodoList.objects.create(title='test')
        test_board.is_archived = True
        test_board.allowed_groups.add(test_permissions_group)

        # Prepare dummy user object
        expected_username = "testUser321"
        expected_password = "testing123456"
        expected_email = "test@example.com"
        user = CustomUser.objects.create_user(expected_username, expected_email, expected_password)
        user.groups.add(test_permissions_group)
        self.client = Client()

        login = self.client.login(username=expected_username, password=expected_password)
        self.assertTrue(login)

        response = self.client.get(reverse('board_backlog', args=(test_board.id,)))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'board_backlog.html')

        test_permissions_group.delete()
        user.delete()
        test_board.delete()

    def test_board_archived_backlog_user_not_logged_in(self):
        test_permissions_group, _ = Group.objects.get_or_create(name='Board Test Admin')
        test_board_content_type = ContentType.objects.get_for_model(TodoList)

        # Add all permissions
        test_board_admin_permissions = Permission.objects.filter(content_type=test_board_content_type)
        test_permissions_group.permissions.add(*test_board_admin_permissions)

        test_board = TodoList.objects.create(title='test')
        test_board.is_archived = True
        test_board.allowed_groups.add(test_permissions_group)

        # Prepare dummy user object
        expected_username = "testUser321"
        expected_password = "testing123456"
        expected_email = "test@example.com"
        user = CustomUser.objects.create_user(expected_username, expected_email, expected_password)
        user.groups.add(test_permissions_group)
        self.client = Client()

        response = self.client.get(reverse('board_backlog', args=(test_board.id,)))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'forbidden.html')

        test_permissions_group.delete()
        user.delete()
        test_board.delete()

    def test_boards_list_view_user_logged_in(self):
        test_board = TodoList.objects.create(title='test')

        # Prepare dummy user object
        expected_username = "testUser321"
        expected_password = "testing123456"
        expected_email = "test@example.com"
        user = CustomUser.objects.create_user(expected_username, expected_email, expected_password)
        self.client = Client()

        login = self.client.login(username=expected_username, password=expected_password)
        self.assertTrue(login)

        response = self.client.get(reverse('boards_list'))
        self.assertTemplateUsed(response, 'boards.html')
        self.assertEqual(response.status_code, 200)

        user.delete()
        test_board.delete()

    def test_board_create_new_group_created(self):
        # Prepare dummy user object
        expected_username = "testUser321"
        expected_password = "testing123456"
        expected_email = "test@example.com"
        user = CustomUser.objects.create_user(expected_username, expected_email, expected_password)
        self.client = Client()

        login = self.client.login(username=expected_username, password=expected_password)
        self.assertTrue(login)

        form_url = reverse('board_create')
        form_data = {
            'title': 'DummyBoard'
        }

        # Simulate form submission
        response = self.client.post(form_url, form_data)

        # Verify board was created and new group was created as well
        created_board = TodoList.objects.filter(title='DummyBoard')
        self.assertTrue(created_board.exists(), 'Board was not created.')
        self.assertTrue(created_board.get().allowed_groups.filter(name='DummyBoard admins').exists(),
                        'Group was not added to board')
        self.assertTrue(Group.objects.filter(name='DummyBoard admins').exists(), 'Group was not created')
        self.assertTrue(user.groups.filter(name='DummyBoard admins').exists(), "User was not added to the group.")

        self.assertRedirects(response, '/boards/1')

        user.delete()

    def test_all_boards_view_user_is_admin(self):
        """
        Test that all boards can be displayed for superuser
        """

        test_board = TodoList.objects.create(title='test')

        # Prepare dummy user object
        expected_username = "testUser321"
        expected_password = "testing123456"
        expected_email = "test@example.com"

        user = CustomUser.objects.create_superuser(expected_username, expected_email, expected_password)
        self.client = Client()

        login = self.client.login(username=expected_username, password=expected_password)
        self.assertTrue(login)

        response = self.client.get(reverse('all_boards_list'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'boards.html')
        self.assertTrue(user.is_superuser)

        user.delete()
        test_board.delete()

    def test_all_boards_view_user_is_not_admin(self):
        """
        Test that all boards can be displayed for superuser
        """

        test_board = TodoList.objects.create(title='test')

        # Prepare dummy user object
        expected_username = "testUser321"
        expected_password = "testing123456"
        expected_email = "test@example.com"
        user = CustomUser.objects.create_user(expected_username, expected_email, expected_password)
        self.client = Client()

        login = self.client.login(username=expected_username, password=expected_password)
        self.assertTrue(login)

        response = self.client.get(reverse('all_boards_list'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'forbidden.html')
        self.assertFalse(user.is_superuser)

        user.delete()
        test_board.delete()

    def test_archived_boards_list_view_user_is_not_admin(self):
        """
        Test that all boards can be displayed for superuser
        """

        test_board = TodoList.objects.create(title='test', is_archived=True)

        # Prepare dummy user object
        expected_username = "testUser321"
        expected_password = "testing123456"
        expected_email = "test@example.com"
        user = CustomUser.objects.create_user(expected_username, expected_email, expected_password)
        self.client = Client()

        login = self.client.login(username=expected_username, password=expected_password)
        self.assertTrue(login)

        response = self.client.get(reverse('archived_boards'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'archived_boards.html')

        # Assert that context boards has no elements if user is not superuser
        self.assertEqual(len(response.context['boards']), 0)

        user.delete()
        test_board.delete()

    def test_archived_boards_list_view_user_is_admin(self):
        """
        Test that all boards can be displayed for superuser
        """

        test_board = TodoList.objects.create(title='test', is_archived=True)

        # Prepare dummy user object
        expected_username = "testUser321"
        expected_password = "testing123456"
        expected_email = "test@example.com"
        user = CustomUser.objects.create_superuser(expected_username, expected_email, expected_password)
        self.client = Client()

        login = self.client.login(username=expected_username, password=expected_password)
        self.assertTrue(login)

        response = self.client.get(reverse('archived_boards'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'archived_boards.html')

        # Assert that context boards has elements if user is superuser
        self.assertEqual(len(response.context['boards']), 1)

        user.delete()
        test_board.delete()

