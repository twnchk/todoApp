from django.test import TestCase, Client
from django.db import IntegrityError
from django.contrib.auth.models import Group, Permission
from django.urls import reverse
from django.contrib.contenttypes.models import ContentType
from todoBoard.models import TodoList
from users.models import CustomUser


class TodoListModelTest(TestCase):
    def setUp(self):
        self.test_object = TodoList.objects.create(title='test_board', description='test_description')

    def create_test_user(self):
        return CustomUser.objects.create_user(username='testUser321',
                                              email='test@example.com',
                                              password='testing123456')

    def create_test_superuser(self):
        return CustomUser.objects.create_superuser(username='testUser321',
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

        user = self.create_test_user()
        user.groups.add(test_permissions_group)

        self.assertTrue(self.test_object.show_delete_button(user))

    def test_show_delete_button_user_not_in_allowed_group(self):
        """
        Verify that show_delete_button returns false for user that is NOT in board group
        """

        # Do not add any permissions to user or test_object
        self.assertFalse(self.test_object.show_delete_button(self.create_test_user()))

    def test_is_user_allowed_for_superuser(self):
        # Do not add any permissions to user or test_object
        self.assertTrue(self.test_object.is_user_allowed(self.create_test_superuser()))


class TodoListViewTest(TestCase):
    def setUp(self):
        self.test_object = TodoList.objects.create(title='test_board', description='test_description')
        self.username = 'testUser321'
        self.password = 'testing123456'

    def create_test_user(self):
        return CustomUser.objects.create_user(username=self.username,
                                              email='test@example.com',
                                              password=self.password)

    def create_test_superuser(self):
        return CustomUser.objects.create_superuser(username=self.username,
                                                   email='test@example.com',
                                                   password=self.password)

    def test_board_detail_user_not_logged_in(self):
        """
        Test that a board cannot be displayed if there is no user logged in
        """
        response = self.client.get(reverse('board_detail', args=(self.test_object.id,)))
        self.assertTemplateUsed(response, 'forbidden.html')
        self.assertEqual(response.status_code, 200)

    def test_board_detail_user_with_permissions(self):
        """
        Test that board can be displayed if user belong to group
        with required permissions
        """
        test_permissions_group, _ = Group.objects.get_or_create(name=f'Board {self.test_object.title} Admin')
        test_board_content_type = ContentType.objects.get_for_model(TodoList)

        # Add all permissions
        test_board_admin_permissions = Permission.objects.filter(content_type=test_board_content_type)
        test_permissions_group.permissions.add(*test_board_admin_permissions)

        self.test_object.allowed_groups.add(test_permissions_group)

        # Prepare dummy user object
        user = self.create_test_user()
        user.groups.add(test_permissions_group)
        self.client = Client()

        login = self.client.login(username=self.username, password=self.password)
        self.assertTrue(login)

        response = self.client.get(reverse('board_detail', args=(self.test_object.id,)))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'board_detail.html')

    def test_board_detail_user_without_permissions(self):
        """
        Test that board can NOT be displayed if user does NOT belong to group
        with required permissions
        """

        user = self.create_test_user()
        # Do not add user to any group
        self.client = Client()

        login = self.client.login(username=self.username, password=self.password)
        self.assertTrue(login)

        response = self.client.get(reverse('board_detail', args=(self.test_object.id,)))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'forbidden.html')

    def test_board_detail_backlog(self):
        test_permissions_group, _ = Group.objects.get_or_create(name='Board Test Admin')
        test_board_content_type = ContentType.objects.get_for_model(TodoList)

        # Add all permissions
        test_board_admin_permissions = Permission.objects.filter(content_type=test_board_content_type)
        test_permissions_group.permissions.add(*test_board_admin_permissions)

        self.test_object.allowed_groups.add(test_permissions_group)

        # Prepare dummy user object
        user = self.create_test_user()
        user.groups.add(test_permissions_group)
        self.client = Client()

        login = self.client.login(username=self.username, password=self.password)
        self.assertTrue(login)

        response = self.client.get(reverse('board_backlog', args=(self.test_object.id,)))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'board_backlog.html')

    def test_board_detail_archived(self):
        test_permissions_group, _ = Group.objects.get_or_create(name='Board Test Admin')
        test_board_content_type = ContentType.objects.get_for_model(TodoList)

        # Add all permissions
        test_board_admin_permissions = Permission.objects.filter(content_type=test_board_content_type)
        test_permissions_group.permissions.add(*test_board_admin_permissions)

        # Archive the board
        self.test_object.is_archived = True
        self.test_object.allowed_groups.add(test_permissions_group)
        self.test_object.save()

        user = self.create_test_user()
        user.groups.add(test_permissions_group)
        self.client = Client()

        login = self.client.login(username=self.username, password=self.password)
        self.assertTrue(login)

        response = self.client.get(reverse('board_detail', args=(self.test_object.pk,)))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'board_detail_archive.html')

    def test_board_archived_backlog(self):
        test_permissions_group, _ = Group.objects.get_or_create(name='Board Test Admin')
        test_board_content_type = ContentType.objects.get_for_model(TodoList)

        # Add all permissions
        test_board_admin_permissions = Permission.objects.filter(content_type=test_board_content_type)
        test_permissions_group.permissions.add(*test_board_admin_permissions)

        self.test_object.is_archived = True
        self.test_object.allowed_groups.add(test_permissions_group)
        self.test_object.save()

        user = self.create_test_user()
        user.groups.add(test_permissions_group)
        self.client = Client()

        login = self.client.login(username=self.username, password=self.password)
        self.assertTrue(login)

        response = self.client.get(reverse('board_backlog', args=(self.test_object.pk,)))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'board_backlog.html')

    def test_board_archived_backlog_user_not_logged_in(self):
        test_permissions_group, _ = Group.objects.get_or_create(name='Board Test Admin')
        test_board_content_type = ContentType.objects.get_for_model(TodoList)

        # Add all permissions
        test_board_admin_permissions = Permission.objects.filter(content_type=test_board_content_type)
        test_permissions_group.permissions.add(*test_board_admin_permissions)

        self.test_object.is_archived = True
        self.test_object.allowed_groups.add(test_permissions_group)
        self.test_object.save()

        user = self.create_test_user()
        user.groups.add(test_permissions_group)
        self.client = Client()

        response = self.client.get(reverse('board_backlog', args=(self.test_object.pk,)))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'forbidden.html')

    def test_boards_list_view_user_logged_in(self):
        user = self.create_test_user()
        self.client = Client()

        login = self.client.login(username=self.username, password=self.password)
        self.assertTrue(login)

        response = self.client.get(reverse('boards_list'))
        self.assertTemplateUsed(response, 'boards.html')
        self.assertEqual(response.status_code, 200)

    def test_board_create_new_group_created(self):
        user = self.create_test_user()
        self.client = Client()

        login = self.client.login(username=self.username, password=self.password)
        self.assertTrue(login)

        form_url = reverse('board_create')
        form_data = {
            'title': 'DummyBoard'
        }

        # Simulate form submission
        response = self.client.post(form_url, form_data)

        board_title = self.test_object.title
        # Verify board was created and new group was created as well
        created_board = TodoList.objects.filter(title='DummyBoard')
        self.assertTrue(created_board.exists(), 'Board was not created.')
        self.assertTrue(created_board.get().allowed_groups.filter(name='DummyBoard admins').exists(),
                        'Group was not added to board')
        self.assertTrue(Group.objects.filter(name='DummyBoard admins').exists(), 'Group was not created')
        self.assertTrue(user.groups.filter(name='DummyBoard admins').exists(), "User was not added to the group.")

        self.assertRedirects(response, f'/boards/{created_board.get().pk}')

        user.delete()

    def test_all_boards_view_user_is_admin(self):
        """
        Test that all boards can be displayed for superuser
        """

        user = self.create_test_superuser()
        self.client = Client()

        login = self.client.login(username=self.username, password=self.password)
        self.assertTrue(login)

        response = self.client.get(reverse('all_boards_list'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'boards.html')
        self.assertEqual(len(response.context['boards']), 1)
        self.assertTrue(user.is_superuser)

    def test_all_boards_view_user_is_not_admin(self):
        """
        Test that all boards can be displayed for superuser
        """

        user = self.create_test_user()
        self.client = Client()

        login = self.client.login(username=self.username, password=self.password)
        self.assertTrue(login)

        response = self.client.get(reverse('all_boards_list'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'forbidden.html')
        self.assertFalse(user.is_superuser)

    def test_archived_boards_list_view_user_is_not_admin(self):
        """
        Test that all boards can be displayed for superuser
        """

        # Archive the board
        self.test_object.is_archived = True
        self.test_object.save()

        user = self.create_test_user()
        self.client = Client()

        login = self.client.login(username=self.username, password=self.password)
        self.assertTrue(login)

        response = self.client.get(reverse('archived_boards'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'archived_boards.html')

        # Assert that context boards has no elements if user is not superuser
        self.assertEqual(len(response.context['boards']), 0)

    def test_archived_boards_list_view_user_is_admin(self):
        """
        Test that all boards can be displayed for superuser
        """

        # Archive the board
        self.test_object.is_archived = True
        self.test_object.save()

        user = self.create_test_superuser()
        self.assertTrue(user.is_superuser)
        self.client = Client()

        login = self.client.login(username=self.username, password=self.password)
        self.assertTrue(login)

        response = self.client.get(reverse('archived_boards'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'archived_boards.html')

        # Assert that context boards has elements if user is superuser
        self.assertEqual(len(response.context['boards']), 1)
