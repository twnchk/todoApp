from django.test import TestCase
from todoBoard.forms import CreateTaskForm

class TodoBoardFormsTest(TestCase):
    def test_create_task_form_missing_init_board_id(self):
        with self.assertRaises(ValueError) as context:
            CreateTaskForm(init_board_id=None, user_id=1)  # pass dummy user value

        self.assertEqual(str(context.exception), "Missing required argument 'init_board_id' or 'user_id'")

    def test_create_task_form_missing_user_id(self):
        with self.assertRaises(ValueError) as context:
            CreateTaskForm(init_board_id=1, user_id=None)  # pass dummy board value

        self.assertEqual(str(context.exception), "Missing required argument 'init_board_id' or 'user_id'")