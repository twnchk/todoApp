from json import dumps as json_dumps

from django.test import TestCase, Client, RequestFactory
from django.urls import reverse
from django.contrib.messages import get_messages

from todoBoard.models import TodoList, TodoItem
from todoBoard.views import TaskCreateView

from users.models import CustomUser


class TodoItemViewTest(TestCase):
    def setUp(self):
        self.username = 'testUser321'
        self.admin_username = 'testSuperUser321'
        self.password = 'testing123456'
        self.user = CustomUser.objects.create_user(username=self.username,
                                                   email='test@example.com',
                                                   password=self.password)
        self.client = Client()

        self.board = TodoList.objects.create(title='test_board', description='test_description', owner=self.user)

        self.test_object = TodoItem.objects.create(name='test_task',
                                                   description='task_description',
                                                   author=self.user,
                                                   board=self.board)

    def create_test_superuser(self):
        self.user = CustomUser.objects.create_superuser(username=self.admin_username,
                                                        email='test@example.com',
                                                        password=self.password)

    def create_not_allowed_user(self):
        username = 'unauthorizedUser'
        email = 'unauthorizedUser@example.com'
        self.user = CustomUser.objects.create_user(username=username,
                                                   email=email,
                                                   password=self.password)

        login = self.client.login(username=username, password=self.password)
        self.assertTrue(login)

    def login_user(self, is_superuser=False):
        login = self.client.login(username=self.admin_username if is_superuser else self.username,
                                  password=self.password)
        self.assertTrue(login)

    def test_task_create_view_user_not_logged_in(self):
        response = self.client.post(reverse('task_create', args=(self.board.id,)))
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, f'/login/?next=/boards/{self.board.pk}/addTask/')

    def test_task_create_view(self):
        self.login_user()

        form_url = reverse('task_create', args=(self.board.id,))
        form_data = {
            'name': 'foo',
            'description': 'boo',
            'author': self.user.id,
            'board': self.board.id,
            'status': "NS"
        }
        response = self.client.post(form_url, form_data)

        created_task = TodoItem.objects.filter(name='foo')
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, f'/boards/{self.board.id}')
        self.assertTrue(created_task.exists(), 'Error! Task was not created')

    def test_task_create_view_board_id_not_present(self):
        """
        Raises value error due to omitted board_id in url
        """
        self.login_user()
        request = RequestFactory().get('/task_create/')
        request.user = self.user  # Mock logged in user

        view = TaskCreateView()
        view.request = request
        view.kwargs = {}  # Do NOT pass board_id to the url

        with self.assertRaises(ValueError) as context:
            view.get_success_url()

        self.assertEqual(str(context.exception), 'ID not provided in the URL')

    def test_task_change_status_view(self):
        self.create_test_superuser()
        self.login_user(is_superuser=True)

        form_url = reverse('task_change_status', kwargs={'pk': self.test_object.pk})
        form_data = {
            'new_status': 'DN'
        }
        response = self.client.post(form_url, form_data)

        # Refresh the object from DB
        self.test_object.refresh_from_db()

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['success'], True)
        self.assertEqual(self.test_object.status, 'DN')

    def test_task_change_status_view_get_method(self):
        self.create_test_superuser()
        self.login_user(is_superuser=True)

        response = self.client.get(reverse('task_change_status', kwargs={'pk': self.test_object.pk}))

        self.assertEqual(response.status_code, 405)
        self.assertEqual(response.json()['error'], 'GET method is not allowed for this action')

    def test_task_detail_view_user_not_allowed(self):
        self.create_not_allowed_user()

        # follow the response to verify a message is raised
        response = self.client.get(reverse('task_detail', args=(self.test_object.pk,)), follow=True)

        self.assertRedirects(response, reverse('boards_list'))

        # get message list from response request
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(str(messages[0]), 'That task does not exist or you are not allowed to see it.')

    def test_task_detail_view_user_allowed(self):
        self.login_user()

        response = self.client.get(reverse('task_detail', args=(self.test_object.pk,)))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['assignees']), 1)
        self.assertTemplateUsed(response, 'task_detail.html')

    def test_task_detail_view_user_is_superuser(self):
        self.create_test_superuser()
        self.login_user(is_superuser=True)

        response = self.client.get(reverse('task_detail', args=(self.test_object.pk,)))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'task_detail.html')

    def test_task_delete_view_user_not_allowed(self):
        self.create_not_allowed_user()

        # follow the response to verify a message is raised
        response = self.client.post(reverse('task_delete', args=(self.test_object.pk,)), follow=True)

        self.assertEqual(response.status_code, 200)

        # get message list from response request
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(str(messages[0]),
                         "You don't have permissions to edit tasks. Please contact board administrator.")

    def test_task_delete_view_get_method(self):
        self.login_user()

        response = self.client.get(reverse('task_delete', args=(self.test_object.pk,)))
        self.assertEqual(response.status_code, 405)
        self.assertEqual(response.json()['error'], 'GET method is not allowed for this action')

    def test_task_delete_view(self):
        self.login_user()

        response = self.client.post(reverse('task_delete', args=(self.test_object.pk,)), follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.json()['success'], True)
        self.assertEqual(response.json()['message'], f'Task {self.test_object.name} has been deleted')
        self.assertEqual(response.json()['board_id'], self.test_object.board.pk)

        # get message list from response request
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(str(messages[0]),
                         f'Task {self.test_object.name} has been deleted')

    def test_task_update_view_user_not_allowed(self):
        self.create_not_allowed_user()

        response = self.client.post(reverse('task_update', args=(self.test_object.pk,)), follow=True)

        self.assertEqual(response.status_code, 200)

        # get message list from response request
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(str(messages[0]),
                         "You don't have permissions to edit tasks. Please contact board administrator.")

    def test_task_update_view_get_method(self):
        self.login_user()

        response = self.client.get(reverse('task_update', args=(self.test_object.pk,)))
        self.assertEqual(response.status_code, 405)
        self.assertEqual(response.json()['error'], 'GET method is not allowed for this action')

    def test_task_update_view(self):
        self.login_user()

        self.assertEqual(self.test_object.name, 'test_task')
        self.assertEqual(self.test_object.description, 'task_description')
        self.assertEqual(self.test_object.assignee, None)
        self.assertEqual(self.test_object.status, 'NS')

        form_url = reverse('task_update', kwargs={'pk': f'{self.test_object.pk}'})

        new_task_name = 'updated task name'
        new_task_description = 'updated task description'
        form_data = {
            'taskName': new_task_name,
            'taskAssignee': f"{self.user.pk}",
            'taskStatus': 'DN',
            'taskDescription': new_task_description
        }

        response = self.client.post(path=form_url, data=json_dumps(form_data), content_type='application/json',
                                    HTTP_X_REQUESTED_WITH='XMLHttpRequest')

        self.test_object.refresh_from_db()

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['success'], True)
        self.assertEqual(response.json()['message'], 'Task updated successfully.')

        self.assertEqual(self.test_object.name, new_task_name)
        self.assertEqual(self.test_object.description, new_task_description)
        self.assertEqual(self.test_object.assignee, self.user)
        self.assertEqual(self.test_object.status, 'DN')

    def test_task_update_view_assign_user(self):
        """
        Test that user assignment works when other data is not sent
        """
        self.login_user()
        self.assertEqual(self.test_object.assignee, None)

        form_url = reverse('task_update', kwargs={'pk': f'{self.test_object.pk}'})

        form_data = {
            'taskName': self.test_object.name,
            'taskAssignee': f"{self.user.pk}",
            'taskStatus': self.test_object.status,
            'taskDescription': self.test_object.description
        }

        response = self.client.post(path=form_url, data=json_dumps(form_data), content_type='application/json',
                                    HTTP_X_REQUESTED_WITH='XMLHttpRequest')

        self.test_object.refresh_from_db()

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['success'], True)
        self.assertEqual(response.json()['message'], 'Task updated successfully.')

        self.assertEqual(self.test_object.assignee, self.user)
        self.assertEqual(self.test_object.name, 'test_task')
        self.assertEqual(self.test_object.description, 'task_description')
        self.assertEqual(self.test_object.status, 'NS')

    def test_task_update_view_unassigned_user(self):
        self.login_user()

        form_url = reverse('task_update', kwargs={'pk': f'{self.test_object.pk}'})
        form_data = {
            'taskName': 'updated task name',
            'taskAssignee': 'unassigned',
            'taskStatus': 'NS',
            'taskDescription': 'updated task description'
        }

        response = self.client.post(path=form_url, data=json_dumps(form_data), content_type='application/json',
                                    HTTP_X_REQUESTED_WITH='XMLHttpRequest')

        self.test_object.refresh_from_db()

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['success'], True)
        self.assertEqual(response.json()['message'], 'Task updated successfully.')
        self.assertEqual(self.test_object.assignee, None)

    def test_task_update_view_board_archived(self):
        self.login_user()
        self.test_object.board.is_archived = True
        # Need to save modified object since TaskUpdateView fetches the object from db
        self.test_object.board.save()

        form_url = reverse('task_update', kwargs={'pk': f'{self.test_object.pk}'})
        form_data = {
            'taskName': 'updated task name',
            'taskAssignee': 'unassigned',
            'taskStatus': 'NS',
            'taskDescription': 'updated task description'
        }

        response = self.client.post(path=form_url, data=json_dumps(form_data), content_type='application/json',
                                    HTTP_X_REQUESTED_WITH='XMLHttpRequest', follow=True)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['success'], False)
        self.assertEqual(response.json()['message'], 'Cannot update task.')
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(str(messages[0]),
                         'You cannot update tasks in archived boards.')

    def test_task_update_view_invalid_json_request(self):
        self.login_user()

        form_url = reverse('task_update', kwargs={'pk': f'{self.test_object.pk}'})
        form_data = '{invalid: json,,}'

        response = self.client.post(path=form_url, data=form_data, content_type='application/json',
                                    HTTP_X_REQUESTED_WITH='XMLHttpRequest')

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['success'], False)
        self.assertEqual(response.json()['error'], 'Invalid JSON format')
