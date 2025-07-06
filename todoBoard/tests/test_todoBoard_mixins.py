from django.test import TestCase
from todoBoard.mixins import get_board_from_kwargs
from todoBoard.models import TodoList

class TodoBoardMixinsTest(TestCase):
    def test_get_board_from_kwargs_board_id_missing(self):
        with self.assertRaises(ValueError) as context:
            get_board_from_kwargs(TodoList)

        self.assertEqual(str(context.exception), 'Board id (pk) not found in URL.')

