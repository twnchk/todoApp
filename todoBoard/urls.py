from django.urls import path
from .views import IndexView, archived_boards_list, board_close, board_reopen, \
    board_delete, \
    task_change_status, task_create, task_detail, task_update, task_delete

from .views import AllBoardsListView, UserBoardsListView, BoardDetailView, BoardBacklogView, BoardCreateView, \
    BoardUpdateView

urlpatterns = [
    path('', IndexView.as_view(), name='index'),
    path('boards/', UserBoardsListView.as_view(), name='boards_list'),
    path('boards/archive/', archived_boards_list, name='archived_boards'),
    path('allBoards/', AllBoardsListView.as_view(), name='all_boards_list'),
    path('addBoard/', BoardCreateView.as_view(), name='board_create'),
    path('boards/<int:pk>', BoardDetailView.as_view(), name='board_detail'),
    path('boards/<int:pk>/backlog/', BoardBacklogView.as_view(), name='board_backlog'),
    path('boards/<int:pk>/addTask/', task_create, name='task_create'),
    path('boards/<int:pk>/update', BoardUpdateView.as_view(), name='board_update'),
    path('boards/<int:pk>/delete', board_delete, name='board_delete'),
    path('boards/<int:pk>/close', board_close, name='board_close'),
    path('boards/<int:pk>/open', board_reopen, name='board_reopen'),
    path('changeTaskStatus/', task_change_status, name='task_change_status'),
    path('task/<int:task_id>', task_detail, name='task_detail'),
    path('taskUpdate/<int:task_id>', task_update, name='task_update'),
    path('taskDelete/<int:task_id>', task_delete, name='task_delete'),
]
