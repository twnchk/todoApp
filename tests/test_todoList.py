from django.test import TestCase
from django.db import IntegrityError
from todoBoard.models import TodoList


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
