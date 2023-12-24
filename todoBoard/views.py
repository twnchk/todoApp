from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.csrf import csrf_protect
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


@login_required
def task_create(request, board_id):
    '''
    Create new task for specific board. board_id is specified by backlog from which this view
    was requested.
    '''
    # Initial data for board_id, TODO: add validation to board_id, dont display form if board doesnt exist

    if request.method == 'POST':
        form = CreateTaskForm(request.POST, init_board_id=board_id, user_id=request.user.id)
        if form.is_valid():
            new_task = form.save(commit=False)
            new_task.save()
            return redirect('board_detail', board_id=board_id)
    else:
        form = CreateTaskForm(init_board_id=board_id, user_id=request.user.id)

    return render(request, template_name='create_task.html', context={'form': form})


@csrf_protect
def task_change_status(request):
    if request.method == 'POST':
        task_id = request.POST.get("task_id")
        new_status = request.POST.get("new_status")
        print(f'taskId = {task_id}')
        task = get_object_or_404(TodoItem, id=task_id)
        task.status = new_status

        with transaction.atomic():
            task.save()

        return JsonResponse({'success': True})
    return JsonResponse({'success': False, 'error': 'Invalid request method'})


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


