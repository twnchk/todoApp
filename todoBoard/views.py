from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from django.db import transaction
from django.http import JsonResponse
import json
from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.http import require_POST
from django.views.generic import TemplateView
from .models import TodoList, TodoItem
from users.models import CustomUser
from .forms import CreateTaskForm, CreateBoardForm
from .decorators import task_editor_required, board_editor_required, board_admin_required


class IndexView(TemplateView):
    template_name = 'index.html'


# Board views
@login_required()
def all_boards_list(request):
    if not request.user.is_superuser:
        return render(request, template_name='forbidden.html')
    boards = TodoList.objects.all()

    for board in boards:
        board.show_delete_button = True

    return render(request, template_name='boards.html', context={'boards': boards})


@login_required()
def boards_list(request):
    user = request.user
    boards = set()
    for group in user.groups.all():
        boards.update(group.allowed_boards.all())

    user_has_delete_perm = ((user.is_authenticated and user.has_perm('todoBoard.can_delete_board'))
                            or user.is_superuser)

    for board in boards:
        if user.is_superuser:
            board.show_delete_button = True
        elif user_has_delete_perm:
            user_group_ids = set(user.groups.values_list('id', flat=True))
            allowed_group_ids = set(board.allowed_groups.values_list('id', flat=True))
            board.show_delete_button = bool(set(user_group_ids) & set(allowed_group_ids))
        else:
            board.show_delete_button = False

    context = {'boards': boards}
    return render(request, template_name='boards.html', context=context)


@board_editor_required(TodoList)
def board_detail(request, board_id, template_name='board_detail.html'):
    tasks = TodoItem.objects.filter(board=board_id)
    board = TodoList.objects.get(id=board_id)
    context = {
        'tasks': tasks,
        'board_id': board_id,
        'board': board,
    }
    if template_name == 'board_backlog.html':
        return render(request, template_name=template_name, context=context)
    return render(request, template_name='board_detail.html', context=context)


@login_required
def board_create(request):
    if request.method == 'POST':
        form = CreateBoardForm(request.POST)
        if form.is_valid():
            new_board_group_name = form.cleaned_data['title'] + ' admins'
            new_group, created = Group.objects.get_or_create(name=new_board_group_name)

            if created:
                board_content_type = ContentType.objects.get_for_model(TodoList)
                task_content_type = ContentType.objects.get_for_model(TodoItem)
                board_permissions = Permission.objects.filter(content_type=board_content_type)
                task_permissions = Permission.objects.filter(content_type=task_content_type)

                new_group.permissions.add(*board_permissions)
                new_group.permissions.add(*task_permissions)
                request.user.groups.add(new_group)

                new_board = form.save()
                new_board.allowed_groups.add(new_group)

                return redirect('board_detail', board_id=new_board.pk)
            else:
                form.add_error(None, 'A group with this name already exists.')
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
@board_admin_required(TodoList)
def board_delete(request, board_id):
    board = get_object_or_404(TodoList, id=board_id)
    board.delete()
    return JsonResponse({'success': True})


# Task views
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
@task_editor_required
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


def task_detail(request, task_id):
    task = get_object_or_404(TodoItem, id=task_id)
    allowed_group_ids = task.board.allowed_groups.values_list('id', flat=True)
    assignees = CustomUser.objects.filter(groups__id__in=allowed_group_ids).distinct()
    context = {
        'task': task,
        'assignees': assignees,
    }

    return render(request, template_name='task_detail.html', context=context)


@csrf_protect
@require_POST
@login_required
@task_editor_required
def task_update(request, task_id):
    try:
        body_unicode = request.body.decode("utf-8")
        json_data = json.loads(body_unicode)
        task = get_object_or_404(TodoItem, id=task_id)
        task_name = json_data.get('taskName')
        task_assignee_id = int(json_data.get('taskAssignee'))
        task_status = json_data.get('taskStatus')
        task_description = json_data.get('taskDescription')
        # TODO: add check whether the data has changed <- shouldn't this be done on frontend?
        task.name = task_name
        task.status = task_status
        task.description = task_description
        new_assignee = get_object_or_404(CustomUser, id=task_assignee_id)
        task.assignee = new_assignee

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
@task_editor_required
def task_delete(request, task_id):
    try:
        task = TodoItem.objects.get(id=task_id)
        board_id = task.board.id
        task.delete()

        return JsonResponse({'success': True, 'board_id': board_id})
    except TodoItem.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Task not found'})
