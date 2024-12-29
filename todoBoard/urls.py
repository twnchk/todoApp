from django.urls import path

# Board views
from .views import IndexView, AllBoardsListView, UserBoardsListView, ArchivedBoardsList, BoardDetailView, \
    BoardBacklogView, BoardCreateView, BoardUpdateView, BoardDeleteView, BoardCloseView, BoardRepoenView

# Task views
from .views import task_change_status, task_create, task_detail, task_update, task_delete

urlpatterns = [
    path('', IndexView.as_view(), name='index'),
    # Boards
    path('boards/', UserBoardsListView.as_view(), name='boards_list'),
    path('boards/archive/', ArchivedBoardsList.as_view(), name='archived_boards'),
    path('allBoards/', AllBoardsListView.as_view(), name='all_boards_list'),
    path('addBoard/', BoardCreateView.as_view(), name='board_create'),
    path('boards/<int:pk>', BoardDetailView.as_view(), name='board_detail'),
    path('boards/<int:pk>/backlog/', BoardBacklogView.as_view(), name='board_backlog'),
    path('boards/<int:pk>/update', BoardUpdateView.as_view(), name='board_update'),
    path('boards/<int:pk>/delete', BoardDeleteView.as_view(), name='board_delete'),
    path('boards/<int:pk>/close', BoardCloseView.as_view(), name='board_close'),
    path('boards/<int:pk>/open', BoardRepoenView.as_view(), name='board_reopen'),
    # Tasks
    path('boards/<int:pk>/addTask/', task_create, name='task_create'),
    path('changeTaskStatus/', task_change_status, name='task_change_status'),
    path('task/<int:task_id>', task_detail, name='task_detail'),
    path('taskUpdate/<int:task_id>', task_update, name='task_update'),
    path('taskDelete/<int:task_id>', task_delete, name='task_delete'),
]
