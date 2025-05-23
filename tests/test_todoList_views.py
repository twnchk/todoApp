from json import dumps as json_dumps

from django.test import TestCase, Client
from django.contrib.auth.models import Group, Permission
from django.urls import reverse
from django.contrib.contenttypes.models import ContentType
from todoBoard.models import TodoList, TodoItem
from users.models import CustomUser

from django.contrib.messages import get_messages


class TodoListViewTest(TestCase):
    def setUp(self):
        self.test_object = TodoList.objects.create(title='test_board', description='test_description')
        self.username = 'testUser321'
        self.admin_username = 'testSuperUser321'
        self.password = 'testing123456'
        self.user = CustomUser.objects.create_user(username=self.username,
                                                   email='test@example.com',
                                                   password=self.password)
        self.client = Client()

    def create_test_superuser(self):
        self.user = CustomUser.objects.create_superuser(username=self.admin_username,
                                                        email='test@example.com',
                                                        password=self.password)

    def login_user(self, is_superuser=False):
        login = self.client.login(username=self.admin_username if is_superuser else self.username,
                                  password=self.password)
        self.assertTrue(login)

    def add_user_permissions(self):
        test_permissions_group, _ = Group.objects.get_or_create(name='Board Test Admin')
        test_board_content_type = ContentType.objects.get_for_model(TodoList)

        # Add all permissions
        test_board_admin_permissions = Permission.objects.filter(content_type=test_board_content_type)
        test_permissions_group.permissions.add(*test_board_admin_permissions)

        self.test_object.allowed_groups.add(test_permissions_group)
        self.user.groups.add(test_permissions_group)

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
        self.login_user()
        self.add_user_permissions()

        response = self.client.get(reverse('board_detail', args=(self.test_object.id,)))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'board_detail.html')

    def test_board_detail_user_without_permissions(self):
        """
        Test that board can NOT be displayed if user does NOT belong to group
        with required permissions
        """

        # Do not add user to any group

        self.login_user()

        response = self.client.get(reverse('board_detail', args=(self.test_object.id,)))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'forbidden.html')

    def test_board_detail_backlog(self):
        self.login_user()
        self.add_user_permissions()

        response = self.client.get(reverse('board_backlog', args=(self.test_object.id,)))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'board_backlog.html')

    def test_board_detail_archived(self):
        # Archive the board
        self.test_object.is_archived = True
        self.test_object.save()

        self.login_user()
        self.add_user_permissions()

        response = self.client.get(reverse('board_detail', args=(self.test_object.pk,)))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'board_detail_archive.html')

    def test_board_archived_backlog(self):
        self.add_user_permissions()

        self.test_object.is_archived = True
        self.test_object.save()

        self.login_user()

        response = self.client.get(reverse('board_backlog', args=(self.test_object.pk,)))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'board_backlog.html')

    def test_board_archived_backlog_user_not_logged_in(self):
        self.test_object.is_archived = True
        self.test_object.save()

        self.add_user_permissions()

        response = self.client.get(reverse('board_backlog', args=(self.test_object.pk,)))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'forbidden.html')

    def test_boards_list_view_user_logged_in(self):
        self.login_user()
        self.add_user_permissions()

        response = self.client.get(reverse('boards_list'))
        self.assertTemplateUsed(response, 'boards.html')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['boards']), 1)

    def test_all_boards_view_user_is_admin(self):
        """
        Test that all boards can be displayed for superuser
        """

        self.create_test_superuser()

        self.login_user(is_superuser=True)

        response = self.client.get(reverse('all_boards_list'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'boards.html')
        self.assertEqual(len(response.context['boards']), 1)
        self.assertTrue(self.user.is_superuser)

    def test_all_boards_view_user_is_not_admin(self):
        """
        Test that all boards can be displayed for superuser
        """

        self.login_user()

        response = self.client.get(reverse('all_boards_list'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'forbidden.html')
        self.assertFalse(self.user.is_superuser)

    def test_archived_boards_list_view_user_is_not_admin(self):
        """
        Test that all boards can be displayed for superuser
        """

        # Archive the board
        self.test_object.is_archived = True
        self.test_object.save()

        self.login_user()

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

        self.create_test_superuser()
        self.assertTrue(self.user.is_superuser)

        self.login_user(is_superuser=True)

        response = self.client.get(reverse('archived_boards'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'archived_boards.html')

        # Assert that context boards has elements if user is superuser
        self.assertEqual(len(response.context['boards']), 1)

    def test_create_view_get_method(self):
        self.login_user()

        response = self.client.get(reverse('board_create'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'create_board.html')
        self.assertIn('form', response.context)

    def test_board_create_new_group_created(self):
        self.login_user()

        form_url = reverse('board_create')
        form_data = {
            'title': 'DummyBoard'
        }

        # Simulate form submission
        response = self.client.post(form_url, form_data)
        created_board = TodoList.objects.filter(title='DummyBoard')
        self.assertRedirects(response, f'/boards/{created_board.get().pk}')
        self.assertEqual(response.status_code, 302)
        self.assertTrue(created_board.exists(), 'Board was not created.')
        self.assertTrue(created_board.get().allowed_groups.filter(name='DummyBoard admins').exists(),
                        'Group was not added to board')
        self.assertTrue(Group.objects.filter(name='DummyBoard admins').exists(), 'Group was not created')
        self.assertTrue(self.user.groups.filter(name='DummyBoard admins').exists(), "User was not added to the group.")

    def test_create_view_create_board_when_same_group_exists(self):
        Group.objects.create(name='test_board admins')

        self.login_user()

        form_url = reverse('board_create')
        form_data = {
            'title': 'test_board'
        }

        # Simulate form submission
        response = self.client.post(form_url, form_data)

        self.assertEqual(response.status_code, 200)
        self.assertFormError(response.context['form'], None, 'A group with this name already exists.')

    def test_board_update_view_get_method(self):
        self.login_user()

        response = self.client.get(reverse('board_update', kwargs={'pk': f'{self.test_object.pk}'}))
        self.assertEqual(response.status_code, 405)
        self.assertEqual(response.json()['error'], 'GET method is not allowed for this action')

    def test_board_update_view(self):
        self.login_user()

        form_url = reverse('board_update', kwargs={'pk': f'{self.test_object.pk}'})
        form_data = {
            'boardTitle': 'updated_title',
            'boardDescription': 'lorem ipsum',
        }

        response = self.client.post(path=form_url, data=json_dumps(form_data), content_type='application/json',
                                    HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['success'], True)
        self.assertEqual(response.json()['message'], 'Board updated successfully.')

        # Refresh the object from DB
        self.test_object.refresh_from_db()
        self.assertEqual(self.test_object.title, 'updated_title')
        self.assertEqual(self.test_object.description, 'lorem ipsum')

    def test_board_update_view_invalid_request(self):
        self.login_user()

        form_url = reverse('board_update', kwargs={'pk': f'{self.test_object.pk}'})
        form_data = {
            'boardTitle': 'updated_title',
            'boardDescription': 'lorem ipsum',
        }

        response = self.client.post(path=form_url, data=json_dumps(form_data), content_type='application/json',
                                    HTTP_X_REQUESTED_WITH='invalid_request')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['success'], False)
        self.assertEqual(response.json()['error'], 'Invalid request.')

        # Refresh the object from DB
        self.test_object.refresh_from_db()
        self.assertNotEqual(self.test_object.title, 'updated_title')
        self.assertNotEqual(self.test_object.description, 'lorem ipsum')

    def test_board_delete_view_get_method(self):
        self.create_test_superuser()
        self.login_user(is_superuser=True)

        response = self.client.get(reverse('board_delete', kwargs={'pk': f'{self.test_object.pk}'}))
        self.assertEqual(response.status_code, 302)

    def test_board_delete_view_user_not_board_admin(self):
        self.login_user()

        response = self.client.post(reverse('board_delete', kwargs={'pk': f'{self.test_object.pk}'}))
        self.assertEqual(response.status_code, 302)
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(str(messages[0]),
                         'Not enough privileges. Please contact board administrator.')

    def test_board_close_view_get_method(self):
        self.create_test_superuser()
        self.assertTrue(self.user.is_superuser)

        self.login_user(is_superuser=True)

        response = self.client.get(reverse('board_close', kwargs={'pk': f'{self.test_object.pk}'}))
        self.assertEqual(response.status_code, 405)
        self.assertEqual(response.json()['error'], 'GET method is not allowed for this action')

    def test_board_close_view_user_is_superuser(self):
        self.create_test_superuser()
        self.login_user(is_superuser=True)

        # Create dummy task for coverage reasons
        task = TodoItem.objects.create(name='Foo', description='', author=self.user, board=self.test_object)
        self.assertEqual(task.status, 'NS')

        view_url = reverse('board_close', kwargs={'pk': f'{self.test_object.pk}'})
        response = self.client.post(view_url)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['success'], True)
        self.assertEqual(response.json()['message'], 'Board closed successfully.')

        # Refresh the object from DB
        task.refresh_from_db()
        # Verify task status was changed to done upon closing the board
        self.assertEqual(task.status, 'DN')

    def test_board_close_view_user_not_editor(self):
        self.login_user()

        view_url = reverse('board_close', kwargs={'pk': f'{self.test_object.pk}'})
        response = self.client.post(view_url)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed('forbidden.html')
        # self.assertEqual(response.json()['success'], True)
        # self.assertEqual(response.json()['message'], 'Board closed successfully.')


    def test_board_reopen_view_user_is_superuser(self):
        self.create_test_superuser()
        self.login_user(is_superuser=True)

        view_url = reverse('board_reopen', kwargs={'pk': f'{self.test_object.pk}'})
        response = self.client.post(view_url)

        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, f'/boards/{self.test_object.pk}')
