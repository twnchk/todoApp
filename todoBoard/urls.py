from django.urls import path
from .views import IndexView, boards_list, board_detail, board_create,\
    task_change_status, task_create, task_detail, task_update, task_delete

urlpatterns = [
    path('', IndexView.as_view(), name='index'),
    path('boards/', boards_list, name='boards_list'),
    path('addBoard/', board_create, name='board_create'),
    path('boards/<int:board_id>', board_detail, name='board_detail'),
    path('boards/<int:board_id>/backlog/', board_detail, {'template_name': 'board_backlog.html'}, name='board_backlog'),
    path('boards/<int:board_id>/addTask/', task_create, name='task_create'),
    path('changeTaskStatus/', task_change_status, name='task_change_status'),
    path('task/<int:task_id>', task_detail, name='task_detail'),
    path('taskUpdate/<int:task_id>', task_update, name='task_update'),
    path('taskDelete/<int:task_id>', task_delete, name='task_delete'),
]
