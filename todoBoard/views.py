from django.shortcuts import render, redirect
from django.views.generic import TemplateView
from .models import TodoList, TodoItem
from .forms import CreateTaskForm, CreateBoardForm


class IndexView(TemplateView):
    template_name = 'index.html'


def boards_list(request):
    boards = TodoList.objects.all()
    context = {'boards': boards}
    return render(request, template_name='boards.html', context=context)


def board_detail(request, board_id, template_name='board_detail.html'):
    tasks = TodoItem.objects.filter(category=board_id)
    context = {
        'tasks': tasks,
        'board_id': board_id,
    }
    if template_name == 'board_backlog.html':
        return render(request, template_name=template_name, context=context)
    return render(request, template_name='board_detail.html', context=context)
    # if template_name == 'board_backlog.html'


def task_create(request, board_id):
    '''
    Create new task for specific board. board_id is specified by backlog from which this view
    was requested.
    '''
    # Initial data for board_id, TODO: add validation to board_id, dont display form if board doesnt exist

    if request.method == 'POST':
        form = CreateTaskForm(request.POST, init_board_id=board_id)
        if form.is_valid():
            new_task = form.save(commit=False)
            new_task.save()
            return redirect('board_detail', board_id=board_id)
    else:
        form = CreateTaskForm(init_board_id=board_id)

    return render(request, template_name='create_task.html', context={'form': form})


def board_create(request):
    # TODO: Add permission to only create boards by logged in by certain users with specific permissions
    if request.method == 'POST':
        form = CreateBoardForm(request.POST)
        if form.is_valid():
            new_board = form.save()
            return redirect('board_detail', board_id=new_board.pk)
    else:
        form = CreateBoardForm()

    return render(request, template_name='create_board.html', context={'form': form})


