from django.test import TestCase
from django.db import IntegrityError
from todoBoard.models import TodoItem

# TODO: finish tests

class TodoItemTest(TestCase):
    def test_createTodoItem(self):
        expected_name = "TestItem"
        expected_description = "Lorem ipsum"
        # expected_user = Users.objects.first()

        test_object = TodoItem.objects.create()
        pass