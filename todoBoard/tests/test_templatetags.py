from django.test import TestCase
from templatetags.custom_filters import filter_status

from todoBoard.models import TodoItem, TodoList
from users.models import CustomUser

class FilterStatusTemplateTagTest(TestCase):
    def setUp(self):
        self.user = CustomUser.objects.create_user(username='testUser321',
                                                   email='test@example.com',
                                                   password='testing123456')
        self.board = TodoList.objects.create(title='dummy board', owner=self.user)
        self.tasks = TodoItem.objects.bulk_create(
            [
                TodoItem(name='Foo', author=self.user, board=self.board),
                TodoItem(name='Boo', author=self.user, board=self.board, status='DN'),
                TodoItem(name='Woo', author=self.user, board=self.board, status='PR')
            ]
        )

    def test_filter_tasks_by_status(self):
        all_tasks = TodoItem.objects.all()
        not_started_tasks = filter_status(all_tasks, 'NS')
        self.assertEqual(not_started_tasks.count(), 1)

        in_progress_tasks = filter_status(all_tasks, 'PR')
        self.assertEqual(in_progress_tasks.count(), 1)

        done_tasks = filter_status(all_tasks, 'DN')
        self.assertEqual(done_tasks.count(), 1)


