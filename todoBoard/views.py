from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.http import JsonResponse, HttpResponseForbidden
import json
from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.http import require_POST
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
    board = TodoList.objects.get(id=board_id)

    user_groups = request.user.groups.all()
    allowed_groups = board.allowed_groups.all()

    if not (user_groups and allowed_groups).exists() or not request.user.has_perm('todoBoard.can_view_board'):
        return render(request, template_name='forbidden.html')
    context = {
        'tasks': tasks,
        'board_id': board_id,
        'board': board,
    }
    if template_name == 'board_backlog.html':
        return render(request, template_name=template_name, context=context)
    return render(request, template_name='board_detail.html', context=context)


@login_required
def task_create(request, board_id):
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
@login_required
def task_change_status(request):
    if request.method == 'POST':
        task_id = request.POST.get("task_id")
        new_status = request.POST.get("new_status")
        task = get_object_or_404(TodoItem, id=task_id)
        task.status = new_status

        with transaction.atomic():
            task.save()

        return JsonResponse({'success': True})
    return JsonResponse({'success': False, 'error': 'Invalid request method'})


@login_required
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


@csrf_protect
@require_POST
@login_required
def board_update(request, board_id):
    if request.method == 'POST':
        board = TodoList.objects.get(id=board_id)
        if board:
            body_unicode = request.body.decode("utf-8")
            json_data = json.loads(body_unicode)
            board_title = json_data.get('boardTitle')
            board_description = json_data.get('boardDescription')

            board.title = board_title
            board.description = board_description

            with transaction.atomic():
                board.save()

            return JsonResponse({'success': True})
        return JsonResponse({'success': False, 'error': 'Board was not found'})

    return JsonResponse({'success': False, 'error': 'Invalid request method'})


@csrf_protect
@require_POST
@login_required
def board_delete(request, board_id):
    board = get_object_or_404(TodoList, id=board_id)
    board.delete()
    return JsonResponse({'success': True})


def task_detail(request, task_id):
    task = TodoItem.objects.get(id=task_id)
    context = {'task': task}

    return render(request, template_name='task_detail.html', context=context)


@csrf_protect
@require_POST
@login_required
def task_update(request, task_id):
    try:
        body_unicode = request.body.decode("utf-8")
        json_data = json.loads(body_unicode)
        task = TodoItem.objects.get(id=task_id)
        task_name = json_data.get('taskName')
        # TODO: taskAsignee
        task_status = json_data.get('taskStatus')
        #task_deadline = json_data.get('taskDeadline')
        task_description = json_data.get('taskDescription')
        #TODO: add check whether the data has changed <- shouldn't this be done on frontend?
        task.name = task_name
        task.status = task_status
        #task.due_to = task_deadline # TODO: fix to proper format
        task.description = task_description

        with transaction.atomic():
            task.save()

        return JsonResponse({'success': True})
    except TodoItem.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Task not found'})
    except json.JSONDecodeError:
        return JsonResponse({'success': False, 'error': 'Invalid JSON format'})


@csrf_protect
@require_POST
@login_required
def task_delete(request, task_id):
    try:
        task = TodoItem.objects.get(id=task_id)
        board_id = task.category.id
        task.delete()

        return JsonResponse({'success': True, 'board_id': board_id})
    except TodoItem.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Task not found'})
