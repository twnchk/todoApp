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

    def test_doNotCreateTodoItemWithoutTitle(self):
        with self.assertRaises(IntegrityError):
            TodoList.objects.create(title=None, description=None)


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

    def test_boards_list_view(self):
        response = self.client.get(reverse('boards_list'))
        self.assertTemplateUsed(response, 'boards.html')
        self.assertEqual(response.status_code, 200)

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
