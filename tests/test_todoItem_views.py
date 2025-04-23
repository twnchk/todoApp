from json import dumps as json_dumps

from django.test import TestCase, Client
from django.contrib.auth.models import Group, Permission
from django.urls import reverse
from django.contrib.contenttypes.models import ContentType
from todoBoard.models import TodoList, TodoItem
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

        self.board = TodoList.objects.create(title='test_board', description='test_description')

        self.test_object = TodoItem.objects.create(name='test_task',
                                                   description='task_description',
                                                   author=self.user,
                                                   board=self.board)

    def create_test_superuser(self):
        return CustomUser.objects.create_superuser(username=self.admin_username,
                                                   email='test@example.com',
                                                   password=self.password)

    def login_user(self, is_superuser=False):
        login = self.client.login(username=self.admin_username if is_superuser else self.username,
                                  password=self.password)
        self.assertTrue(login)

    def test_task_create_view_user_not_logged_in(self):
        response = self.client.post(reverse('task_create', args=(self.board.id,)))
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, f'/login/?next=/boards/{self.board.pk}/addTask/')

    def test_task_create_view_user(self):
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

    def test_task_change_status_view(self):
        self.create_test_superuser()
        self.login_user(is_superuser=True)

        form_url = reverse('task_change_status')
        form_data = {
            'task_id': self.test_object.pk,
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

        response = self.client.get(reverse('task_change_status'))

        self.assertEqual(response.status_code, 405)
        self.assertEqual(response.json()['error'], 'GET method is not allowed for this action')
